// yt_vision_pick_place — pick_place_node
//
// A single, self-contained pick-and-place motion node for the Manipulation Lab
// cell. It waits for a 3D target pose (published by perception_node.py in the
// robot base frame), then runs one straight-line-of-thought sequence:
//
//     open -> pregrasp -> grasp -> close -> attach -> lift -> place -> detach -> open -> home
//
// This is intentionally a flat, readable script, not a reusable skill library.
// Every cell-specific constant (planning group, links, frames, offsets, the
// place location, the top-down orientation) is a ROS parameter — tune the demo
// from the launch/params.yaml, never by editing this file.
//
// It reuses, and does not reimplement: the UR5 MoveIt2 configuration, the
// ros2_control controllers, the Robotiq gripper, and the Gazebo LinkAttacher
// services (/ATTACHLINK, /DETACHLINK) that stand in for a real grasp in sim.

#include <chrono>
#include <memory>
#include <string>
#include <thread>
#include <vector>

#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.h>
#include <moveit/planning_scene_interface/planning_scene_interface.h>
#include <moveit_msgs/msg/collision_object.hpp>
#include <shape_msgs/msg/solid_primitive.hpp>
#include <geometry_msgs/msg/pose.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <std_srvs/srv/trigger.hpp>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>

#include <linkattacher_msgs/srv/attach_link.hpp>
#include <linkattacher_msgs/srv/detach_link.hpp>

using namespace std::chrono_literals;

class PickPlace
{
public:
  explicit PickPlace(const rclcpp::Node::SharedPtr & node)
  : node_(node), logger_(node->get_logger())
  {
    // --- parameters (all cell-specific constants live here) ------------------
    arm_group_        = declare<std::string>("arm_group", "ur5_manipulator");
    gripper_group_    = declare<std::string>("gripper_group", "robotiq_gripper");
    ee_link_          = declare<std::string>("ee_link", "tool0");
    base_frame_       = declare<std::string>("base_frame", "base_link");
    target_topic_     = declare<std::string>("target_topic", "/yt_vision/target_pose");

    robot_model_name_ = declare<std::string>("robot_model_name", "cobot");
    robot_grasp_link_ = declare<std::string>("robot_grasp_link", "wrist_3_link");
    object_model_     = declare<std::string>("object_model", "yt_red_cube");
    object_link_      = declare<std::string>("object_link", "link");

    gripper_joint_    = declare<std::string>("gripper_joint", "robotiq_85_left_knuckle_joint");
    gripper_close_    = declare<double>("gripper_close", 0.4);
    gripper_open_     = declare<double>("gripper_open", 0.0);

    grasp_z_offset_   = declare<double>("grasp_z_offset", 0.13);    // tool0 height above the target point at grasp
    approach_z_offset_= declare<double>("approach_z_offset", 0.28); // pregrasp height above the target point
    lift_dz_          = declare<double>("lift_dz", 0.15);           // rise this far above the grasp before carrying

    // Place is RELATIVE to where the object was picked (base frame), so we never
    // need to know the table's absolute coordinates: carry it sideways and drop.
    place_dx_         = declare<double>("place_dx", 0.0);
    place_dy_         = declare<double>("place_dy", 0.25);

    // Top-down grasp orientation, as base-frame RPY. Default points tool0 down.
    grasp_roll_       = declare<double>("grasp_roll", 3.14159265);
    grasp_pitch_      = declare<double>("grasp_pitch", 0.0);
    grasp_yaw_        = declare<double>("grasp_yaw", 0.0);

    vel_scale_        = declare<double>("vel_scale", 0.2);
    acc_scale_        = declare<double>("acc_scale", 0.2);
    planning_time_    = declare<double>("planning_time", 10.0);
    planning_attempts_= declare<int>("planning_attempts", 10);

    // Motion planning pipeline: "ompl" (MoveIt default — samples the free space and
    // routes AROUND obstacles) or "pilz" (industrial point-to-point — deterministic
    // and repeatable, but goes the direct way; it collision-checks and FAILS rather
    // than detouring). Choosing between them, and designing the motion, is the paid
    // engineering this demo deliberately does not do.
    motion_planning_  = declare<std::string>("motion_planning", "ompl");
    ompl_planner_id_  = declare<std::string>("ompl_planner_id", "");     // "" = pipeline default
    pilz_planner_id_  = declare<std::string>("pilz_planner_id", "PTP");  // PTP | LIN | CIRC

    arm_joint_names_  = declare<std::vector<std::string>>(
      "arm_joint_names",
      {"shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint",
       "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"});
    home_joints_      = declare<std::vector<double>>(
      "home_joints", {0.0, -1.57, 1.57, -1.57, -1.57, 0.0});

    run_on_start_     = declare<bool>("run_on_start", true);
    target_timeout_s_ = declare<double>("target_timeout_s", 30.0);

    // Collision scene. With it ON, OMPL plans around the work tables and the demo
    // runs cleanly. Turn it OFF (use_collision_scene:=false) to show, on camera,
    // how unpredictable free-space planning is when the scene has no obstacles —
    // the teaching point behind the paid tracks. Boxes are solid (floor to top),
    // in the planning frame, matching the cell's two tables.
    use_collision_scene_ = declare<bool>("use_collision_scene", true);
    collision_frame_  = declare<std::string>("collision_frame", "world");
    table_a_size_     = declare<std::vector<double>>("table_a_size", {0.8, 1.5, 1.0});
    table_a_xyz_      = declare<std::vector<double>>("table_a_xyz",  {0.731, -0.048, 0.5});
    table_b_size_     = declare<std::vector<double>>("table_b_size", {1.5, 0.8, 1.0});
    table_b_xyz_      = declare<std::vector<double>>("table_b_xyz",  {-0.49, 0.69, 0.5});

    // --- ROS wiring ----------------------------------------------------------
    target_sub_ = node_->create_subscription<geometry_msgs::msg::PoseStamped>(
      target_topic_, rclcpp::QoS(1),
      [this](const geometry_msgs::msg::PoseStamped::SharedPtr msg) {
        last_target_ = *msg;
        have_target_ = true;
      });

    attach_client_ = node_->create_client<linkattacher_msgs::srv::AttachLink>("/ATTACHLINK");
    detach_client_ = node_->create_client<linkattacher_msgs::srv::DetachLink>("/DETACHLINK");

    run_srv_ = node_->create_service<std_srvs::srv::Trigger>(
      "/yt_vision/run",
      [this](const std::shared_ptr<std_srvs::srv::Trigger::Request>,
             std::shared_ptr<std_srvs::srv::Trigger::Response> res) {
        const bool ok = runOnce();
        res->success = ok;
        res->message = ok ? "pick-and-place completed" : "pick-and-place failed";
      });
  }

  // Construct the MoveIt interfaces. Call this only AFTER the node's executor is
  // already spinning — MoveGroupInterface needs live state to come up.
  void connect()
  {
    RCLCPP_INFO(logger_, "Connecting to MoveIt (arm='%s', gripper='%s')...",
                arm_group_.c_str(), gripper_group_.c_str());
    arm_ = std::make_shared<moveit::planning_interface::MoveGroupInterface>(node_, arm_group_);
    gripper_ = std::make_shared<moveit::planning_interface::MoveGroupInterface>(node_, gripper_group_);

    arm_->setPoseReferenceFrame(base_frame_);
    arm_->setEndEffectorLink(ee_link_);
    arm_->setMaxVelocityScalingFactor(vel_scale_);
    arm_->setMaxAccelerationScalingFactor(acc_scale_);
    arm_->setPlanningTime(planning_time_);
    arm_->setNumPlanningAttempts(planning_attempts_);
    gripper_->setMaxVelocityScalingFactor(vel_scale_);

    if (motion_planning_ == "pilz") {
      arm_->setPlanningPipelineId("pilz_industrial_motion_planner");
      arm_->setPlannerId(pilz_planner_id_);
      RCLCPP_INFO(logger_, "Motion planning: Pilz industrial (%s) — deterministic "
                           "point-to-point; does NOT route around obstacles.",
                  pilz_planner_id_.c_str());
    } else {
      arm_->setPlanningPipelineId("ompl");
      if (!ompl_planner_id_.empty()) arm_->setPlannerId(ompl_planner_id_);
      RCLCPP_INFO(logger_, "Motion planning: OMPL (sampling-based; avoids obstacles).");
    }

    RCLCPP_INFO(logger_, "Planning frame: %s | EE link: %s",
                arm_->getPlanningFrame().c_str(), arm_->getEndEffectorLink().c_str());

    if (use_collision_scene_) {
      addCollisionScene();
    } else {
      RCLCPP_WARN(logger_, "use_collision_scene=false — planning with NO obstacles in "
                           "the scene. Expect unpredictable paths and table collisions.");
    }
  }

  bool runOnStartIfRequested()
  {
    if (!run_on_start_) {
      RCLCPP_INFO(logger_, "run_on_start=false. Call the /yt_vision/run service to start.");
      return true;
    }
    return runOnce();
  }

private:
  template <typename T>
  T declare(const std::string & name, const T & def) { return node_->declare_parameter<T>(name, def); }

  geometry_msgs::msg::Quaternion topDownOrientation() const
  {
    tf2::Quaternion q;
    q.setRPY(grasp_roll_, grasp_pitch_, grasp_yaw_);
    q.normalize();
    return tf2::toMsg(q);
  }

  // Add the cell's work tables to the planning scene so OMPL plans around them.
  // Solid boxes (floor to just below the table surface), matching the world.
  void addCollisionScene()
  {
    moveit::planning_interface::PlanningSceneInterface psi;
    std::vector<moveit_msgs::msg::CollisionObject> objs;

    auto add_box = [&](const std::string & id, const std::vector<double> & size,
                       const std::vector<double> & xyz) {
      if (size.size() != 3 || xyz.size() != 3) {
        RCLCPP_WARN(logger_, "collision box '%s' needs 3-element size/xyz; skipping", id.c_str());
        return;
      }
      moveit_msgs::msg::CollisionObject o;
      o.header.frame_id = collision_frame_;
      o.id = id;
      shape_msgs::msg::SolidPrimitive box;
      box.type = shape_msgs::msg::SolidPrimitive::BOX;
      box.dimensions = {size[0], size[1], size[2]};
      geometry_msgs::msg::Pose p;
      p.position.x = xyz[0];
      p.position.y = xyz[1];
      p.position.z = xyz[2];
      p.orientation.w = 1.0;
      o.primitives.push_back(box);
      o.primitive_poses.push_back(p);
      o.operation = moveit_msgs::msg::CollisionObject::ADD;
      objs.push_back(o);
    };

    add_box("yt_work_table", table_a_size_, table_a_xyz_);
    add_box("yt_side_table", table_b_size_, table_b_xyz_);
    psi.applyCollisionObjects(objs);
    RCLCPP_INFO(logger_, "Collision scene: added %zu table box(es) in frame '%s'.",
                objs.size(), collision_frame_.c_str());
  }

  bool moveArmTo(double x, double y, double z, const geometry_msgs::msg::Quaternion & q,
                 const std::string & label)
  {
    geometry_msgs::msg::PoseStamped pose;
    pose.header.frame_id = base_frame_;
    pose.pose.position.x = x;
    pose.pose.position.y = y;
    pose.pose.position.z = z;
    pose.pose.orientation = q;
    arm_->setPoseTarget(pose, ee_link_);

    moveit::planning_interface::MoveGroupInterface::Plan plan;
    RCLCPP_INFO(logger_, "[%s] planning to (%.3f, %.3f, %.3f)...", label.c_str(), x, y, z);
    if (arm_->plan(plan) != moveit::core::MoveItErrorCode::SUCCESS) {
      RCLCPP_ERROR(logger_, "[%s] planning FAILED", label.c_str());
      return false;
    }
    if (arm_->execute(plan) != moveit::core::MoveItErrorCode::SUCCESS) {
      RCLCPP_ERROR(logger_, "[%s] execution FAILED", label.c_str());
      return false;
    }
    RCLCPP_INFO(logger_, "[%s] done", label.c_str());
    return true;
  }

  bool moveGripper(double value, const std::string & label)
  {
    gripper_->setJointValueTarget(gripper_joint_, value);
    if (gripper_->move() != moveit::core::MoveItErrorCode::SUCCESS) {
      RCLCPP_ERROR(logger_, "[%s] gripper move FAILED", label.c_str());
      return false;
    }
    RCLCPP_INFO(logger_, "[%s] gripper -> %.3f", label.c_str(), value);
    return true;
  }

  bool goHome()
  {
    if (home_joints_.size() != arm_joint_names_.size()) {
      RCLCPP_WARN(logger_, "home_joints size != arm_joint_names size; skipping home");
      return true;
    }
    std::map<std::string, double> target;
    for (size_t i = 0; i < arm_joint_names_.size(); ++i) target[arm_joint_names_[i]] = home_joints_[i];
    arm_->setJointValueTarget(target);
    if (arm_->move() != moveit::core::MoveItErrorCode::SUCCESS) {
      RCLCPP_ERROR(logger_, "[home] FAILED");
      return false;
    }
    RCLCPP_INFO(logger_, "[home] done");
    return true;
  }

  bool attach(bool do_attach)
  {
    const std::string what = do_attach ? "ATTACH" : "DETACH";
    if (do_attach) {
      if (!attach_client_->wait_for_service(5s)) {
        RCLCPP_ERROR(logger_, "[%s] /ATTACHLINK not available", what.c_str());
        return false;
      }
      auto req = std::make_shared<linkattacher_msgs::srv::AttachLink::Request>();
      req->model1_name = robot_model_name_;
      req->link1_name  = robot_grasp_link_;
      req->model2_name = object_model_;
      req->link2_name  = object_link_;
      auto fut = attach_client_->async_send_request(req);
      if (fut.wait_for(5s) != std::future_status::ready) {
        RCLCPP_ERROR(logger_, "[%s] service call timed out", what.c_str());
        return false;
      }
    } else {
      if (!detach_client_->wait_for_service(5s)) {
        RCLCPP_ERROR(logger_, "[%s] /DETACHLINK not available", what.c_str());
        return false;
      }
      auto req = std::make_shared<linkattacher_msgs::srv::DetachLink::Request>();
      req->model1_name = robot_model_name_;
      req->link1_name  = robot_grasp_link_;
      req->model2_name = object_model_;
      req->link2_name  = object_link_;
      auto fut = detach_client_->async_send_request(req);
      if (fut.wait_for(5s) != std::future_status::ready) {
        RCLCPP_ERROR(logger_, "[%s] service call timed out", what.c_str());
        return false;
      }
    }
    RCLCPP_INFO(logger_, "[%s] %s <-> %s ok", what.c_str(),
                robot_grasp_link_.c_str(), object_model_.c_str());
    return true;
  }

  bool waitForTarget()
  {
    RCLCPP_INFO(logger_, "Waiting for a detected target on '%s'...", target_topic_.c_str());
    const auto deadline = node_->now() + rclcpp::Duration::from_seconds(target_timeout_s_);
    rclcpp::Rate rate(10);
    while (rclcpp::ok() && !have_target_) {
      if (node_->now() > deadline) {
        RCLCPP_ERROR(logger_, "No target seen within %.0fs. Is the object in view / red enough?",
                     target_timeout_s_);
        return false;
      }
      rate.sleep();
    }
    RCLCPP_INFO(logger_, "Target at (%.3f, %.3f, %.3f) in %s",
                last_target_.pose.position.x, last_target_.pose.position.y,
                last_target_.pose.position.z, last_target_.header.frame_id.c_str());
    return have_target_;
  }

  bool runOnce()
  {
    if (running_.exchange(true)) {
      RCLCPP_WARN(logger_, "A pick-and-place is already running; ignoring.");
      return false;
    }
    struct Guard { std::atomic<bool> & r; ~Guard(){ r = false; } } guard{running_};

    const auto q = topDownOrientation();

    if (!moveGripper(gripper_open_, "open")) return false;
    if (!waitForTarget()) return false;

    const double tx = last_target_.pose.position.x;
    const double ty = last_target_.pose.position.y;
    const double tz = last_target_.pose.position.z;

    const double grasp_z = tz + grasp_z_offset_;
    const double carry_z = grasp_z + lift_dz_;
    const double px = tx + place_dx_;
    const double py = ty + place_dy_;

    if (!moveArmTo(tx, ty, tz + approach_z_offset_, q, "pregrasp")) return false;
    if (!moveArmTo(tx, ty, grasp_z,                 q, "grasp"))    return false;
    if (!moveGripper(gripper_close_, "close")) return false;
    if (!attach(true)) return false;
    if (!moveArmTo(tx, ty, carry_z, q, "lift"))  return false;
    if (!moveArmTo(px, py, carry_z, q, "carry")) return false;
    if (!moveArmTo(px, py, grasp_z, q, "place")) return false;
    if (!attach(false)) return false;
    if (!moveGripper(gripper_open_, "release")) return false;
    if (!moveArmTo(px, py, carry_z, q, "retreat")) return false;
    if (!goHome()) return false;

    RCLCPP_INFO(logger_, "Pick-and-place complete. Re-randomise the object and call /yt_vision/run again.");
    // Allow the next run to pick up a fresh detection.
    have_target_ = false;
    return true;
  }

  rclcpp::Node::SharedPtr node_;
  rclcpp::Logger logger_;

  std::shared_ptr<moveit::planning_interface::MoveGroupInterface> arm_;
  std::shared_ptr<moveit::planning_interface::MoveGroupInterface> gripper_;

  rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr target_sub_;
  rclcpp::Client<linkattacher_msgs::srv::AttachLink>::SharedPtr attach_client_;
  rclcpp::Client<linkattacher_msgs::srv::DetachLink>::SharedPtr detach_client_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr run_srv_;

  geometry_msgs::msg::PoseStamped last_target_;
  std::atomic<bool> have_target_{false};
  std::atomic<bool> running_{false};

  // parameters
  std::string arm_group_, gripper_group_, ee_link_, base_frame_, target_topic_;
  std::string robot_model_name_, robot_grasp_link_, object_model_, object_link_;
  std::string gripper_joint_;
  double gripper_close_, gripper_open_;
  double grasp_z_offset_, approach_z_offset_, lift_dz_;
  double place_dx_, place_dy_;
  double grasp_roll_, grasp_pitch_, grasp_yaw_;
  double vel_scale_, acc_scale_, planning_time_, target_timeout_s_;
  int planning_attempts_;
  std::string motion_planning_, ompl_planner_id_, pilz_planner_id_;
  std::vector<std::string> arm_joint_names_;
  std::vector<double> home_joints_;
  bool run_on_start_;

  bool use_collision_scene_;
  std::string collision_frame_;
  std::vector<double> table_a_size_, table_a_xyz_, table_b_size_, table_b_xyz_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("yt_pick_place_node");

  auto app = std::make_shared<PickPlace>(node);

  // Spin the node in the background so MoveGroupInterface and service futures work.
  rclcpp::executors::SingleThreadedExecutor executor;
  executor.add_node(node);
  std::thread spinner([&executor]() { executor.spin(); });

  app->connect();
  const bool ok = app->runOnStartIfRequested();
  RCLCPP_INFO(node->get_logger(),
              ok ? "Ready. Service /yt_vision/run is available for repeats."
                 : "Startup run failed. Fix the cause, then call /yt_vision/run.");

  // Keep serving the /yt_vision/run service until shutdown.
  spinner.join();
  rclcpp::shutdown();
  return 0;
}

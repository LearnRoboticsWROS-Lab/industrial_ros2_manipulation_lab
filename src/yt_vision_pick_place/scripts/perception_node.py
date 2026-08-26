#!/usr/bin/env python3
"""yt_vision_pick_place — perception_node

The whole "vision" of the demo, in one file. It finds a red object in the
camera image by colour, reads its depth, turns that pixel into a 3D point using
the camera intrinsics, transforms the point into the robot base frame, and
publishes it as a target pose for the motion node.

    RGB image ─┐
    depth image┤─► red-colour centroid (u, v) ─► deproject with (fx, fy, cx, cy)
    camera_info┘        + depth[v, u]           ─► 3D point in camera frame
                                                ─► TF2 ─► point in base frame
                                                ─► /yt_vision/target_pose (+ RViz marker)

Deliberately a plain colour threshold, not a perception pipeline. Swapping this
for a real detector, or making it reusable/configurable/robust, is exactly the
engineering the paid Simulation Track teaches (see the project README).
"""

import numpy as np
import cv2

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.duration import Duration

import message_filters
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped, PointStamped
from visualization_msgs.msg import Marker

import tf2_ros
import tf2_geometry_msgs  # noqa: F401  (registers PointStamped transforms)


class PerceptionNode(Node):
    def __init__(self):
        super().__init__("yt_perception_node")

        # --- parameters ------------------------------------------------------
        self.rgb_topic = self.declare_parameter("rgb_topic", "/camera/image_raw").value
        self.depth_topic = self.declare_parameter("depth_topic", "/camera/depth/image_raw").value
        self.info_topic = self.declare_parameter("info_topic", "/camera/camera_info").value
        self.base_frame = self.declare_parameter("base_frame", "base_link").value
        self.target_topic = self.declare_parameter("target_topic", "/yt_vision/target_pose").value

        # Red wraps around hue 0/180, so we use two HSV bands.
        self.h_lo1 = self.declare_parameter("hue_low_1", 0).value
        self.h_hi1 = self.declare_parameter("hue_high_1", 10).value
        self.h_lo2 = self.declare_parameter("hue_low_2", 160).value
        self.h_hi2 = self.declare_parameter("hue_high_2", 179).value
        self.s_min = self.declare_parameter("sat_min", 100).value
        self.v_min = self.declare_parameter("val_min", 60).value
        self.min_area = self.declare_parameter("min_area_px", 150).value

        self.bridge = CvBridge()
        self.info = None

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.pose_pub = self.create_publisher(PoseStamped, self.target_topic, 1)
        self.marker_pub = self.create_publisher(Marker, "/yt_vision/target_marker", 1)

        self.create_subscription(CameraInfo, self.info_topic, self._on_info, 10)

        rgb_sub = message_filters.Subscriber(self, Image, self.rgb_topic, qos_profile=qos_profile_sensor_data)
        depth_sub = message_filters.Subscriber(self, Image, self.depth_topic, qos_profile=qos_profile_sensor_data)
        self.sync = message_filters.ApproximateTimeSynchronizer([rgb_sub, depth_sub], queue_size=10, slop=0.1)
        self.sync.registerCallback(self._on_frame)

        self._warned_no_info = False
        self.get_logger().info(
            f"Perception up. RGB='{self.rgb_topic}' depth='{self.depth_topic}' "
            f"info='{self.info_topic}' -> '{self.target_topic}' (base '{self.base_frame}')")

    def _on_info(self, msg: CameraInfo):
        self.info = msg

    # -- pixel + depth -> 3D point in the camera optical frame ----------------
    def _deproject(self, u, v, z):
        fx = self.info.k[0]
        fy = self.info.k[4]
        cx = self.info.k[2]
        cy = self.info.k[5]
        x = (u - cx) * z / fx
        y = (v - cy) * z / fy
        return x, y, z

    def _on_frame(self, rgb_msg: Image, depth_msg: Image):
        if self.info is None:
            if not self._warned_no_info:
                self.get_logger().warn(f"Waiting for CameraInfo on '{self.info_topic}'...")
                self._warned_no_info = True
            return

        rgb = self.bridge.imgmsg_to_cv2(rgb_msg, desired_encoding="bgr8")
        depth = self.bridge.imgmsg_to_cv2(depth_msg, desired_encoding="passthrough")

        # Colour segmentation: red in HSV (two bands), then largest blob.
        hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
        m1 = cv2.inRange(hsv, (self.h_lo1, self.s_min, self.v_min), (self.h_hi1, 255, 255))
        m2 = cv2.inRange(hsv, (self.h_lo2, self.s_min, self.v_min), (self.h_hi2, 255, 255))
        mask = cv2.morphologyEx(m1 | m2, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return
        blob = max(contours, key=cv2.contourArea)
        if cv2.contourArea(blob) < self.min_area:
            return
        mm = cv2.moments(blob)
        if mm["m00"] == 0:
            return
        u = int(mm["m10"] / mm["m00"])
        v = int(mm["m01"] / mm["m00"])

        z = self._read_depth(depth, u, v)
        if z is None:
            return

        x, y, zc = self._deproject(u, v, z)

        # Point in the camera optical frame; transform into the base frame.
        pt = PointStamped()
        pt.header = depth_msg.header  # frame_id = camera_optical_link
        pt.point.x, pt.point.y, pt.point.z = float(x), float(y), float(zc)
        try:
            pt_base = self.tf_buffer.transform(
                pt, self.base_frame, timeout=Duration(seconds=0.5))
        except (tf2_ros.LookupException, tf2_ros.ExtrapolationException,
                tf2_ros.ConnectivityException) as exc:
            self.get_logger().warn(f"TF {pt.header.frame_id}->{self.base_frame} failed: {exc}",
                                   throttle_duration_sec=2.0)
            return

        self._publish(pt_base)

    def _read_depth(self, depth, u, v):
        # Median over a small window is steadier than a single pixel.
        h, w = depth.shape[:2]
        u0, u1 = max(0, u - 2), min(w, u + 3)
        v0, v1 = max(0, v - 2), min(h, v + 3)
        patch = depth[v0:v1, u0:u1].astype(np.float32).ravel()
        patch = patch[np.isfinite(patch)]
        patch = patch[patch > 0.0]
        if patch.size == 0:
            return None
        z = float(np.median(patch))
        # gazebo depth is metres (32FC1); guard against a mm (16UC1) camera too.
        if z > 20.0:
            z /= 1000.0
        return z

    def _publish(self, pt_base: PointStamped):
        pose = PoseStamped()
        pose.header.frame_id = self.base_frame
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position = pt_base.point
        pose.pose.orientation.w = 1.0  # motion node sets the grasp orientation
        self.pose_pub.publish(pose)

        marker = Marker()
        marker.header = pose.header
        marker.ns = "yt_vision"
        marker.id = 0
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose = pose.pose
        marker.scale.x = marker.scale.y = marker.scale.z = 0.04
        marker.color.r, marker.color.g, marker.color.b, marker.color.a = 1.0, 0.1, 0.1, 0.9
        self.marker_pub.publish(marker)

        self.get_logger().info(
            f"target @ base ({pt_base.point.x:.3f}, {pt_base.point.y:.3f}, {pt_base.point.z:.3f})",
            throttle_duration_sec=1.0)


def main():
    rclpy.init()
    node = PerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

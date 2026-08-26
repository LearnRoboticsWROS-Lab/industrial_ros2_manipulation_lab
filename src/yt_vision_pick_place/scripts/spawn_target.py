#!/usr/bin/env python3
"""yt_vision_pick_place — spawn_target

Puts the red target object into Gazebo at a random, valid position so the demo
proves the robot is *not* using hard-coded coordinates. Re-randomise at any time
by calling the /yt_vision/randomize service, then call /yt_vision/run again.

Reuses the red_cube model already shipped with lrwros_ur5_workcell — nothing is
duplicated. This is the minimum needed for the demo, not a domain-randomisation
framework.
"""

import os
import random

import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory
from gazebo_msgs.srv import SpawnEntity, DeleteEntity
from std_srvs.srv import Trigger


class SpawnTarget(Node):
    def __init__(self):
        super().__init__("yt_spawn_target")

        self.model_name = self.declare_parameter("model_name", "yt_red_cube").value
        # Objects to remove before (re)spawning: the cell's own grey 'red_cube'
        # (rendered with the Gazebo/Grey script, so colour detection can't see it),
        # and any previous target of ours.
        self.delete_names = self.declare_parameter(
            "delete_names", ["red_cube", "yt_red_cube"]).value
        self.pkg = self.declare_parameter("model_pkg", "yt_vision_pick_place").value
        default_sdf = os.path.join(
            get_package_share_directory(self.pkg), "models", "yt_red_cube", "model.sdf")
        self.sdf_path = self.declare_parameter("sdf_path", default_sdf).value

        # Valid pick region on the work surface, in WORLD coordinates. The cell's
        # table sits ~1.0 m up (the robot is on a pedestal); the cell's own cube
        # rests at (0.5, 0.0, ~1.115). Spawn just above so it settles onto the table.
        self.x_min = self.declare_parameter("x_min", 0.40).value
        self.x_max = self.declare_parameter("x_max", 0.60).value
        self.y_min = self.declare_parameter("y_min", -0.15).value
        self.y_max = self.declare_parameter("y_max", 0.15).value
        self.z_spawn = self.declare_parameter("z_spawn", 1.15).value

        with open(self.sdf_path, "r") as fh:
            self.sdf_xml = fh.read()

        self.spawn_cli = self.create_client(SpawnEntity, "/spawn_entity")
        self.delete_cli = self.create_client(DeleteEntity, "/delete_entity")

        self.srv = self.create_service(Trigger, "/yt_vision/randomize", self._on_randomize)

        # Spawn once at startup.
        self._respawn()

    def _random_pose(self):
        x = random.uniform(self.x_min, self.x_max)
        y = random.uniform(self.y_min, self.y_max)
        return x, y, self.z_spawn

    def _delete_all(self):
        if not self.delete_cli.wait_for_service(timeout_sec=5.0):
            return
        for name in self.delete_names:
            req = DeleteEntity.Request()
            req.name = name
            fut = self.delete_cli.call_async(req)
            rclpy.spin_until_future_complete(self, fut, timeout_sec=5.0)

    def _respawn(self):
        # Remove the grey cell cube and any previous target (ignored if absent),
        # then spawn our red target at a new spot.
        self._delete_all()
        if not self.spawn_cli.wait_for_service(timeout_sec=10.0):
            self.get_logger().error("/spawn_entity not available — is Gazebo up?")
            return None
        x, y, z = self._random_pose()
        req = SpawnEntity.Request()
        req.name = self.model_name
        req.xml = self.sdf_xml
        req.initial_pose.position.x = x
        req.initial_pose.position.y = y
        req.initial_pose.position.z = z
        fut = self.spawn_cli.call_async(req)
        rclpy.spin_until_future_complete(self, fut, timeout_sec=10.0)
        self.get_logger().info(f"Spawned '{self.model_name}' at ({x:.3f}, {y:.3f}, {z:.3f})")
        return x, y, z

    def _on_randomize(self, _request, response):
        pose = self._respawn()
        response.success = pose is not None
        response.message = (f"respawned at ({pose[0]:.3f}, {pose[1]:.3f})"
                            if pose else "spawn failed")
        return response


def main():
    rclpy.init()
    node = SpawnTarget()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

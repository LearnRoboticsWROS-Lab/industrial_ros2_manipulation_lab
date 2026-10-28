#!/usr/bin/env python3
"""LinkAttacher grasp adapter for the TrainIt Gazebo backend (ADR-0008 F2 / ADR-0010).

Gazebo Classic has no suction/gripper-grasp physics, so a grasp is simulated by a rigid
weld: the IFRA_LinkAttacher plugin's ``/ATTACHLINK`` / ``/DETACHLINK`` services. This node
is the Gazebo **sim grasp adapter** and follows the SAME contract as the Isaac SurfaceGripper
adapter (``isaac_gripper_subscriber.py``): it subscribes to the grasp signal — a latched
``std_msgs/Bool`` on ``gripper_cmd_topic`` — and welds on ``true`` / releases on ``false``.

That Bool is the single, backend-agnostic grasp signal published by the runtime
(``trainit_run_bt`` when ``gripper_cmd_topic`` is set, ADR-0010), the SAME topic
``scene_manager_node`` uses to attach the object in the MoveIt planning scene. So the physics
weld and the planning-scene attach fire together, with no per-simulator BT branch.

The plugin's answer to every request is logged ("ATTACH done: ..."); a refusal is tried once
more, then reported as an ERROR naming the plugin's reason -- the runtime does not see the
weld, so this log is where a part that was never held shows up.

It runs ONLY in the ``gazebo`` backend. Wire it into the cell's ``*_moveit_config`` bring-up
(the adaptation layer) or capture it as a bridge with ``modes: [gazebo]`` — TSA selects the
adapter but does not invent the wiring. Depends on ``linkattacher_msgs`` (clone
IFRA_LinkAttacher into the workspace; Gazebo backend only).

Parameters:
  gripper_cmd_topic (str)  the grasp signal (std_msgs/Bool, latched). Match
                           scene.yaml / bt_params ``gripper_cmd_topic`` (default /isaac_gripper_cmd).
  robot_model  (str)  the spawned robot model name (spawn_entity -entity <name>)
  ee_link      (str)  the end-effector link the object welds to (e.g. "robotiq_85_base_link")
  object_model (str)  the Gazebo model welded on grasp (e.g. "red_box")
  object_link  (str)  its link name (default "link")
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from std_msgs.msg import Bool

try:
    from linkattacher_msgs.srv import AttachLink, DetachLink
except ImportError:  # pragma: no cover - only importable with IFRA_LinkAttacher present
    AttachLink = DetachLink = None


class LinkAttacherBridge(Node):
    def __init__(self):
        super().__init__('link_attacher_bridge')
        self.declare_parameter('gripper_cmd_topic', '/isaac_gripper_cmd')
        self.declare_parameter('robot_model', 'robot')
        self.declare_parameter('ee_link', 'ee_link')
        self.declare_parameter('object_model', 'red_box')
        self.declare_parameter('object_link', 'link')
        g = lambda n: self.get_parameter(n).get_parameter_value().string_value
        self._topic = g('gripper_cmd_topic')
        self._robot_model, self._ee_link = g('robot_model'), g('ee_link')
        self._obj_model, self._obj_link = g('object_model'), g('object_link')
        self._last = None  # act only on change (a latched topic re-delivers on connect)
        self._signal = 0   # bumped on every change: an older request's answer or retry is dropped
        self._welded = False  # the plugin confirmed this bridge's last weld
        self._retry = None    # the one pending retry

        if AttachLink is None:
            self.get_logger().error(
                'linkattacher_msgs not found: clone IFRA_LinkAttacher into the workspace '
                '(Gazebo backend only). The grasp weld is inert until then.')
        self._attach = self.create_client(AttachLink, '/ATTACHLINK') if AttachLink else None
        self._detach = self.create_client(DetachLink, '/DETACHLINK') if DetachLink else None

        # Match the runtime publisher's QoS: latched (transient-local, depth 1) so a grasp
        # signal sent before this node connects is still delivered.
        latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.create_subscription(Bool, self._topic, self._on_cmd, latched)
        self.get_logger().info(
            f'LinkAttacher adapter: {self._topic} (Bool) welds '
            f'{self._robot_model}/{self._ee_link} <-> {self._obj_model}/{self._obj_link}')

    def _on_cmd(self, msg: Bool):
        close = bool(msg.data)
        if close == self._last:
            return
        self._last = close
        self._signal += 1
        self._cancel_retry()
        self._request(close, self._signal, retry=True)

    def _cancel_retry(self):
        if self._retry is not None:
            self._retry.cancel()
            self.destroy_timer(self._retry)
            self._retry = None

    def _request(self, close: bool, signal: int, retry: bool):
        client, srv_type = (self._attach, AttachLink) if close else (self._detach, DetachLink)
        if client is None:
            self.get_logger().warn('linkattacher_msgs unavailable (IFRA_LinkAttacher not built)')
            return
        if not client.wait_for_service(timeout_sec=2.0):
            self.get_logger().error(f'{client.srv_name} not available: ' + (
                'the part is not welded to the gripper' if close else 'the part may still be welded'))
            return
        req = srv_type.Request()
        req.model1_name, req.link1_name = self._robot_model, self._ee_link
        req.model2_name, req.link2_name = self._obj_model, self._obj_link
        # the plugin answers success + a message; a refusal (a model or link it cannot find, a
        # weld it already holds) is otherwise invisible -- the cycle goes on either way
        client.call_async(req).add_done_callback(
            lambda future: self._on_response(close, signal, retry, future))
        self.get_logger().info(f'{"ATTACH" if close else "DETACH"} -> {client.srv_name}')

    def _on_response(self, close: bool, signal: int, retry: bool, future):
        what = 'ATTACH' if close else 'DETACH'
        error = future.exception()
        res = None if error is not None else future.result()
        why = (res.message if res is not None else repr(error)) or 'no message'
        if res is not None and res.success:
            self._welded = close
            self.get_logger().info(f'{what} done: {why}')
            return
        if signal != self._signal:   # the grasp signal changed since: its own request rules
            return
        if not close and not self._welded:   # e.g. the opening command at start-up
            self.get_logger().info(f'DETACH: nothing this bridge welded to release ({why})')
            return
        if retry:
            self.get_logger().warn(f'{what} refused by Gazebo ({why}): trying once more')

            def again():
                self._cancel_retry()
                if signal == self._signal:
                    self._request(close, signal, retry=False)
            self._retry = self.create_timer(0.5, again)
            return
        if close:
            self.get_logger().error(f'ATTACH FAILED in Gazebo ({why}): this weld was not made, and the '
                                    'cycle goes on with the part maybe not in the gripper')
        else:
            self.get_logger().error(f'DETACH FAILED in Gazebo ({why}): the part may still be welded '
                                    'to the gripper')


def main(args=None):
    rclpy.init(args=args)
    node = LinkAttacherBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

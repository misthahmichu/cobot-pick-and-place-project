import rclpy
from rclpy.node import Node
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, JointConstraint
from rclpy.action import ActionClient
from std_srvs.srv import SetBool
from std_msgs.msg import String
import time
import json

PLACE_BLUE  = [-1.941, -1.182, 1.550, -2.044, -1.460,  0.000]
PLACE_RED   = [-1.701, -1.186, 1.249, -1.357, -1.632,  0.000]
PLACE_GREEN = [-1.529, -1.185, 1.349, -1.357, -1.632,  0.000]
HOME  = [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]
SCAN  = [0.0, -1.529, 0.344, -0.807, -1.495, 0.0]
SCAN_CAMERA_X = 0.60
SCAN_CAMERA_Y = 0.00

KNOWN_ABOVE = {
    (0.40,  0.00): [ 0.052,  -1.0,   1.056, -1.170, -1.570,  0.000],
    (0.45, -0.15): [-0.292, -1.804,  2.020, -1.529, -1.529, -0.008],
    (0.45,  0.15): [ 0.120,  -1.495, 1.718, -1.632, -1.529,  0.210],
    (0.55, -0.15): [-0.350,  -1.185, 1.366, -1.357, -1.632,  0.000],
    (0.50, -0.20): [-0.120,  -1.288, 1.466, -1.529, -1.529, -0.008],
    (0.55,  0.05): [-0.567,  -1.426, 1.651, -1.632, -1.529,  0.210],
}
KNOWN_LIFT = {
    (0.40,  0.00): [ 0.052,  -1.25,  1.232, -1.570, -1.460,  0.000],
    (0.45, -0.15): [ 0.052,  -1.80,  1.800, -1.327, -1.529,  0.000],
    (0.45,  0.15): [-0.086,  -1.50,  1.500, -1.323, -1.529,  0.017],
    (0.55, -0.15): [-0.420,  -1.185, 1.215, -1.357, -1.632,  0.000],
    (0.50, -0.20): [ 0.052,  -1.25,  1.232, -1.570, -1.460,  0.000],
    (0.55,  0.05): [-0.429,  -1.185, 1.215, -1.357, -1.632,  0.000],
}


def interpolate_joints(x, y, table):
    points = list(table.keys())
    joints = list(table.values())
    dists  = [((x-kx)**2 + (y-ky)**2)**0.5 for (kx,ky) in points]
    min_d  = min(dists)
    if min_d < 0.01:
        return joints[dists.index(min_d)]
    weights = [1.0/d for d in dists]
    total_w = sum(weights)
    n = len(joints[0])
    return [round(sum(weights[i]*joints[i][j] for i in range(len(points)))/total_w, 4)
            for j in range(n)]


class WristCameraPickPlace(Node):
    def __init__(self):
        super().__init__('wrist_camera_pick_place')
        self._action_client  = ActionClient(self, MoveGroup, '/move_action')
        self._gripper_client = self.create_client(SetBool, '/vacuum_gripper/switch')
        self.pose_pub        = self.create_publisher(String, '/wrist_camera/scan_pose', 10)
        self.detected_boxes  = []
        self.boxes_received  = False
        self.box_sub = self.create_subscription(
            String, '/detected_boxes', self._boxes_cb, 10)
        self.get_logger().info('Wrist Camera Pick & Place Ready!')

    def _boxes_cb(self, msg):
        try:
            data = json.loads(msg.data)
            if data:
                self.detected_boxes = data
                self.boxes_received = True
        except Exception as e:
            self.get_logger().error(f'Box parse error: {e}')

    def publish_scan_pose(self, x, y):
        msg = String()
        msg.data = json.dumps({'x': x, 'y': y})
        for _ in range(5):
            self.pose_pub.publish(msg)
            time.sleep(0.1)
        self.get_logger().info(f'Scan pose sent: x={x} y={y}')

    def wait_for_detection(self, timeout=8.0):
        self.get_logger().info('Waiting for box detections...')
        self.boxes_received = False
        start = time.time()
        while not self.boxes_received:
            rclpy.spin_once(self, timeout_sec=0.3)
            if time.time() - start > timeout:
                self.get_logger().warn('Detection timeout!')
                return False
        return True

    def get_sorted_boxes(self):
        for _ in range(8):
            rclpy.spin_once(self, timeout_sec=0.2)
        order = {'blue': 0, 'red': 1, 'green': 2}
        return sorted(self.detected_boxes, key=lambda b: order.get(b['color'], 99))

    def move_to_joints(self, positions, label=''):
        self.get_logger().info(f'Moving to: {label}')
        goal = MoveGroup.Goal()
        goal.request.group_name                      = 'ur_manipulator'
        goal.request.num_planning_attempts           = 10
        goal.request.allowed_planning_time           = 5.0
        goal.request.max_velocity_scaling_factor     = 0.1
        goal.request.max_acceleration_scaling_factor = 0.1
        c = Constraints()
        names = ['shoulder_pan_joint','shoulder_lift_joint','elbow_joint',
                 'wrist_1_joint','wrist_2_joint','wrist_3_joint']
        for name, pos in zip(names, positions):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position   = pos
            jc.tolerance_above = jc.tolerance_below = 0.01
            jc.weight = 1.0
            c.joint_constraints.append(jc)
        goal.request.goal_constraints.append(c)
        self._action_client.wait_for_server()
        future = self._action_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        gh = future.result()
        if not gh or not gh.accepted:
            self.get_logger().error(f'Rejected: {label}')
            return False
        rclpy.spin_until_future_complete(self, gh.get_result_async())
        self.get_logger().info(f'Done: {label}')
        return True

    def vacuum_on(self):
        self.get_logger().info('Vacuum ON')
        req = SetBool.Request()
        req.data = True
        if self._gripper_client.wait_for_service(timeout_sec=5.0):
            rclpy.spin_until_future_complete(self, self._gripper_client.call_async(req))

    def vacuum_off(self):
        self.get_logger().info('Vacuum OFF')
        req = SetBool.Request()
        req.data = False
        if self._gripper_client.wait_for_service(timeout_sec=5.0):
            rclpy.spin_until_future_complete(self, self._gripper_client.call_async(req))


def main(args=None):
    rclpy.init(args=args)
    node = WristCameraPickPlace()
    place_map = {'red': PLACE_RED, 'blue': PLACE_BLUE, 'green': PLACE_GREEN}

    node.move_to_joints(HOME, 'HOME')
    time.sleep(1.0)

    node.get_logger().info('Moving to SCAN position...')
    node.move_to_joints(SCAN, 'SCAN')
    time.sleep(2.0)

    node.publish_scan_pose(SCAN_CAMERA_X, SCAN_CAMERA_Y)
    time.sleep(0.5)

    if not node.wait_for_detection(timeout=10.0):
        node.get_logger().error('No boxes detected!')
        node.move_to_joints(HOME, 'HOME')
        node.destroy_node()
        rclpy.shutdown()
        return

    boxes = node.get_sorted_boxes()
    node.get_logger().info(f'=== Detected {len(boxes)} boxes ===')
    for b in boxes:
        node.get_logger().info(f"  {b['color']:6s}  x={b['x']:.3f}  y={b['y']:.3f}")

    for box in boxes:
        color = box['color']
        bx, by = box['x'], box['y']
        node.get_logger().info(f'Picking {color} at ({bx:.3f}, {by:.3f})')
        ABOVE = interpolate_joints(bx, by, KNOWN_ABOVE)
        LIFT  = interpolate_joints(bx, by, KNOWN_LIFT)
        PLACE = place_map[color]
        if not node.move_to_joints(ABOVE, f'ABOVE {color}'):
            continue
        time.sleep(2.0)
        node.vacuum_on()
        time.sleep(2.0)
        if not node.move_to_joints(LIFT, f'LIFT {color}'):
            node.vacuum_off()
            continue
        time.sleep(0.5)
        node.move_to_joints(PLACE, f'PLACE {color}')
        time.sleep(0.5)
        node.vacuum_off()
        time.sleep(1.0)
        node.get_logger().info(f'{color} box sorted!')

    node.move_to_joints(HOME, 'FINAL HOME')
    node.get_logger().info('All boxes picked and sorted!')
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

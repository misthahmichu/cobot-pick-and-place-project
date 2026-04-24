import rclpy
from rclpy.node import Node
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, JointConstraint
from rclpy.action import ActionClient
from std_srvs.srv import SetBool
import time

class PickAndPlace(Node):
    def __init__(self):
        super().__init__('pick_and_place')
        self._action_client = ActionClient(self, MoveGroup, '/move_action')
        self._gripper_client = self.create_client(SetBool, '/vacuum_gripper/switch')
        self.get_logger().info('Pick and Place Node Started! 🤖')

    def move_to_joints(self, positions, label=''):
        self.get_logger().info(f'🔧 Moving to: {label}')
        goal = MoveGroup.Goal()
        goal.request.group_name = 'ur_manipulator'
        goal.request.num_planning_attempts = 10
        goal.request.allowed_planning_time = 5.0
        goal.request.max_velocity_scaling_factor = 0.1
        goal.request.max_acceleration_scaling_factor = 0.1
        c = Constraints()
        names = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
                 'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
        for name, pos in zip(names, positions):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position = pos
            jc.tolerance_above = 0.01
            jc.tolerance_below = 0.01
            jc.weight = 1.0
            c.joint_constraints.append(jc)
        goal.request.goal_constraints.append(c)
        self._action_client.wait_for_server()
        future = self._action_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        gh = future.result()
        if not gh or not gh.accepted:
            self.get_logger().error(f'❌ Goal rejected: {label}')
            return False
        res_future = gh.get_result_async()
        rclpy.spin_until_future_complete(self, res_future)
        self.get_logger().info(f'✅ Done: {label}')
        return True

    def vacuum_on(self):
        self.get_logger().info('🟢 Vacuum ON')
        req = SetBool.Request()
        req.data = True
        if self._gripper_client.wait_for_service(timeout_sec=5.0):
            future = self._gripper_client.call_async(req)
            rclpy.spin_until_future_complete(self, future)

    def vacuum_off(self):
        self.get_logger().info('🔴 Vacuum OFF')
        req = SetBool.Request()
        req.data = False
        if self._gripper_client.wait_for_service(timeout_sec=5.0):
            future = self._gripper_client.call_async(req)
            rclpy.spin_until_future_complete(self, future)

def main(args=None):
    rclpy.init(args=args)
    node = PickAndPlace()

    # ── HOME ─────────────────────────────────────────
    HOME = [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]

    # ── ABOVE positions (gripper touching each box) ──
    ABOVE_BLUE_1  = [0.052,  -1.0,   1.056,  -1.170, -1.57,  0.000]
    ABOVE_BLUE_2  = [-0.292, -1.804, 2.020,  -1.529, -1.529, -0.008]
    ABOVE_RED_1   = [0.120,  -1.495, 1.718,  -1.632, -1.529,  0.210]
    ABOVE_RED_2   = [-0.35, -1.185, 1.366,  -1.357, -1.632,  0.000]
    ABOVE_GREEN_1 = [-0.120, -1.288, 1.466,  -1.529, -1.529, -0.008]
    ABOVE_GREEN_2 = [-0.567, -1.426, 1.651,  -1.632, -1.529,  0.210]

    # ── LIFT positions (safe height after picking) ───
    LIFT_BLUE_1   = [0.052,   -1.25,  1.232,  -1.570, -1.460, 0.000]
    LIFT_BLUE_2   = [0.052, -1.80, 1.80,  -1.327, -1.529,  0.000]
    LIFT_RED_1    = [-0.086, -1.50,  1.50,  -1.323, -1.529, 0.017]
    LIFT_RED_2    = [-0.42, -1.185, 1.215,  -1.357, -1.632,  0.000]
    LIFT_GREEN_1  = [0.052,  -1.25,  1.232,  -1.570, -1.460,  0.000]
    LIFT_GREEN_2  = [-0.429, -1.185, 1.215,  -1.357, -1.632,  0.000]

    # ── PLACE positions (above basket per color) ─────
    PLACE_BLUE  = [-1.941, -1.182, 1.550, -2.044, -1.460,  0.000]
    PLACE_RED   = [-1.701, -1.186, 1.249, -1.357, -1.632,  0.000]
    PLACE_GREEN = [-1.529, -1.185, 1.349, -1.357, -1.632,  0.000]

    # ── Box sequence: blue first, then red, then green
    # (ABOVE, LIFT, PLACE, name)
    boxes = [
        (ABOVE_BLUE_1,  LIFT_BLUE_1,  PLACE_BLUE,  'box_blue_1'),
        (ABOVE_BLUE_2,  LIFT_BLUE_2,  PLACE_BLUE,  'box_blue_2'),
        (ABOVE_RED_1,   LIFT_RED_1,   PLACE_RED,   'box_red_1'),
        (ABOVE_RED_2,   LIFT_RED_2,   PLACE_RED,   'box_red_2'),
        (ABOVE_GREEN_1, LIFT_GREEN_1, PLACE_GREEN, 'box_green_1'),
        (ABOVE_GREEN_2, LIFT_GREEN_2, PLACE_GREEN, 'box_green_2'),
    ]

    node.get_logger().info('=== Starting Full Pick & Place ===')
    node.move_to_joints(HOME, 'HOME')
    time.sleep(1.0)

    for ABOVE, LIFT, PLACE, box_name in boxes:
        node.get_logger().info(f'━━━ Picking {box_name} ━━━')

        # Step 1: Move ABOVE box
        if not node.move_to_joints(ABOVE, f'ABOVE {box_name}'):
            node.get_logger().error(f'❌ Failed ABOVE {box_name} — skipping!')
            continue
        time.sleep(2.0)

        # Step 2: Vacuum ON
        node.vacuum_on()
        time.sleep(2.0)

        # Step 3: Lift UP
        if not node.move_to_joints(LIFT, f'LIFT {box_name}'):
            node.get_logger().error(f'❌ Failed LIFT — dropping!')
            node.vacuum_off()
            continue
        time.sleep(0.5)

        # Step 4: Move to basket
        node.move_to_joints(PLACE, f'PLACE {box_name}')
        time.sleep(0.5)

        # Step 5: Vacuum OFF
        node.vacuum_off()
        time.sleep(1.0)

        node.get_logger().info(f'✅ {box_name} placed!')

    # Return HOME only at the very end
    node.move_to_joints(HOME, 'FINAL HOME')
    node.get_logger().info('🎉 All 6 boxes picked and placed!')
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
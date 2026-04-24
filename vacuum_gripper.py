import rclpy
from rclpy.node import Node
from std_srvs.srv import Empty
from gazebo_msgs.srv import ApplyBodyWrench
from geometry_msgs.msg import Wrench, Point
import time

class VacuumGripper(Node):
    def __init__(self):
        super().__init__('vacuum_gripper')
        
        # Service clients for attaching/detaching objects
        self.attach_client = self.create_client(
            Empty, '/vacuum_gripper/on')
        self.detach_client = self.create_client(
            Empty, '/vacuum_gripper/off')
        
        self.get_logger().info('Vacuum Gripper Node Ready!')

    def gripper_on(self):
        self.get_logger().info('Vacuum ON - Picking object...')
        req = Empty.Request()
        if self.attach_client.wait_for_service(timeout_sec=2.0):
            future = self.attach_client.call_async(req)
            rclpy.spin_until_future_complete(self, future)
            self.get_logger().info('Gripper ON!')
        else:
            self.get_logger().warn('Gripper ON service not available')

    def gripper_off(self):
        self.get_logger().info('Vacuum OFF - Releasing object...')
        req = Empty.Request()
        if self.detach_client.wait_for_service(timeout_sec=2.0):
            future = self.detach_client.call_async(req)
            rclpy.spin_until_future_complete(self, future)
            self.get_logger().info('Gripper OFF!')
        else:
            self.get_logger().warn('Gripper OFF service not available')

def main(args=None):
    rclpy.init(args=args)
    node = VacuumGripper()
    
    # Test gripper
    node.gripper_on()
    time.sleep(2)
    node.gripper_off()
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
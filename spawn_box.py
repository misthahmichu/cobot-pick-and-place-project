import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SpawnEntity
import random

class SpawnObjects(Node):
    def __init__(self):
        super().__init__('spawn_objects')
        self.client = self.create_client(SpawnEntity, '/spawn_entity')
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for spawn_entity service...')

    def spawn(self, name, xml):
        request = SpawnEntity.Request()
        request.name = name
        request.xml = xml
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        self.get_logger().info(f'{name} spawned! ✅')

    def make_box(self, name, x, y, z, r, g, b):
        return f"""
        <sdf version='1.6'>
          <model name='{name}'>
            <pose>{x} {y} {z} 0 0 0</pose>
            <link name='link'>
              <collision name='collision'>
                <geometry><box><size>0.05 0.05 0.05</size></box></geometry>
              </collision>
              <visual name='visual'>
                <geometry><box><size>0.05 0.05 0.05</size></box></geometry>
                <material><ambient>{r} {g} {b} 1</ambient></material>
              </visual>
              <inertial>
                <mass>0.1</mass>
                <inertia>
                  <ixx>0.0001</ixx><iyy>0.0001</iyy><izz>0.0001</izz>
                </inertia>
              </inertial>
            </link>
          </model>
        </sdf>"""

    def make_basket(self, name, x, y, r, g, b):
        return f"""
        <sdf version='1.6'>
          <model name='{name}'>
            <pose>{x} {y} 0.0 0 0 0</pose>
            <static>true</static>
            <link name='link'>
              <collision name='collision'>
                <geometry><box><size>0.4 0.4 0.05</size></box></geometry>
              </collision>
              <visual name='visual'>
                <geometry><box><size>0.4 0.4 0.05</size></box></geometry>
                <material><ambient>{r} {g} {b} 1</ambient></material>
              </visual>
            </link>
          </model>
        </sdf>"""

def main(args=None):
    rclpy.init(args=args)
    node = SpawnObjects()

    # Spawn table
    table_xml = """
    <sdf version='1.6'>
      <model name='table'>
        <pose>0.6 0.0 0.0 0 0 0</pose>
        <static>true</static>
        <link name='link'>
          <collision name='collision'>
            <geometry><box><size>0.6 0.8 0.4</size></box></geometry>
          </collision>
          <visual name='visual'>
            <geometry><box><size>0.6 0.8 0.4</size></box></geometry>
            <material><ambient>0.5 0.3 0.1 1</ambient></material>
          </visual>
        </link>
      </model>
    </sdf>"""

    node.spawn('table', table_xml)

    # Spawn 3 colored baskets at different positions
    node.spawn('basket_red',   node.make_basket('basket_red',   -0.5, -0.3, 0.8, 0.1, 0.1))
    node.spawn('basket_blue',  node.make_basket('basket_blue',  -0.5,  0.0, 0.1, 0.1, 0.8))
    node.spawn('basket_green', node.make_basket('basket_green', -0.5,  0.3, 0.1, 0.7, 0.1))

    # 6 boxes with slight random offset to simulate scattered positions
    boxes = [
        ('box_red_1',   0.45 + random.uniform(-0.03, 0.03),  0.15 + random.uniform(-0.03, 0.03), 0.43, 1, 0, 0),
        ('box_red_2',   0.55 + random.uniform(-0.03, 0.03), -0.15 + random.uniform(-0.03, 0.03), 0.43, 1, 0, 0),
        ('box_blue_1',  0.40 + random.uniform(-0.03, 0.03),  0.00 + random.uniform(-0.03, 0.03), 0.43, 0, 0, 1),
        ('box_blue_2',  0.60 + random.uniform(-0.03, 0.03),  0.20 + random.uniform(-0.03, 0.03), 0.43, 0, 0, 1),
        ('box_green_1', 0.50 + random.uniform(-0.03, 0.03), -0.20 + random.uniform(-0.03, 0.03), 0.43, 0, 1, 0),
        ('box_green_2', 0.55 + random.uniform(-0.03, 0.03),  0.05 + random.uniform(-0.03, 0.03), 0.43, 0, 1, 0),
    ]

    for name, x, y, z, r, g, b in boxes:
        node.spawn(name, node.make_box(name, x, y, z, r, g, b))

    node.get_logger().info('🎉 All objects spawned!')
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
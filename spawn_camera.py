import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SpawnEntity

class SpawnCamera(Node):
    def __init__(self):
        super().__init__('spawn_camera')
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

def main(args=None):
    rclpy.init(args=args)
    node = SpawnCamera()

    # Fixed overhead camera — 1.5m above table center, pointing straight down
    camera_xml = """
    <sdf version='1.6'>
      <model name='overhead_camera'>
        <pose>0.6 0.0 1.5 0 1.5707 0</pose>
        <static>true</static>
        <link name='link'>
          <visual name='visual'>
            <geometry><box><size>0.05 0.05 0.05</size></box></geometry>
            <material><ambient>0 0 0 1</ambient></material>
          </visual>
          <sensor type='camera' name='overhead_camera'>
            <always_on>true</always_on>
            <update_rate>15</update_rate>
            <visualize>true</visualize>
            <camera>
              <horizontal_fov>1.5708</horizontal_fov>
              <image>
                <width>1280</width>
                <height>960</height>
                <format>R8G8B8</format>
              </image>
              <clip>
                <near>0.1</near>
                <far>10.0</far>
              </clip>
            </camera>
            <plugin name='overhead_camera_controller' filename='libgazebo_ros_camera.so'>
              <ros>
                <namespace>/overhead_camera</namespace>
                <remapping>image_raw:=image_raw</remapping>
                <remapping>camera_info:=camera_info</remapping>
              </ros>
              <camera_name>overhead_camera</camera_name>
              <frame_name>overhead_camera_frame</frame_name>
            </plugin>
          </sensor>
        </link>
      </model>
    </sdf>"""

    node.spawn('overhead_camera', camera_xml)
    node.get_logger().info('Overhead camera spawned at 1.5m above table!')
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

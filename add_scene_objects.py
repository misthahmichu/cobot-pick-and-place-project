import rclpy
from rclpy.node import Node
from moveit_msgs.msg import PlanningScene, CollisionObject
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose
import time

class SceneObjects(Node):
    def __init__(self):
        super().__init__('scene_objects')
        self.scene_pub = self.create_publisher(
            PlanningScene, '/planning_scene', 10)

    def add_objects(self):
        scene = PlanningScene()
        scene.is_diff = True

        objects = [
            # name,         x,    y,     z,     sx,   sy,   sz
            # Table: size 0.6x0.8x0.4, center at z=0.20 → top at z=0.40
            ('table',       0.6,  0.0,   0.10,  0.6,  0.7,  0.2),
            # Basket: size 0.4x0.4x0.1, center at z=0.05 → top at z=0.10
            ('basket',      0.0, -0.6,   0.05,  0.4,  0.4,  0.1),
            # Boxes: size 0.05x0.05x0.05, center at z=0.225 → top at z=0.25
            ('box_red_1',   0.45,  0.15, 0.225, 0.05, 0.05, 0.05),
            ('box_red_2',   0.55, -0.15, 0.225, 0.05, 0.05, 0.05),
            ('box_blue_1',  0.40,  0.00, 0.225, 0.05, 0.05, 0.05),
            ('box_blue_2',  0.60,  0.20, 0.225, 0.05, 0.05, 0.05),
            ('box_green_1', 0.50, -0.20, 0.225, 0.05, 0.05, 0.05),
            ('box_green_2', 0.55,  0.05, 0.225, 0.05, 0.05, 0.05),
        ]

        for name, x, y, z, sx, sy, sz in objects:
            obj = CollisionObject()
            obj.header.frame_id = 'base_link'
            obj.id = name
            shape = SolidPrimitive()
            shape.type = SolidPrimitive.BOX
            shape.dimensions = [sx, sy, sz]
            pose = Pose()
            pose.position.x = x
            pose.position.y = y
            pose.position.z = z
            pose.orientation.w = 1.0
            obj.primitives.append(shape)
            obj.primitive_poses.append(pose)
            obj.operation = CollisionObject.ADD
            scene.world.collision_objects.append(obj)

        for i in range(5):
            self.scene_pub.publish(scene)
            time.sleep(0.5)
        self.get_logger().info('✅ All objects added to RViz!')

def main(args=None):
    rclpy.init(args=args)
    node = SceneObjects()
    time.sleep(1.0)
    node.add_objects()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

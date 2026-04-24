import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np
import json

CAMERA_HEIGHT_ABOVE_TABLE = 0.65
FOV_H_RAD = 1.2217
IMG_W     = 640
IMG_H     = 480
SCALE     = (2.0 * CAMERA_HEIGHT_ABOVE_TABLE * np.tan(FOV_H_RAD / 2.0)) / IMG_W
CX        = IMG_W / 2.0
CY        = IMG_H / 2.0
BOX_Z     = 0.425

COLOR_RANGES = {
    'red': [
        (np.array([0,   120,  70]),  np.array([10,  255, 255])),
        (np.array([170, 120,  70]),  np.array([180, 255, 255])),
    ],
    'blue': [
        (np.array([100, 150,  50]),  np.array([130, 255, 255])),
    ],
    'green': [
        (np.array([40,  60,   50]),  np.array([80,  255, 255])),
    ],
}

MIN_BOX_AREA = 150
MAX_BOX_AREA = 8000


class WristCameraDetector(Node):
    def __init__(self):
        super().__init__('wrist_camera_detector')
        self.bridge = CvBridge()
        self.camera_world_x = None
        self.camera_world_y = None

        self.image_sub = self.create_subscription(
            Image, '/overhead_camera/image_raw', self.image_callback, 10)
        self.pose_sub = self.create_subscription(
            String, '/wrist_camera/scan_pose', self.pose_callback, 10)
        self.boxes_pub = self.create_publisher(String, '/detected_boxes', 10)
        self.debug_pub = self.create_publisher(Image, '/wrist_camera/debug', 10)

        self.get_logger().info('Wrist Camera Detector Ready!')

    def pose_callback(self, msg):
        try:
            data = json.loads(msg.data)
            self.camera_world_x = data['x']
            self.camera_world_y = data['y']
            self.get_logger().info(
                f'Scan pose set: x={self.camera_world_x:.3f} y={self.camera_world_y:.3f}')
        except Exception as e:
            self.get_logger().error(f'Pose parse error: {e}')

    def pixel_to_world(self, px, py):
        if self.camera_world_x is None:
            return None, None
        wx = self.camera_world_x - (py - CY) * SCALE
        wy = self.camera_world_y - (px - CX) * SCALE
        return round(wx, 3), round(wy, 3)

    def detect_color_mask(self, hsv, color):
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for (lo, hi) in COLOR_RANGES[color]:
            mask |= cv2.inRange(hsv, lo, hi)
        k = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  k)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
        return mask

    def find_boxes(self, mask, color, debug_img):
        detections = []
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        draw_color = {'red': (0,0,255), 'blue': (255,100,0), 'green': (0,200,0)}[color]
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < MIN_BOX_AREA or area > MAX_BOX_AREA:
                continue
            M = cv2.moments(cnt)
            if M['m00'] == 0:
                continue
            px = int(M['m10'] / M['m00'])
            py = int(M['m01'] / M['m00'])
            wx, wy = self.pixel_to_world(px, py)
            if wx is None:
                continue
            detections.append({'color': color, 'x': wx, 'y': wy, 'z': BOX_Z})
            cv2.drawContours(debug_img, [cnt], -1, draw_color, 2)
            cv2.circle(debug_img, (px, py), 6, draw_color, -1)
            cv2.putText(debug_img, f'{color}({wx:.2f},{wy:.2f})',
                        (px-40, py-10), cv2.FONT_HERSHEY_SIMPLEX, 0.38, draw_color, 1)
        return detections

    def image_callback(self, msg):
        if self.camera_world_x is None:
            return
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'CV Bridge error: {e}')
            return
        hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
        debug_img = cv_img.copy()
        all_detections = []
        for color in ['red', 'blue', 'green']:
            mask  = self.detect_color_mask(hsv, color)
            boxes = self.find_boxes(mask, color, debug_img)
            all_detections.extend(boxes)
        if all_detections:
            counts = {c: sum(1 for d in all_detections if d['color']==c)
                      for c in ['red','blue','green']}
            self.get_logger().info(
                f'Detected → red:{counts["red"]} blue:{counts["blue"]} green:{counts["green"]}')
        out = String()
        out.data = json.dumps(all_detections)
        self.boxes_pub.publish(out)
        try:
            self.debug_pub.publish(
                self.bridge.cv2_to_imgmsg(debug_img, encoding='bgr8'))
        except Exception as e:
            self.get_logger().error(f'Debug image error: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = WristCameraDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

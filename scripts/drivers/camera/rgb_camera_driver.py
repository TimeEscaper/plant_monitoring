from .camera_driver_base import AbstractCameraDriver

import time
import cv2


"""
Ordinary RGB web camera driver.
"""
class RGBCameraDriver(AbstractCameraDriver):
    def __init__(self, camera_device):
        super(RGBCameraDriver, self).__init__()
        self.camera_device_ = camera_device

    def is_rgb_supported(self):
        return True

    def is_depth_supported(self):
        return True

    def take_rgb_image(self, file_name, image_size, focus_skip_count=0):
        # Get OpenCV camera object
        cam = cv2.VideoCapture(self.camera_device_)
        if not cam.isOpened():
            raise RuntimeError("Unable to open camera " + self.camera_device_)

        # Set image size
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, image_size[0])
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, image_size[1])

        # Take some time for camera initialization
        time.sleep(1)

        captured_image = None

        # Take focus_skip_count images for focus initialization
        # and additional 3 images for other camera initialization
        for i in range(focus_skip_count+3):
            ret, captured_image = cam.read()
            if not ret:
                captured_image = None

        if captured_image is None:
            raise RuntimeError("Unable to take photo from camera " + self.camera_device_)

        # Save image and release camera
        cv2.imwrite(file_name, captured_image)
        cam.release()

    def take_depth_image(self, file_name, image_size):
        raise RuntimeError("Depth image is not supported")

    def take_point_cloud(self, file_name):
        raise RuntimeError("Point cloud is not supported")

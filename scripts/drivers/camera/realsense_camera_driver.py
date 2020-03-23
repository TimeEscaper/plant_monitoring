from .camera_driver_base import AbstractCameraDriver

import pyrealsense2 as rs
import numpy as np
import cv2


class RealsenseCameraDriver(AbstractCameraDriver):
    def __init__(self, camera_serial_number):
        super(RealsenseCameraDriver, self).__init__()
        self.camera_serial_number_ = camera_serial_number

    """
    Initializes Realsense pipeline.
    :param image_size Size of the image, ignored if rgb_only is depth_enabled=True.
    :param rgb_enabled If RGB mode is enabled
    :param depth_enabled If depth mode is enabled.
    """
    def init_pipeline_(self, image_size, rgb_enabled, depth_enabled):
        # Realsense camera configuration
        config = rs.config()
        config.enable_device(self.camera_serial_number_)
        if not depth_enabled:
            config.enable_stream(rs.stream.color, image_size[0], image_size[1], rs.format.bgr8, 30)
        else:
            if rgb_enabled:
                config.enable_stream(rs.stream.depth, 640, 480, rs.format.bgr8, 30)
            config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        # Realsense camera working pipeline
        rs_pipeline = rs.pipeline()
        try:
            rs_pipeline.start(config)
        except Exception as e:
            raise RuntimeError("Unable to initialize Realsense camera " + self.camera_serial_number_)

        return rs_pipeline


    def is_rgb_supported(self):
        return True

    def is_depth_supported(self):
        return True

    def is_point_cloud_supported(self):
        return True

    def take_rgb_image(self, file_name, image_size, focus_skip_count=0):
        rs_pipeline = self.init_pipeline_(image_size, True, False)

        color_frame = None

        # Take first focus_skip_count images plus 3 additional to allow camera to focus
        for i in range(0, focus_skip_count+3):
            try:
                frames = rs_pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()
            except Exception as e:
                rs_pipeline.stop()
                raise RuntimeError("Error while capturing from " + self.camera_serial_number_ + ": " + str(e))

        if color_frame is None:
            rs_pipeline.stop()
            raise RuntimeError("Unable to capture color frame from Realsense camera " + self.camera_serial_number_)

        # Convert Realsense color frame to image
        color_image = np.asanyarray(color_frame.get_data())
        cv2.imwrite(file_name, color_image)

        rs_pipeline.stop()

    def take_depth_image(self, file_name, image_size):
        rs_pipeline = self.init_pipeline_(image_size, False, True)

        depth_frame = None

        # Take first 3 photos to allow camera to initialize
        for i in range(0, 3):
            try:
                frames = rs_pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
            except Exception as e:
                rs_pipeline.stop()
                raise RuntimeError("Error while capturing from " + self.camera_serial_number_ + ": " + str(e))

        if depth_frame is None:
            rs_pipeline.stop()
            raise RuntimeError("Unable to capture depth frame from Realsense camera " + self.camera_serial_number_)

        # Convert Realsense depth frame to image
        depth_image = cv2.applyColorMap(cv2.convertScaleAbs(
            np.asanyarray(depth_frame.get_data()), alpha=0.03), cv2.COLORMAP_JET)
        cv2.imwrite(file_name, depth_image)

        rs_pipeline.stop()

    def take_point_cloud(self, file_name):
        rs_pipeline = self.init_pipeline_(None, True, True)

        color_frame = None
        depth_frame = None

        # Take first 3 photos to allow camera to initialize
        for i in range(0, 3):
            try:
                frames = rs_pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()
                depth_frame = frames.get_depth_frame()
            except Exception as e:
                rs_pipeline.stop()
                raise RuntimeError("Error while capturing from " + self.camera_serial_number_ + ": " + str(e))

        if color_frame is None or depth_frame is None:
            rs_pipeline.stop()
            raise RuntimeError("Unable to capture frames from Realsense camera " + self.camera_serial_number_)

        # Process point cloud
        pc = rs.pointcloud()
        pc.map_to(color_frame)
        points = pc.calculate(depth_frame)
        points.export_to_ply(file_name, color_frame)

        rs_pipeline.stop()



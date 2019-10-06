# Based on examples:
# https://github.com/IntelRealSense/librealsense/blob/master/wrappers/python/examples/opencv_viewer_example.py

import pyrealsense2 as rs
import numpy as np
import cv2
import datetime

from pathlib import Path


def save_depth_image(depth_frame, output_file):
    depth_image = np.asanyarray(depth_frame.get_data())
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    cv2.imwrite(output_file, depth_colormap)


def save_rgb_image(color_frame, output_file):
    color_image = np.asanyarray(color_frame.get_data())
    cv2.imwrite(output_file, color_image)


def run_realsense_camera(configuration):
    storage_directory_str = str(configuration["storage_dir"])
    if storage_directory_str.startswith("$HOME/"):
        storage_directory = Path.home() / storage_directory_str.strip("$HOME/")
    else:
        storage_directory = Path(storage_directory_str)

    config = rs.config()

    depth_enabled = False
    rgb_enabled = False
    for camera_config in configuration["realsense_camera"]:
        output_type = str(camera_config["type"])
        if output_type == "depth":
            depth_enabled = True
            depth_label = camera_config["label"]
            config.enable_stream(rs.stream.depth, int(camera_config["width"]), int(camera_config["height"]),
                                 rs.format.z16, 30)
        elif output_type == "rgb":
            rgb_enabled = True
            rgb_label = camera_config["label"]
            config.enable_stream(rs.stream.color, int(camera_config["width"]), int(camera_config["height"]),
                                 rs.format.bgr8, 30)
    rs_pipeline = rs.pipeline()
    rs_pipeline.start(config)

    delay_counter = 0

    try:
        while True:
            frames = rs_pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if (depth_enabled and not depth_frame) or (rgb_enabled and not color_frame):
                continue

            # Add some "delay" to let camera to be auto-calibrated
            if delay_counter < 100:
                delay_counter += 1
                continue

            datetime_str = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

            if depth_enabled:
                label_dir = storage_directory / depth_label
                if not label_dir.exists():
                    label_dir.mkdir(parents=True, exist_ok=True)
                image_file = str(label_dir / (depth_label + "_" + datetime_str + ".jpg"))
                save_depth_image(depth_frame, image_file)

            if rgb_enabled:
                label_dir = storage_directory / rgb_label
                if not label_dir.exists():
                    label_dir.mkdir(parents=True, exist_ok=True)
                image_file = str(label_dir / (rgb_label + "_" + datetime_str + ".jpg"))
                save_rgb_image(color_frame, image_file)

            break

    finally:
        rs_pipeline.stop()

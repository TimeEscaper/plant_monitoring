# Based on examples:
# https://github.com/IntelRealSense/librealsense/blob/master/wrappers/python/examples/opencv_viewer_example.py
# https://github.com/IntelRealSense/librealsense/blob/development/wrappers/python/examples/export_ply_example.py

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


def save_point_cloud(color_frame, depth_frame, output_file):
    pc = rs.pointcloud()

    pc.map_to(color_frame)
    points = pc.calculate(depth_frame)

    points.export_to_ply(output_file, color_frame)


def get_file(storage_dir, label, datetime_str, extension):
    directory = storage_dir / label
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
    return str(directory / (label + "_" + datetime_str + extension))


def run_realsense_camera(configuration):
    storage_directory_str = str(configuration["storage_dir"])
    if storage_directory_str.startswith("$HOME/"):
        storage_directory = Path.home() / storage_directory_str.strip("$HOME/")
    else:
        storage_directory = Path(storage_directory_str)

    config = rs.config()

    camera_config = configuration["realsense_camera"]
    label = str(camera_config["label"])
    width = int(camera_config["width"])
    height = int(camera_config["height"])

    config.enable_stream(rs.stream.depth, width, height, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, 30)

    rs_pipeline = rs.pipeline()
    rs_pipeline.start(config)

    delay_counter = 0

    try:
        while True:
            frames = rs_pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            # Add some "delay" to let camera to be auto-calibrated
            if delay_counter < 100:
                delay_counter += 1
                continue

            datetime_str = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

            depth_file = get_file(storage_directory, label + "_depth", datetime_str, ".jpg")
            rgb_file = get_file(storage_directory, label + "_rgb", datetime_str, ".jpg")
            point_cloud_file = get_file(storage_directory, label + "_point_cloud", datetime_str, ".ply")

            save_depth_image(depth_frame, depth_file)
            save_rgb_image(color_frame, rgb_file)
            save_point_cloud(color_frame, depth_frame, point_cloud_file)

            break

    finally:
        rs_pipeline.stop()

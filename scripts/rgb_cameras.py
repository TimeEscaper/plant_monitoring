#!/usr/bin/env python3

import datetime
import time
import logging
from pathlib import Path

import cv2

from blur_util import is_image_blurred


# Captures the image from specified camera device
def capture_image(camera_device, image_size, output_file):
    cam = cv2.VideoCapture(camera_device)
    if not cam.isOpened():
        raise RuntimeError("Unable to open camera " + camera_device)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, image_size[0])
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, image_size[1])
    time.sleep(1)

    for i in range(0, 5):

        # Try to capture frame 3 times, if can't read correct frame - raise error
        for j in range(0, 3):
            ret, image = cam.read()
            if ret:
                break
        if not ret:
            raise RuntimeError("Unable to capture correct frame on camera " + camera_device)

        blurred = is_image_blurred(image)
        if not blurred:
            break
        time.sleep(0.5)

    cv2.imwrite(output_file, image)
    cam.release()


def run_cameras(configuration):

    storage_directory_str = str(configuration["storage_dir"])
    if storage_directory_str.startswith("$HOME/"):
        storage_directory = Path.home() / storage_directory_str.strip("$HOME/")
    else:
        storage_directory = Path(storage_directory_str)

    # Current datetime string (common for all images)
    datetime_str = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    logger = logging.getLogger('root')

    for camera_config in configuration["rgb_cameras"]:
        label = str(camera_config["label"])
        device = str(camera_config["device"])
        image_width = int(camera_config["width"])
        image_height = int(camera_config["height"])

        label_dir = storage_directory / label
        if not label_dir.exists():
            label_dir.mkdir(parents=True, exist_ok=True)
        image_file = str(label_dir / (label + "_" + datetime_str + ".jpg"))

        try:
            capture_image(device, (image_width, image_height), image_file)
        except RuntimeError as e:
            logger.exception("message")
        else:
            logger.info("Successfully captured image " + image_file)
            pass




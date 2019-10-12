#!/usr/bin/env python3

import datetime
import time
from pathlib import Path

import cv2

from blur_util import is_image_blurred


# Captures the image from specified camera device
def capture_image(camera_device, image_size, output_file):
    cam = cv2.VideoCapture(camera_device)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, image_size[0])
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, image_size[1])
    time.sleep(1)
    for i in range(0, 5):
        ret, image = cam.read()
        blurred = is_image_blurred(image)
        if not blurred:
            break
        print("Image for " + output_file + " got blurred, try again")
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

    for camera_config in configuration["rgb_cameras"]:
        label = str(camera_config["label"])
        device = str(camera_config["device"])
        image_width = int(camera_config["width"])
        image_height = int(camera_config["height"])

        label_dir = storage_directory / label
        if not label_dir.exists():
            label_dir.mkdir(parents=True, exist_ok=True)
        image_file = label_dir / (label + "_" + datetime_str + ".jpg")

        capture_image(device, (image_width, image_height), str(image_file))




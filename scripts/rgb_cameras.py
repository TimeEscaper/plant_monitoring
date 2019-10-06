#!/usr/bin/env python3

# Currently use pygame instead of OpenCV to avoid unnecessary "fat" dependencies
import pygame
import pygame.camera
import sys
import json
import datetime
import os

from pathlib import Path


# Captures the image from specified camera device
def capture_image(camera_device, image_size, output_file):
    cam = pygame.camera.Camera(camera_device, image_size)
    cam.start()
    image = cam.get_image()
    pygame.image.save(image, output_file)
    cam.stop()


def run_cameras(configuration):
    pygame.init()
    pygame.camera.init()

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



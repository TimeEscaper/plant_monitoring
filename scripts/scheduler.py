import atexit
import sys
import os
import logging
import time
import datetime

import json
from pathlib import Path

from apscheduler.schedulers.background import BlockingScheduler

import pandas as pd
import numpy as np
import requests

from rgb_cameras import run_cameras
from light_switcher import switch_light
from realsense_cameras import run_realsense_cameras
from sensors import readMessageFromArduino

need_light_up = False

def parse_configs():
    args = sys.argv
    if len(args) < 2:
        global_config_file = Path(os.path.realpath(__file__)).parent.parent / "config/global.json"
        config_dir = Path(os.path.realpath(__file__)).parent.parent / "config/"
    else:
        global_config_file = args[1]
        # config_dir = args[1][:args[1].rindex("/")]
        pass
    with open(global_config_file) as json_file:
        configuration = json.load(json_file)

    settings = configuration['settings']
    devices = configuration['devices']
    sensors = configuration['sensors']

    with open(config_dir / devices['cameras']) as file:
        cameras_config = json.load(file)
    cameras_config.update(settings['cameras_settings'])

    with open(config_dir / devices['light']) as file:
        light_config = json.load(file)

    run_interval = settings['run_interval_seconds']

    sensors_directory_str = str(sensors["storage_dir"])
    if sensors_directory_str.startswith("$HOME/"):
        sensors_directory = Path.home() / sensors_directory_str.strip("$HOME/")
    else:
        sensors_directory = Path(sensors_directory_str)
    csv = Path(str(sensors["csv_file"]))
    sensors["csv_file"] = str(sensors_directory / csv)

    return {"run_interval": run_interval, "light_config": light_config, "cameras_config": cameras_config,
            "sensors_config": sensors}


def init_logger():
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("plant_monitoring.log")
    file_handler.setFormatter(formatter)

    logger = logging.getLogger('root')

    logger.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger


def write_images_to_csv(cameras_config, rgb_images, realsense_images, logger):

    storage_directory_str = str(cameras_config["storage_dir"])
    if storage_directory_str.startswith("$HOME/"):
        storage_directory = Path.home() / storage_directory_str.strip("$HOME/")
    else:
        storage_directory = Path(storage_directory_str)
    csv_file = storage_directory / cameras_config["csv_file"]

    csv_exists = csv_file.exists()

    if csv_exists:
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            logger.error("Error while trying to read csv file: " + str(e))
            return None
    else:
        df = pd.DataFrame()

    rgb_labels = list()
    realsense_labels = list()
    for cam in cameras_config["rgb_cameras"]:
        rgb_labels.append(cam["label"])
    for cam in cameras_config["realsense_cameras"]:
        realsense_labels.append(cam["label"])

    values = list()
    values.append(datetime.datetime.now())
    for label in rgb_labels:
        if label in rgb_images:
            values.append(rgb_images[label])
        else:
            values.append(None)
    for label in realsense_labels:
        if label in realsense_images:
            values.append(realsense_images[label])
        else:
            values.append(None)

    if not csv_exists:
        df = pd.DataFrame([values], columns=["time"]+rgb_labels+realsense_labels)
    else:
        df = df.append(pd.Series(values, index=df.columns), ignore_index=True)
    df['time'] = df['time'].astype('datetime64[ns]')

    try:
        df.to_csv(csv_file, index=False)
    except Exception as e:
        logger.error("Error while writing to csv file: " + str(e))
        return None
    else:
        logger.info("Successfully wrote images to csv file")

    return str(csv_file)


def run_job_cameras(light_config, cameras_config, sensors_config, logger):
    logger.info("Job started")

    global need_light_up

    # 1. Turn lights on
    lights_on = False
    if need_light_up:
        lights_on = True
        logger.info("Switching light on")
        switch_light(light_config, 'on')
        time.sleep(1)

    # 2. Turn cameras on and take photos
    logger.info("Starting capture images")
    rgb_images = dict()
    realsense_images = dict()
    try:
        rgb_images = run_cameras(cameras_config)
        realsense_images = run_realsense_cameras(cameras_config)
    except Exception as e:
        logger.error("Error while capturing from cameras: " + str(e))

    csv_file = write_images_to_csv(cameras_config, rgb_images, realsense_images, logger)
    time.sleep(1)

    # 3. Turn lights off
    if lights_on:
        logger.info("Switching light off")
        switch_light(light_config, 'off')

    # 4. Upload csv files to server
    if csv_file is not None:
        logger.info("Starting to upload cameras file to server")
        try:
            files = {'upload_file': open(csv_file, 'rb')}
            response = requests.post("http://spp.pythonanywhere.com/upload/csv/cameras", files=files)
            if response.status_code != 200:
                logger.error("Error while uploading cameras csv file: status code " + str(response.status_code))
            else:
                logger.info("Successfully uploaded cameras csv file")
        except Exception as e:
            logger.error("Error while uploading cameras csv file: " + str(e))

    csv_file = Path(sensors_config["csv_file"])
    if csv_file.exists():
        logger.info("Starting to upload sensors file to server")
        try:
            files = {'upload_file': open(str(csv_file), 'rb')}
            response = requests.post("http://spp.pythonanywhere.com/upload/csv/sensors", files=files)
            if response.status_code != 200:
                logger.error("Error while uploading sensors csv file: status code " + str(response.status_code))
            else:
                logger.info("Successfully uploaded sensors csv file")
        except Exception as e:
            logger.error("Error while uploading sensors csv file: " + str(e))


def run_job_sensors(sensors_config, logger):
    global need_light_up
    logger.info("Reading message from Arduino")
    need_light_up = readMessageFromArduino(sensors_config)
    logger.info("Light needed: " + str(need_light_up))
    logger.info("Message received")

if __name__ == '__main__':
    settings = parse_configs()

    logger = init_logger()
    logger.info("Script started")

    time.sleep(2)

    scheduler = BlockingScheduler()
    logger.info("Scheduling the job")
    scheduler.add_job(func=(lambda: run_job_cameras(settings["light_config"], settings["cameras_config"], settings["sensors_config"], logger)),
                      trigger="interval", seconds=settings['run_interval'])

    atexit.register(lambda: scheduler.shutdown())
    scheduler.start()

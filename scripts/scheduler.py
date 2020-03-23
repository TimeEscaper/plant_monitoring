from pathlib import Path
import json
import sys
import os
import logging
from queue import Queue
from threading import Thread
import atexit


from apscheduler.schedulers.background import BlockingScheduler

from pipeline import PipelineExecutor
from drivers.i2c import I2CDriver


def parse_configs():
    args = sys.argv
    if len(args) < 2:
        config_dir = Path(os.path.realpath(__file__)).parent.parent / "config/"
    else:
        config_dir = Path(args[1])
        pass

    if not config_dir.is_dir():
        raise RuntimeError("Wrong configuration directory!")

    # Parse cameras configuration file
    cameras_config = None
    with open(str(config_dir / "cameras.json"), "r") as read_file:
        cameras_config = json.load(read_file)
    cameras = dict()
    for camera in cameras_config:
        cameras[camera["id"]] = camera

    # Parse light configuration file
    light_config = None
    with open(str(config_dir / "light.json"), "r") as read_file:
        light_config = json.load(read_file)
    light = dict()
    for light_it in light_config:
        light[light_it["id"]] = light_it

    # Parse project
    project = None
    with open(str(config_dir / "project.json"), "r") as read_file:
        project = json.load(read_file)

    return cameras, light, project


def main():
    log = logging.getLogger("main")
    cameras, light, project = parse_configs()

    storage_dir = Path(project["storage_dir"])
    if not storage_dir.is_dir():
        storage_dir.mkdir(parents=True)

    # We will use queue to connect scheduler thread with I2C communication thread
    connection_queue = Queue()

    # Create separate thread for I2C communication
    log.info("Starting I2C thread")
    i2c_driver = I2CDriver(0x04)
    i2c_thread = Thread(target=i2c_thread_function, args=(i2c_driver, connection_queue))
    i2c_thread.start()

    log.info("Running pipeline for the first time")
    pipeline_executor = PipelineExecutor(storage_dir, cameras, light, connection_queue, project["pipeline"])

    # For the first time, execute pipeline manually, then schedule it
    pipeline_executor.execute()

    # Create a scheduler and add job to it
    log.info("Scheduling the pipeline")
    scheduler = BlockingScheduler()
    scheduler.add_job(func=(lambda executor=pipeline_executor: executor.execute()),
                      trigger="interval",
                      seconds=project['run_interval_seconds'])
    atexit.register(lambda: scheduler.shutdown())
    scheduler.start() # Blocks thread


"""
Separate I2C thread function.
Reads messages from queue (in blocking mode) and sends them vis I2C.
"""
def i2c_thread_function(driver, queue):
    logger = logging.getLogger("main.I2C_Thread")
    while True:
        message = queue.get(block=True)
        if message is None:
            continue
        try:
            driver.send_message(message)
        except Exception as e:
            logger.error(str(e))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    try:
        main()
    except Exception as e:
        logging.error(str(e))

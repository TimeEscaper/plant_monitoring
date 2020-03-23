import logging
import time
from datetime import datetime
from pathlib import Path

from drivers.light import LightDriver
from drivers.camera import RGBCameraDriver, RealsenseCameraDriver


"""
Executes tasks in pipeline.
"""
class PipelineExecutor:
    """
    :param storage_dir A pathlib Path to photos and etc. storage dir.
    :param rgb_cameras A dict with RGB cameras configs.
    :param realsense_cameras A dict with Realsense cameras configs.
    :param lights A dict with light configs.
    :param hardware_interface_queue A queue to hardware interface thread.
    :param pipeline_tasks An array with dict-like tasks.
    """
    def __init__(self, storage_dir, cameras, lights, hardware_interface_queue, pipeline_tasks):
        self.storage_dir_ = storage_dir
        self.cameras_ = cameras
        self.lights_ = lights
        self.hardware_queue_ = hardware_interface_queue
        self.pipeline_tasks_ = pipeline_tasks
        self.log_ = logging.getLogger("pipeline.PipelineExecutor")

    def execute(self):
        # Obtain current datetime and make file names postfix
        current_datetime = datetime.now()
        datetime_prefix = current_datetime.strftime("%m_%d_%H_%M")

        # Execute task by task
        for task in self.pipeline_tasks_:
            try:
                self.execute_task_(task, datetime_prefix)
            except Exception as e:
                self.log_.error(str(e))

    def execute_task_(self, task, datetime_prefix):
        task_type = task["task_type"]
        if task_type is None:
            self.log_.warning("Empty task type!")
        elif task_type == "delay":
            time.sleep(task["interval_seconds"])
        elif task_type == "light_on":
            self.execute_lights_(task, True)
        elif task_type == "light_off":
            self.execute_lights_(task, False)
        elif task_type == "rgb_photo":
            self.execute_rgb_photo_(task, datetime_prefix)
        elif task_type == "depth_photo":
            self.execute_depth_photo_(task, datetime_prefix)
        elif task_type == "point_cloud":
            self.execute_point_cloud_(task, datetime_prefix)

    def execute_lights_(self, task, enable):
        driver = LightDriver(self.hardware_queue_)
        for light_id in task["light_ids"]:
            if light_id not in self.lights_:
                self.log_.warning("Unknown light ID: " + light_id)
                continue
            if enable:
                driver.light_on(self.lights_[light_id]["pin"])
            else:
                driver.light_off(self.lights_[light_id]["pin"])

    def execute_rgb_photo_(self, task, datetime_prefix):
        for camera_id in task["camera_ids"]:
            if camera_id not in self.cameras_:
                self.log_.warning("Unknown camera ID: " + camera_id)
                continue
            camera = self.cameras_[camera_id]

            # Create camera driver depending on camera type
            driver = None
            camera_type_postfix = None
            if camera["type"] == "rgb":
                driver = RGBCameraDriver(camera["device"])
                camera_type_postfix = "rg"
            elif camera["type"] == "realsense":
                driver = RealsenseCameraDriver(camera["serial_number"])
                camera_type_postfix = "3d"
            else:
                self.log_.warning("Unsupported camera type for RGB images")
                continue

            filename = datetime_prefix + "_" + camera_type_postfix
            if task["filename_postfix"] is not None:
                filename = filename + "_" + task["filename_postfix"]
            filename = self.storage_dir_ / (filename + ".jpg")
            focus_skip = 0 if camera["focus_skip"] is None else camera["focus_skip"]

            try:
                driver.take_rgb_image(str(filename), (camera["width"], camera["height"]), focus_skip_count=focus_skip)
                self.log_.info("Successfully took image " + str(filename))
            except Exception as e:
                self.log_.error(str(e))

    def execute_depth_photo_(self, task, datetime_prefix):
        for camera_id in task["camera_ids"]:
            if camera_id not in self.cameras_:
                self.log_.warning("Unknown camera ID: " + camera_id)
                continue
            camera = self.cameras_[camera_id]

            # Create camera driver depending on camera type
            driver = None
            camera_type_postfix = None
            if camera["type"] == "realsense":
                driver = RealsenseCameraDriver(camera["serial_number"])
                camera_type_postfix = "depth"
            else:
                self.log_.warning("Unsupported camera type for depth images")
                continue

            filename = datetime_prefix + "_" + camera_type_postfix
            if task["filename_postfix"] is not None:
                filename = filename + "_" + task["filename_postfix"]
            filename = self.storage_dir_ / (filename + ".jpg")

            try:
                driver.take_depth_image(str(filename), (camera["width"], camera["height"]))
                self.log_.info("Successfully took depth image " + str(filename))
            except Exception as e:
                self.log_.error(str(e))

    def execute_point_cloud_(self, task, datetime_prefix):
        for camera_id in task["camera_ids"]:
            if camera_id not in self.cameras_:
                self.log_.warning("Unknown camera ID: " + camera_id)
                continue
            camera = self.cameras_[camera_id]

            # Create camera driver depending on camera type
            driver = None
            camera_type_postfix = None
            if camera["type"] == "realsense":
                driver = RealsenseCameraDriver(camera["serial_number"])
                camera_type_postfix = "point_cloud"
            else:
                self.log_.warning("Unsupported camera type for point cloud")
                continue

            filename = datetime_prefix + "_" + camera_type_postfix
            if task["filename_postfix"] is not None:
                filename = filename + "_" + task["filename_postfix"]
            filename = self.storage_dir_ / (filename + ".ply")

            try:
                driver.take_point_cloud(str(filename))
                self.log_.info("Successfully took point cloud " + str(filename))
            except Exception as e:
                self.log_.error(str(e))

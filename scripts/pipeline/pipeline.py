import logging
import time
from pathlib import Path


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
    def __init__(self, storage_dir, rgb_cameras, realsense_cameras, lights, hardware_interface_queue, pipeline_tasks):
        self.storage_dir_ = storage_dir
        self.rgb_cameras_ = rgb_cameras
        self.realsense_cameras_ = realsense_cameras
        self.lights_ = lights
        self.hardware_queue_ = hardware_interface_queue
        self.pipeline_tasks_ = pipeline_tasks
        self.log_ = logging.getLogger("pipeline.PipelineExecutor")

    def execute(self):
        for task in self.pipeline_tasks_:
            try:
                self.execute_task_(task)
            except Exception as e:
                self.log_.error(str(e))

    def execute_task_(self, task):
        task_type = task["task_type"]
        if task_type is None:
            self.log_.warning("Empty task type!")
        elif task_type is "delay":
            time.sleep(task["interval_seconds"])
        elif task_type is "light_on":
            self.execute_lights_on_(task)
        elif task_type is "light_off":
            self.execute_lights_off_(task)
        elif task_type is "rgb_photo":
            self.execute_rgb_photo_(task)
        elif task_type is "depth_photo":
            self.execute_depth_photo_(task)
        elif task_type is "point_cloud":
            self.execute_point_cloud_(task)

    def execute_lights_on_(self, task):
        # TODO: Implement
        pass

    def execute_lights_off_(self, task):
        # TODO: Implement
        pass

    def execute_rgb_photo_(self, task):
        # TODO: Implement
        pass

    def execute_depth_photo_(self, task):
        # TODO: Implement
        pass

    def execute_point_cloud_(self, task):
        # TODO: Implement
        pass

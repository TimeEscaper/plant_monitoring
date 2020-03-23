# plant_monitoring
Plant growth monitoring project.

- - -
## Dependencies
Project is designed to be run with Python 3.6+.

Project requires following system-wide dependencies:
* OpenCV 3.4+
* RealSense Drivers and SDK (see [Linux installation guide](https://github.com/IntelRealSense/librealsense/blob/master/doc/distribution_linux.md))

Required Python packages specified in *requirements.txt*.
- - -

## Usage

### Running the code
The system is designed to schedule plant monitoring tasks. The system can be run with command: `python3 scripts/scheduler.py`. To run system in background, `nohup` can be used: `nohup python3 scripts/scheduler.py &`. By default, the pipeline and devices configurations will be read from *config/* directory in this repository.

### Configurations
Currently, the configurations consist of 3 parts: *cameras configurations*, *light configurations*, *project configuration with pipeline*.

#### Cameras configurations
Cameras configurations are stored in file *cameras.json* in configurations directory. It is a JSON array that has following structure:
```json
[
    {
      "id": "bl",
      "type": "rgb",
      "device": "/dev/video0",
      "width": 1920,
      "height": 1080,
      "focus_skip": 30
    },
    {
      "id": "tm",
      "type": "realsense",
      "serial_number": "627204004931",
      "width": 1920,
      "height": 1080,
      "focus_skip": 30
    }
]
```

Currently, the ordinary RGB web cameras and Intel RealSense 3D cameras are supported. The fields in configurations are following:
* *id* - a unique identifier of the camera
* *type* - type of the camera: *rgb* or *realsense*
* *device* - path to Linux device of the camera, only for RGB web cameras
* *serial_number* - serial number of the RealSense camera, only for the RealSense cameras
* *width*, *height* - size of the output RGB image, for depth image the size is fixed
* *focus_skip* - number of the first skipped images to let camera to focus, optional

#### Light configuration
Light configurations are stored in file *light.json* in configurations directory. It is a JSON array that has following structure:
```json
[
	{
		"id": "phyto",
		"pin": 1
	},
	{
		"id": "led_tape_1",
		"pin": 2
	}
]
```
Currently, the design assumes that the light is controled by external board that is connected to Raspberry Pi over I2C interface. The fields in configurations are following:
* *id* - a unique identifier of the light device
* *pin* - pin of the external board to which this light device is connected to

#### Project and pipeline configuration
Porject configurations are stored in file *project.json* in configurations directory. It is a JSON array that has following structure:
```json
{
  "name": "plant_photos",
  "storage_dir": "/home/sibirsky/plant_photos_test",
  "run_interval_seconds": 1800,

  "pipeline": [
    {
      "task_type": "light_off",
      "light_ids": ["phyto"],
      "only_if_was_enabled": true
    },
    {
      "task_type": "light_on",
      "light_ids": ["alarm_led"]
    },
    {
      "task_type": "delay",
      "interval_seconds": 10
    },
    {
      "task_type": "rgb_photo",
      "camera_ids": ["bl", "ml", "mr", "br", "tm"],
      "filename_postfix": "1"
    },
    {
      "task_type": "light_off",
      "light_ids": ["alarm_led"]
    },
    {
      "task_type": "light_off",
      "light_ids": ["phyto"],
      "only_if_was_enabled": true
    }
  ]
}
```
The commond fields are following:
* *name* - name of the project
* *storage_dir* - path to the directory where to store output photos and etc.
* *run_interval_seconds* - an interval of repeating the pipeline

The pipeline is defined in the field *pipeline*. It is the array that represents the sequence of tasks. The tasks syntax was tried to be designed as self-explained. For now, the following tasks are supported:
* *light_on* / *light_off* - switches on / off the light. IDs of the lights are imported from light configurations.
    * *only_if_was_enabled* - an optional field that tells that light shouldn't be switched on/off it was switched off before this pipeline was executed.
* *delay* - a simple analog to *sleep* function
* *rgb_photo* - take a set of RGB photos. Camera IDs are imported from cameras configuration.
    * *filename_postfix* - an optional filename postfix for photos that was taken during this task
* *depth_photo* - take a set of depth images. Syntax is analog to *rgb_photo* task.
* *point_cloud* - take a set of point clouds. Syntax is analog to *rgb_photo* task. Point clouds are stored in *.ply* files.
---

## Project architecture and structure
The project is designed to be modular and as reusable as possible. The main parts of the project are:
* *drivers* - a package that contains driver abstractions for different devices: different types of cameras, default light driver, I2C driver with pre-defined communication protocol and etc.
* *pipeline* - an implementation of the tasks pipeline execution
* *scheduler.py* - entry point of the program, reads configs and schedules tasks using the *Advanced Python Scheduler (APS)* package.

An important moment is the threading model. Currently, two threads are used:
* The main thread that is occupied by *Blocking scheduler* (see APS docs)
* A separate thread for communication with external board over I2C. Communication with this thread is implemented using queue.

In order to add new device and functionality support, the developer should:
* Create a driver in *drivers* package for it
* Implement specific tasks *pipeline.PipelineExecutor*
* Update configs parsing if it is needed
---
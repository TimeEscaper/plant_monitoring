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
A script *run_system.py* is main and executed on a call of a scheduler. It reads global config file *global.json* from *./config* and runs a sequence of operations, i.e. turn on light, take a shot, turn off light, etc.

To add $run_system.py$ to scheduler (*cron*), run *chmod +x init.sh && sudo ./init.sh*. The script sets new environment variable *PLANT_MONITOR_DIR* to current path and adds new tasks to */etc/crontab*.

Config file *global.json* contains settings of project modules and a list of devices that are used in monitoring system. 

```
{
	"settings": {
		"cameras_settings": {
			"storage_dir": "plant_monitoring_images/"
		},
		"light_settings": {
			"literally": "something"
		}
	}, 
	"devices" : {
		"cameras": "cameras.json",
		"light": "light.json"
	}
}
```
*Settings* field contains settings for each device. *Devices* field contains a list of *.json* configuration files for each device. All config files are to be in the same folder with *global.json*.

## Working with RGB cameras
Scripts *rgb_cameras.py* and *realsense_cameras.py* are responsible for capturing images from standard RGB cameras and RealSense cameras. They take as input a config from *cameras.json* merged with settings from *global.json*.

Cameras configuration file is a *.json* file with following  structure:
```json
{
  "rgb_cameras": [
    {
      "label": "label of the first camera",
      "device": "first camera device",
      "width": 640,
      "height": 480
    },
    {
      "label": "label of the Nth camera",
      "device": "Nth camera device",
      "width": 1280,
      "height": 720
    }
  ],
  "realsense_cameras": [
    {
      "label": "realsense_1",
      "serial_no": "Serial number (can be obtained from realsense-viewer",
      "width": 640,
      "height": 480,
      "point_cloud_enabled": false
    },
    {
      "label": "realsense_M",
      "serial_no": "Serial number (can be obtained from realsense-viewer",
      "width": 1280,
      "height": 720,
      "point_cloud_enabled": true
    }
  ]
}
```
Images from RGB cameras will be stored using following schema: 
*<storage_dir>/\<label>/\<label>_<current_datetime>.jpg*

RGB images, depth map images and point clouds can be obtained using RealSense cameras. Files will be stored using following schema:
*<storage_dir>/\<label>_rgb/\<label>_rgb\_<current_datetime>.jpg*
*<storage_dir>/\<label>_depth/\<label>_depth\_<current_datetime>.jpg*
*<storage_dir>/\<label>_point_cloud/\<label>_point\_cloud\_<current_datetime>.ply*
- - -

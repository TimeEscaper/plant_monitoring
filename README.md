# plant_monitoring
Plant growth monitoring project.

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
Script *rgb_cameras.py* is responsible for capturing images from standard RGB cameras. It takes as input a config from *cameras.json* merged with settings from *global.json*.

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
  ]
}
```
Images will be stored using following schema: 
*<storage_dir>/\<label>/\<label>_<current_datetime>.jpg*

- - -

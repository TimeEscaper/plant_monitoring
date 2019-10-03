# plant_monitoring
Plant growth monitoring project

- - -

## Working with RGB cameras
Script *rgb_cameras.py* is responsible for capturing images from standard RGB cameras. You can run it using command:
```shell script
python3 rgb_cameras.py <path-to-configuration-file>
```
By default, file *cameras_default.json* in the same directory with script is used.

Cameras configuration file is a *.json* file with following  structure:
```json
{
  "storage_dir": "path to common storage directory for images",
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

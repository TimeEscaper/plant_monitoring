import sys
import os

import json
from pathlib import Path

from rgb_cameras import run_cameras
from light_switcher import switch_light
from realsense_cameras import run_realsense_cameras

if __name__ == '__main__':
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

    with open(config_dir / devices['cameras']) as file:
        cameras_config = json.load(file)
    cameras_config.update(settings['cameras_settings'])

    with open(config_dir / devices['light']) as file:
        light_config = json.load(file)
    light_config.update(settings['light_settings'])

    # 1. Turn lights on
    switch_light(light_config, 'on')

    # 2. Turn cameras on and take photos
    run_cameras(cameras_config)
    run_realsense_cameras(cameras_config)

    # 3. Turn lights off
    switch_light(light_config, 'off')
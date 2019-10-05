#!/usr/bin/bash

export PLANT_MONITOR_DIR=$(pwd)
cat $PLANT_MONITOR_DIR/crontab | tee -a /etc/crontab


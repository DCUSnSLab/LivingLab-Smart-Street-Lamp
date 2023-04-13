#!/bin/sh
G_PATH=`pwd -P`
echo $G_PATH
export PYTHONPATH=$PYTHONPATH:/$G_PATH
cd /home/pi/LivingLab-Smart-Street-Lamp
pwd
echo $PYTHONPATH
python3 ./gateway/ota/lampOTA.py

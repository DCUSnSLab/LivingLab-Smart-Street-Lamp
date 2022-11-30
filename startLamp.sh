#!/bin/sh
G_PATH=`pwd -P`
echo $G_PATH
export PYTHONPATH=$PYTHONPATH:/$G_PATH
python3 ./gateway/ota/lampOTA.py

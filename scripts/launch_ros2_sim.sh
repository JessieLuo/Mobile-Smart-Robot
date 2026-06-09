#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch msr_bringup sim_full.launch.py
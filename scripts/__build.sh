#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

source /opt/ros/jazzy/setup.bash

colcon build --symlink-install

echo ""
echo "Build complete."
echo "Run:"
echo "source install/setup.bash"
echo "ros2 launch msr_bringup sim_full.launch.py"
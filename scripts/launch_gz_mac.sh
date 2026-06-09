#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

export GZ_SIM_RESOURCE_PATH="$PWD/src/msr_gazebo/models:$PWD/src/msr_gazebo/worlds"

gz sim -r "$PWD/src/msr_gazebo/worlds/sorting_room.sdf"
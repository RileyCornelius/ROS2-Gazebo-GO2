#!/usr/bin/env bash

set -eo pipefail

WORKSPACE_DIR="${WORKSPACE:-/workspaces/ROS2-Gazebo-GO2}"

source /opt/ros/${ROS_DISTRO}/setup.bash
cd "${WORKSPACE_DIR}"

# Clean up previous build artifacts
rm -rf build install log 

# Install dependencies and build the workspace
rosdep update
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install

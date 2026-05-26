<h1 align="center">Go2 Gazebo Sim</h1>

<p align="center">
  <img src="https://www.unitree.com/images/b5fffd3e4fc04e6f9fcafedb9516b341_3840x2146.jpg" alt="Unitree Go2" width="720">
</p>

# 1. Project Description
This repository is a ROS2-Gazebo simulation of the Unitree Go2 robot dog. It was built and tested using Ubuntu 22.04 with ROS2 Humble.

This project includes:
- A front monocular camera to simulate the GO2 front camera
- Two LiDAR sensors:
  - A front L1 LiDAR to simulate GO2's built-in LiDAR
  - An external VLP16 LiDAR
- A D435i depth camera

Both LiDARs publish `LaserScan` and `PointCloud2` simultaneously, making mapping and navigation workflows easier.

# 2. Build

## 2.1 Native
Clone the project, then install dependencies and build the workspace:
```bash
cd ROS2-Gazebo-GO2
rosdep update
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
```

## 2.2 Docker

### Manual
```bash
cd ROS2-Gazebo-GO2
docker compose -f .devcontainer/docker-compose.yml up -d --build
docker compose -f .devcontainer/docker-compose.yml exec go2_sim bash
bash .devcontainer/post-install.sh
```

To stop the container:
```bash
docker compose -f .devcontainer/docker-compose.yml down
```

### VS Code Dev Container
Requirements:
- Docker Desktop with this WSL distro enabled under **Settings > Resources > WSL integration**
- VS Code with the **Dev Containers** extension
- Open the repo root folder, not a package subfolder

Run **Dev Containers: Reopen in Container** from the Command Palette. VS Code builds the image, starts the container, and automatically runs `.devcontainer/post-install.sh` via `postCreateCommand`. The script cleans stale artifacts, installs rosdep dependencies, and builds the workspace with colcon.

If you change the Dockerfile, docker-compose, or dependencies, use **Dev Containers: Rebuild Container** instead.

# 3. Run

Source the workspace, then launch the simulation:
```bash
source setup.sh
ros2 launch gazebo_sim launch.py
```

The first launch may take longer because Gazebo downloads required world resources. After a successful launch:

![alt text](images/image-18.png)

Launch with extended sensors in a specific world:
```bash
ros2 launch gazebo_sim launch.py sensors:=true world:=warehouse.sdf
```

### Teleoperation
```bash
source setup.sh
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/robot1/cmd_vel
```

Behavior service commands (`walk`, `up`, `sit`):
```bash
ros2 service call /robot1/robot_behavior_command quadropted_msgs/srv/RobotBehaviorCommand "{command: 'walk'}"
```

# 4. Mapping and Navigation

For mapping, run each in a separate terminal:
```bash
ros2 launch gazebo_sim launch.py sensors:=true world:=warehouse.sdf
ros2 launch cartographer go2_cartographer.launch.py
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/robot1/cmd_vel
ros2 run nav2_map_server map_saver_cli -t map -f warehouse_map
```

![alt text](images/image-21.png)

![alt text](<images/2026-05-10 20-10-20.gif>)

For navigation:
```bash
# Terminal 1
ros2 launch gazebo_sim launch.py sensors:=true world:=warehouse.sdf
# Terminal 2
ros2 launch navigation2 go2_navigation2.launch.py
```

Set a `2D Pose Estimate` at the Go2 spawn point (0, 0), then use `2D Nav Goal` to navigate.

![alt text](<images/2026-05-10 20-18-03.gif>)

![alt text](images/image-22.png)

# Afterword
This project would not be possible without the strength of the open-source community. I mainly integrated existing open-source projects and made some modifications, but the credit belongs far more to the original project authors. Thanks to the open-source community, open-source projects, and open-source contributors.

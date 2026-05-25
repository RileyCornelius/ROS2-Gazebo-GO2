<h1 align="center">Go2 Gazebo Sim</h1>

<p align="center">
  <a href="README.md">中文</a> |
  <a href="README_EN.md">English</a>
</p>

<p align="center">
  <img src="https://www.unitree.com/images/b5fffd3e4fc04e6f9fcafedb9516b341_3840x2146.jpg" alt="Unitree Go2" width="720">
</p>

# 1. Project Description
This repository is the foundational ROS2-Gazebo simulation project for Chapter 1 of the Unitree robot dog series. The repository will be updated from time to time as the full project series progresses. You can check the current project plan on my Feishu page: [Feishu Project Page](https://ai.feishu.cn/wiki/CVpbwLIiMiwGnekKjhMcLXTRnag?from=from_copylink). This is expected to be a very long-term project.

# 2. How to Use the Project
## 2.1 Build and Run Directly
Go to the workspace:
```bash
cd ROS2-Gazebo-GO2
rosdep update
rosdep install --from-paths . --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

![alt text](images/image-17.png)

Launch the simulation. The first launch may take longer because required world resources need to be downloaded:
```bash
source setup.sh
ros2 launch gazebo_sim launch.py
```
After a successful launch, you should see something like this:
![alt text](images/image-18.png)

This project includes:
- A front monocular camera to simulate the GO2 front camera
- Two LiDAR sensors:
  - A front L1 LiDAR to simulate GO2’s built-in LiDAR
  - An external VLP16 LiDAR

Both LiDARs can publish `LaserScan` and `PointCloud2` data simultaneously, making mapping and navigation workflows easier. A D435i camera has also been added.

Use keyboard teleoperation:
```bash
cd ROS2-Gazebo-GO2
source setup.sh
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/robot1/cmd_vel
```

After running the command above, you can control the robot dog with your keyboard. You can also use the following service to control behavior. Supported commands are `walk`, `up`, and `sit`.
```bash
ros2 service call /robot1/robot_behavior_command quadropted_msgs/srv/RobotBehaviorCommand "{command: 'walk'}"
```

## 2.2 Mapping and Navigation
For mapping, run the following commands in terminal:
```bash
ros2 launch gazebo_sim launch.py sensors:=true world:=warehouse.sdf
ros2 launch cartographer go2_cartographer.launch.py
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/robot1/cmd_vel # keyboard control
ros2 run nav2_map_server map_saver_cli -t map -f warehouse_map # save map
```

![alt text](images/image-21.png)

![alt text](<images/2026-05-10 20-10-20.gif>)

For navigation, run:
```bash
ros2 launch gazebo_sim launch.py sensors:=true world:=warehouse.sdf
ros2 launch navigation2 go2_navigation2.launch.py
```

![alt text](images/image-22.png)

![alt text](<images/2026-05-10 20-18-03.gif>)

## 2.3 Using Docker
Before using Docker, please read the Docker setup guide briefly, since environments may differ. In my setup, I use mounted volumes.

The following commands cover the main Docker workflow:
```bash
cd ROS2-Gazebo-GO2/src/docker
docker compose up -d --build --remove-orphans        # Build containers
docker compose up -d go2_sim                        # Start container in detached mode
docker compose ps                                    # List containers
docker compose exec go2_sim bash                    # Enter container
docker compose down                                  # Remove containers
```

Inside the Docker container, follow the same steps as direct local usage:
```bash
colcon build
source install/setup.bash
```

![alt text](images/image-19.png)

Launch the simulation. First launch may take longer due to resource downloads:
```bash
ros2 launch gazebo_sim launch.py # Launch GO2 without extended sensors
ros2 launch gazebo_sim launch.py sensors:=true world:=warehouse.sdf # Launch GO2 with extended sensors in selected map
```
After successful startup, you should see:

![alt text](images/image-20.png)

As above, the project includes a front monocular camera and two LiDARs (GO2 front L1 + external VLP16), both of which can publish `LaserScan` and `PointCloud2`. This supports later mapping/navigation tasks. A D435i camera is also included.

```bash
cd ROS2-Gazebo-GO2
source install/local_setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/robot1/cmd_vel
```
![alt text](<images/2026-05-10 19-41-15.gif>)

Once the command runs, you can control the robot dog with keyboard input. Behavior services support `walk`, `up`, and `sit`.
```bash
ros2 service call /robot1/robot_behavior_command quadropted_msgs/srv/RobotBehaviorCommand "{command: 'walk'}"
```
![alt text](<images/2026-05-10 19-48-16.gif>)

# Afterword
This project would not be possible without the strength of the open-source community. I mainly integrated existing open-source projects and made some modifications, but the credit belongs far more to the original project authors. Thanks to the open-source community, open-source projects, and open-source contributors.

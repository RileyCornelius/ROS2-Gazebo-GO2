FROM osrf/ros:humble-desktop-full

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    bash-completion \
    build-essential \
    curl \
    git \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    sudo \
    wget \
    ros-humble-angles \
    ros-humble-camera-info-manager \
    ros-humble-cartographer \
    ros-humble-cartographer-ros \
    ros-humble-controller-manager \
    ros-humble-cyclonedds \
    ros-humble-gazebo-dev \
    ros-humble-gazebo-plugins \
    ros-humble-gazebo-ros \
    ros-humble-gz-ros2-control \
    ros-humble-hardware-interface \
    ros-humble-ign-ros2-control \
    ros-humble-joint-state-publisher \
    ros-humble-launch-ros \
    ros-humble-nav2-bringup \
    ros-humble-nav2-common \
    ros-humble-navigation2 \
    ros-humble-opennav-docking \
    ros-humble-pluginlib \
    ros-humble-rclcpp \
    ros-humble-rclpy \
    ros-humble-robot-localization \
    ros-humble-robot-state-publisher \
    ros-humble-ros-gz \
    ros-humble-ros-gz-bridge \
    ros-humble-ros-gz-image \
    ros-humble-ros-gz-sim \
    ros-humble-rosidl-default-generators \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-rqt-robot-steering \
    ros-humble-rqt-tf-tree \
    ros-humble-rviz2 \
    ros-humble-sensor-msgs \
    ros-humble-slam-toolbox \
    ros-humble-std-msgs \
    ros-humble-teleop-twist-keyboard \
    ros-humble-tf-transformations \
    ros-humble-urdf \
    ros-humble-velodyne-description \
    ros-humble-xacro && \
    (rosdep init || true) && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USERNAME=rosuser

ENV DEBIAN_FRONTEND= \
    WORKSPACE=/workspaces/ROS2-Gazebo-GO2 \
    RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
    GZ_SIM_RESOURCE_PATH=/workspaces/ROS2-Gazebo-GO2/src/gazebo_sim/models \
    CYCLONEDDS_URI=file:///workspaces/ROS2-Gazebo-GO2/config/cyclonedds.xml \
    QT_X11_NO_MITSHM=1 \
    NVIDIA_DRIVER_CAPABILITIES=all

RUN groupadd --gid ${GROUP_ID} ${USERNAME} && \
    useradd --uid ${USER_ID} --gid ${GROUP_ID} --create-home --shell /bin/bash ${USERNAME} && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} && \
    chmod 0440 /etc/sudoers.d/${USERNAME}

RUN { \
    echo "source /opt/ros/humble/setup.bash"; \
    echo "if [ -f /workspaces/ROS2-Gazebo-GO2/install/setup.bash ]; then source /workspaces/ROS2-Gazebo-GO2/install/setup.bash; fi"; \
    echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp"; \
    echo "export GZ_SIM_RESOURCE_PATH=/workspaces/ROS2-Gazebo-GO2/src/gazebo_sim/models"; \
    echo "export CYCLONEDDS_URI=file:///workspaces/ROS2-Gazebo-GO2/config/cyclonedds.xml"; \
    } >> /home/${USERNAME}/.bashrc

WORKDIR /workspaces/ROS2-Gazebo-GO2

USER ${USERNAME}

CMD ["/bin/bash"]

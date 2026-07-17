# Industrial ROS2 Manipulation Lab — main image
#
# ROS2 Humble + Gazebo Classic 11 + MoveIt2 + ros2_control + the tools the lab
# needs. The repository is bind-mounted at /lab_ws (see compose.yaml); sources
# are NOT baked into the image, so image rebuilds are rare.
#
# NOTE — where does the Gazebo SIMULATOR come from?
#   The base image osrf/ros:humble-desktop-full already ships Gazebo Classic 11
#   (gzserver/gzclient), and ros-humble-gazebo-ros-pkgs below depends on the
#   'gazebo11' package too. So the simulator is present even though it is not
#   listed by name here. Verify inside the container with: gzserver --version
#   The gazebo-ros* packages below are the ROS2<->Gazebo bridges, not the
#   simulator itself.

FROM osrf/ros:humble-desktop-full

ENV DEBIAN_FRONTEND=noninteractive

# --- Core robotics stack -------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Simulation: gazebo-ros-pkgs pulls in Gazebo Classic 11 (the simulator) +
    # the ROS2 bridges; gazebo-ros2-control links ros2_control to Gazebo.
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-ros2-control \
    # Control
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-gripper-controllers \
    ros-humble-joint-state-broadcaster \
    ros-humble-joint-state-publisher-gui \
    # Planning
    ros-humble-moveit \
    ros-humble-moveit-setup-assistant \
    # Description tooling
    ros-humble-xacro \
    # Headless rendering. Gazebo Classic will NOT create a camera sensor without an X
    # server: no display, no /camera/points, no vision module (Module 6). Xvfb gives it a
    # virtual framebuffer so the cell runs — camera and all — on a machine with no GUI.
    xvfb \
    # Behavior trees — the C++ framework of Module 7/9 (industrial_bt_framework)
    ros-humble-behaviortree-cpp \
    ros-humble-geometric-shapes \
    libyaml-cpp-dev \
    # Perception
    ros-humble-vision-opencv \
    ros-humble-cv-bridge \
    ros-humble-pcl-ros \
    ros-humble-pcl-conversions \
    python3-opencv \
    # Workspace tooling
    python3-vcstool \
    python3-rosdep \
    python3-colcon-common-extensions \
    git \
    # GUI diagnostics
    x11-apps \
    mesa-utils \
    && rm -rf /var/lib/apt/lists/*

# --- Non-root user matching the host (avoids root-owned files in the bind mount)
ARG HOST_UID=1000
ARG HOST_GID=1000
RUN groupadd -g "${HOST_GID}" lab 2>/dev/null || true \
    && useradd -m -u "${HOST_UID}" -g "${HOST_GID}" -s /bin/bash lab 2>/dev/null || true

# --- GUI/Qt behavior --------------------------------------------------------------
ENV QT_X11_NO_MITSHM=1

# --- Workspace --------------------------------------------------------------------
RUN mkdir -p /lab_ws && chown "${HOST_UID}:${HOST_GID}" /lab_ws
WORKDIR /lab_ws

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER lab
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]

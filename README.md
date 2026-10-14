# PX4 ROS 2 Drone Teleoperation

Keyboard and joystick teleoperation for PX4 SITL using **Ubuntu 24.04
LTS**, **ROS 2 Jazzy**, Gazebo, and the Micro XRCE-DDS Agent.

This repository contains `px4_offboard` and `px4_bringup`. The commands
below match the launch files currently included in this repository.

> **Scope:** These instructions target simulation. They do not establish
> that the configuration is safe for a real aircraft.

## Contents

-   [Features](#features)
-   [Requirements](#requirements)
-   [Install prerequisites](#install-prerequisites)
-   [Workspace and build](#workspace-and-build)
-   [Start PX4 and the agent](#start-px4-and-the-agent)
-   [Keyboard teleoperation](#keyboard-teleoperation)
-   [Joystick teleoperation](#joystick-teleoperation)
-   [Verify communication](#verify-communication)
-   [Troubleshooting](#troubleshooting)
-   [Safety](#safety)

## Features

-   Keyboard velocity control
-   Joystick teleoperation
-   PX4 Offboard velocity controller
-   Position-control node
-   Launch files for keyboard, joystick, and PX4 SITL bringup

## Requirements

-   Ubuntu 24.04 LTS and ROS 2 Jazzy
-   PX4 Autopilot with Gazebo support
-   Micro XRCE-DDS Agent
-   `px4_msgs` definitions compatible with your PX4 firmware
-   GNOME Terminal (launch files open new terminal windows)
-   A joystick/game controller for joystick mode

The bringup launch expects PX4 at `~/PX4-Autopilot`, starts
`make px4_sitl gz_x500`, and starts the agent on UDP port `8888`.

## Install prerequisites

### 1. Install ROS 2 Jazzy

Follow the official [ROS 2 Jazzy Ubuntu installation
guide](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html),
then run:

``` bash
source /opt/ros/jazzy/setup.bash
```

### 2. Install common tools

``` bash
sudo apt update
sudo apt install -y python3-rosdep python3-colcon-common-extensions python3-vcstool python3-pip gnome-terminal
```

Initialize rosdep if it has not already been initialized:

``` bash
sudo rosdep init
rosdep update
```

If `rosdep init` says it is already initialized, just run
`rosdep update`.

### 3. Install PX4 and Gazebo

Follow the [official PX4 Ubuntu development
setup](https://docs.px4.io/main/en/dev_setup/dev_env_linux_ubuntu) for
the PX4 release you intend to use. The launch file expects the source
tree at `~/PX4-Autopilot`. If yours is elsewhere, edit
`px4_bringup/launch/minimal.launch.py`.

### 4. Install Micro XRCE-DDS Agent

Follow the [PX4 ROS 2
guide](https://docs.px4.io/main/en/ros2/user_guide.html) for the
matching PX4 release. Verify the command is available:

``` bash
MicroXRCEAgent --help
```

The included launch uses `MicroXRCEAgent udp4 -p 8888`. PX4's client
configuration and the agent port must match.

## Workspace and build

If you already have a workspace with compatible `px4_msgs`, use it.
Otherwise create a workspace and clone this project:

``` bash
mkdir -p ~/px4_ros2_ws/src
cd ~/px4_ros2_ws/src
git clone https://github.com/TechNinja-01/px4-ros2-drone-teleoperation.git
```

Ensure a complete, compatible `px4_msgs` ROS 2 package is present under
`~/px4_ros2_ws/src`. The `px4_msgs/` directory in this repository is not
a complete package; obtain the matching package/version using the [PX4
ROS 2 guide](https://docs.px4.io/main/en/ros2/user_guide.html). Do not
mix arbitrary PX4, `px4_msgs`, and `px4_ros_com` branches.

Build from the workspace root:

``` bash
source /opt/ros/jazzy/setup.bash
cd ~/px4_ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Replace `~/px4_ros2_ws` if your workspace is elsewhere. Check package
discovery:

``` bash
ros2 pkg list | grep -E '^(px4_offboard|px4_bringup)$'
```

**Build note:** If a package such as `px4_ros_com` fails on a missing
generated header like `px4_msgs/msg/sensor_gps.hpp`, this may indicate
incompatible versions or a stale example. Align package versions before
assuming the workspace is built. A failed `colcon build` means the
overall build did not complete successfully.

## Start PX4 and the agent

### Option A --- included bringup launch

In a terminal:

``` bash
source /opt/ros/jazzy/setup.bash
source ~/px4_ros2_ws/install/setup.bash
ros2 launch px4_bringup minimal.launch.py
```

It opens separate GNOME Terminal windows for: 1. PX4 SITL and Gazebo
(`make px4_sitl gz_x500`) 2. Micro XRCE-DDS Agent (`udp4 -p 8888`),
after a short delay

It assumes PX4 is in `~/PX4-Autopilot` and `MicroXRCEAgent` is on
`PATH`.

### Option B --- start components manually

**Terminal 1 --- PX4 SITL**

``` bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500
```

**Terminal 2 --- XRCE-DDS Agent**

``` bash
MicroXRCEAgent udp4 -p 8888
```

Leave both running. Use either Option A or Option B, not both at once.

## Keyboard teleoperation

With PX4 and the agent running, open another terminal:

``` bash
source /opt/ros/jazzy/setup.bash
source ~/px4_ros2_ws/install/setup.bash
ros2 launch px4_offboard keyboard_teleop.launch.py
```

The launch starts the velocity controller and opens a separate GNOME
Terminal for the keyboard node. Click that keyboard terminal to give it
focus before pressing keys.

  Key                   Action
  --------------------- ---------------------------
  `Space`               Toggle arm/disarm request
  `W` / `S`             Up / down
  Up / Down arrows      Forward / backward
  Left / Right arrows   Left / right
  `A` / `D`             Yaw left / yaw right
  `X`                   Stop movement

PX4 uses NED coordinates in common configurations, where negative Z
velocity corresponds to upward movement. Verify behavior in simulation.

## Joystick teleoperation

Connect the controller first. Confirm the ROS 2 `joy` package and the
project's `config/joy_config.yaml` are available, then run:

``` bash
source /opt/ros/jazzy/setup.bash
source ~/px4_ros2_ws/install/setup.bash
ros2 launch px4_offboard joystick_teleop.launch.py
```

This launch starts the velocity controller, `joy_node`, and the joystick
teleoperation node. Button and axis mappings depend on the
controller/configuration. Test in simulation first:

``` bash
ros2 topic list | grep joy
ros2 topic echo /joy
```

## Verify communication

In a sourced terminal:

``` bash
source /opt/ros/jazzy/setup.bash
source ~/px4_ros2_ws/install/setup.bash
ros2 topic list | grep '/fmu/'
ros2 topic echo /offboard_velocity_cmd
ros2 topic echo /fmu/in/trajectory_setpoint
```

Vehicle status topic names vary by PX4/`px4_msgs` version. Discover
available names with:

``` bash
ros2 topic list | grep vehicle_status
```

## Troubleshooting

**`ros2 launch` cannot find a package** Source Jazzy and the workspace
overlay in the same terminal, then confirm the workspace built
successfully:

``` bash
source /opt/ros/jazzy/setup.bash
source ~/px4_ros2_ws/install/setup.bash
ros2 pkg list | grep -E '^(px4_offboard|px4_bringup)$'
```

**`gnome-terminal` is missing**

``` bash
sudo apt install -y gnome-terminal
```

**`MicroXRCEAgent` is missing** Install it using the official PX4
instructions and check `which MicroXRCEAgent`.

**PX4 topics do not appear** Confirm SITL is running, the agent is
running on UDP port 8888, PX4's XRCE-DDS client is configured to
connect, and `px4_msgs` matches the firmware version.

**Missing `sensor_gps.hpp` during build** Check for a version mismatch
between `px4_ros_com` and `px4_msgs`; align the versions before
rebuilding. Do not change branches or delete your PX4 tree without
confirming which versions are needed.

**Keyboard keys do nothing** Focus the separate keyboard terminal, check
that the teleop node is running, and look for Python errors in the
terminal output.

## Safety

-   This guide is for simulation and development.
-   Validate arming checks, Offboard entry/exit, communications-loss
    behavior, failsafes, and emergency procedures independently before
    any hardware use.
-   Follow local regulations. Never assume successful SITL operation
    means real-flight readiness.

## References

-   [ROS 2 Jazzy
    installation](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)
-   [PX4 Ubuntu development
    setup](https://docs.px4.io/main/en/dev_setup/dev_env_linux_ubuntu)
-   [PX4 ROS 2 User
    Guide](https://docs.px4.io/main/en/ros2/user_guide.html)
-   [PX4 Autopilot](https://github.com/PX4/PX4-Autopilot)
-   [Micro XRCE-DDS
    Agent](https://github.com/eProsima/Micro-XRCE-DDS-Agent)
-   [QGroundControl](https://docs.qgroundcontrol.com/)

Preserve applicable license and copyright notices for any upstream code
used or adapted in this repository.

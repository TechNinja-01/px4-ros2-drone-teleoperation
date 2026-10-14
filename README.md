# PX4 ROS 2 Drone Teleoperation

Beginner-friendly keyboard and joystick teleoperation for **PX4 SITL**,
**Gazebo**, **ROS 2 Jazzy**, and the **Micro XRCE-DDS Agent** on Ubuntu
24.04 LTS.

## Demo video

Watch the project demonstration: **[PX4 ROS 2 Drone Teleoperation
Demo](media/demo.mp4)**

> The link works after `media/demo.mp4` is added to the repository. See
> the **Add your recording to GitHub** instructions below. If the video
> is large, upload it to YouTube or GitHub Releases and replace the link
> above with the public video URL.

## What this project contains

-   `px4_bringup/` --- launch file to start PX4 SITL + Gazebo and the
    Micro XRCE-DDS Agent.
-   `px4_offboard/` --- velocity controller, keyboard teleoperation,
    joystick teleoperation, and launch files.

## Contents

1.  [How the system works](#how-the-system-works)
2.  [Requirements](#requirements)
3.  [Install software](#install-software)
4.  [Prepare the ROS 2 workspace](#prepare-the-ros-2-workspace)
5.  [Build the packages](#build-the-packages)
6.  [Start PX4 and the Agent](#start-px4-and-the-agent)
7.  [Keyboard teleoperation](#keyboard-teleoperation)
8.  [Joystick teleoperation](#joystick-teleoperation)
9.  [Check topics](#check-topics)
10. [Troubleshooting](#troubleshooting)
11. [Add your recording to GitHub](#add-your-recording-to-github)
12. [Safety](#safety)

## How the system works

The main components are:

1.  **PX4 SITL** --- the simulated flight controller.
2.  **Gazebo** --- renders the simulated drone and world.
3.  **Micro XRCE-DDS Agent** --- connects PX4's uXRCE-DDS client to ROS
    2.
4.  **This ROS 2 project** --- publishes control requests and velocity
    setpoints.

Start PX4/Gazebo and the Agent first. Then launch keyboard or joystick
teleoperation.

## Requirements

-   Ubuntu 24.04 LTS
-   ROS 2 Jazzy
-   PX4 Autopilot with Gazebo simulation support
-   Micro XRCE-DDS Agent
-   A compatible `px4_msgs` package
-   GNOME Terminal (the supplied launch files open new terminal windows)
-   A joystick/game controller for joystick mode

The launch files expect PX4 at `~/PX4-Autopilot`. In the example
commands below, the workspace is `~/Desktop/px4_ros2_ws`, matching the
workspace used for this project demo. If you use another location,
change the path consistently.

## Install software

### 1. Install ROS 2 Jazzy

Follow the official [ROS 2 Jazzy installation instructions for
Ubuntu](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html).

Open a terminal and source ROS 2:

``` bash
source /opt/ros/jazzy/setup.bash
echo $ROS_DISTRO
```

Expected output: `jazzy`.

### 2. Install common tools

``` bash
sudo apt update
sudo apt install -y python3-rosdep python3-colcon-common-extensions gnome-terminal
```

Initialize rosdep only if it has not been initialized before:

``` bash
sudo rosdep init
rosdep update
```

If `sudo rosdep init` says it is already initialized, just run
`rosdep update`.

### 3. Install PX4 and Gazebo

Follow the official [PX4 Ubuntu development
setup](https://docs.px4.io/main/en/dev_setup/dev_env_linux_ubuntu). Make
sure PX4 is installed at:

``` text
~/PX4-Autopilot
```

The included bringup launch runs `make px4_sitl gz_x500`. If your PX4
folder is elsewhere, update the path in
`px4_bringup/launch/minimal.launch.py`.

### 4. Install the Micro XRCE-DDS Agent

Follow the [official PX4 ROS 2
guide](https://docs.px4.io/main/en/ros2/user_guide.html) for
instructions compatible with your PX4 release.

Check that the executable is available:

``` bash
which MicroXRCEAgent
```

The included launch uses:

``` bash
MicroXRCEAgent udp4 -p 8888
```

PX4's uXRCE-DDS client must be configured to connect to the Agent using
compatible settings.

## Prepare the ROS 2 workspace

If you already have this repository in `~/Desktop/px4_ros2_ws/src`, skip
the clone command. Otherwise:

``` bash
mkdir -p ~/Desktop/px4_ros2_ws/src
cd ~/Desktop/px4_ros2_ws/src
git clone https://github.com/TechNinja-01/px4-ros2-drone-teleoperation.git
```

A compatible, complete `px4_msgs` ROS 2 package must also be present
under `src`. The `px4_msgs/` directory included in this repository is
not a complete message package. Use the [PX4 ROS 2
guide](https://docs.px4.io/main/en/ros2/user_guide.html) to choose a
`px4_msgs` version compatible with your PX4 firmware.

**Version compatibility matters:** do not mix arbitrary PX4, `px4_msgs`,
and `px4_ros_com` branches. A mismatch can cause missing generated
message-header errors.

## Build the packages

Run in a terminal:

``` bash
source /opt/ros/jazzy/setup.bash
cd ~/Desktop/px4_ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-up-to px4_offboard px4_bringup
```

If the build succeeds, source the workspace:

``` bash
source ~/Desktop/px4_ros2_ws/install/setup.bash
```

Check that both project packages are discoverable:

``` bash
ros2 pkg list | grep -E '^(px4_offboard|px4_bringup)$'
```

Expected output includes:

``` text
px4_bringup
px4_offboard
```

If `colcon build` reports an error, do not continue as if the build
succeeded. A warning about a missing `px4_ros_com/local_setup.bash` may
indicate an incomplete or stale installation from another package. A
missing header such as `px4_msgs/msg/sensor_gps.hpp` can indicate
incompatible package versions. Resolve errors relevant to the packages
you need before running the project.

## Start PX4 and the Agent

Choose **one** method below. Do not start duplicate PX4 instances or
duplicate Agents on the same port.

### Method A: use this project's bringup launch

In a terminal:

``` bash
source /opt/ros/jazzy/setup.bash
source ~/Desktop/px4_ros2_ws/install/setup.bash
ros2 launch px4_bringup minimal.launch.py
```

The launch should open GNOME Terminal windows for: - PX4 SITL and Gazebo
(`make px4_sitl gz_x500`) - Micro XRCE-DDS Agent (`udp4 -p 8888`)

Keep those terminals open. This launch expects `~/PX4-Autopilot` and
`MicroXRCEAgent` on your `PATH`.

### Method B: start them manually

**Terminal 1 --- PX4 SITL + Gazebo**

``` bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500
```

Wait for PX4 and Gazebo to start.

**Terminal 2 --- Micro XRCE-DDS Agent**

``` bash
MicroXRCEAgent udp4 -p 8888
```

Leave both terminals running.

## Keyboard teleoperation

With PX4/Gazebo and the Agent running, open another terminal:

``` bash
source /opt/ros/jazzy/setup.bash
source ~/Desktop/px4_ros2_ws/install/setup.bash
ros2 launch px4_offboard keyboard_teleop.launch.py
```

The launch starts the velocity controller and opens a separate GNOME
Terminal for keyboard input. Click the keyboard terminal so it has focus
before pressing keys.

  Key                   Action
  --------------------- ---------------------------
  `Space`               Toggle arm/disarm request
  `W` / `S`             Up / down
  Up / Down arrows      Forward / backward
  Left / Right arrows   Left / right
  `A` / `D`             Yaw left / yaw right
  `X`                   Stop movement

PX4 commonly uses NED coordinates, where the Z axis points down;
negative Z velocity corresponds to upward movement. Test in Gazebo
first. Do not attempt takeoff until you have confirmed the commands and
Offboard behavior.

## Joystick teleoperation

Connect the joystick/game controller before launching. Then run:

``` bash
source /opt/ros/jazzy/setup.bash
source ~/Desktop/px4_ros2_ws/install/setup.bash
ros2 launch px4_offboard joystick_teleop.launch.py
```

This launch starts the velocity controller, `joy_node`, and the
project's joystick node. It reads settings from
`px4_offboard/config/joy_config.yaml`.

Mappings depend on the controller and configuration. Test in simulation
first. To inspect joystick messages:

``` bash
ros2 topic list | grep joy
ros2 topic echo /joy
```

## Check topics

In a new terminal, source ROS 2 and the workspace:

``` bash
source /opt/ros/jazzy/setup.bash
source ~/Desktop/px4_ros2_ws/install/setup.bash
```

List PX4 topics:

``` bash
ros2 topic list | grep '/fmu/'
```

Inspect the teleoperation velocity command:

``` bash
ros2 topic echo /offboard_velocity_cmd
```

Inspect trajectory setpoints sent toward PX4:

``` bash
ros2 topic echo /fmu/in/trajectory_setpoint
```

Vehicle status topic names differ by PX4 and `px4_msgs` version.
Discover the names available in your setup with:

``` bash
ros2 topic list | grep vehicle_status
```

## Troubleshooting

### `ros2: command not found`

``` bash
source /opt/ros/jazzy/setup.bash
```

If the setup file does not exist, install ROS 2 Jazzy first.

### `Package 'px4_offboard' not found`

``` bash
source /opt/ros/jazzy/setup.bash
source ~/Desktop/px4_ros2_ws/install/setup.bash
```

If it is still missing, confirm the repository is under the workspace's
`src` folder and that the build succeeded.

### `gnome-terminal` is missing

``` bash
sudo apt install -y gnome-terminal
```

### `MicroXRCEAgent` is missing

Install/build it following the [PX4 ROS 2
guide](https://docs.px4.io/main/en/ros2/user_guide.html), then check:

``` bash
which MicroXRCEAgent
```

### No `/fmu/` topics appear

-   Confirm PX4 SITL is running.
-   Confirm the Agent is running on UDP port `8888`.
-   Check that PX4's uXRCE-DDS client connects to the Agent.
-   Confirm that `px4_msgs` matches your PX4 firmware version.

### `/offboard_velocity_cmd` is not published

-   Confirm `keyboard_teleop.launch.py` is still running.
-   Check for Python errors in the launch terminal and the separate
    keyboard terminal.
-   Focus the keyboard terminal and press a movement key briefly.
-   Check nodes with `ros2 node list` and topics with `ros2 topic list`.

### Build reports missing `sensor_gps.hpp`

This may indicate a version mismatch between `px4_ros_com` and
`px4_msgs` or an outdated example. Align versions using the PX4 ROS 2
guide before rebuilding. Do not assume a failed build is successful.

## Safety

-   These instructions are for simulation and development.
-   Successful simulation does not prove that the system is safe for a
    real aircraft.
-   Before hardware use, validate arming checks, Offboard entry/exit
    behavior, communication-loss handling, failsafes, and emergency
    procedures independently.
-   Follow local regulations and keep people clear of any real aircraft.

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
-   [QGroundControl documentation](https://docs.qgroundcontrol.com/)

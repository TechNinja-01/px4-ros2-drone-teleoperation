# PX4 ROS 2 Drone Teleoperation

Keyboard-based drone teleoperation using **Ubuntu 24.04 LTS**, **ROS 2 Jazzy**, **PX4 SITL**, Gazebo, and Micro XRCE-DDS Agent.

## Features

- Keyboard-based velocity control
- Arm/disarm requests
- Vertical and horizontal movement
- Yaw control
- PX4 Offboard setpoint publishing

## Project Structure

- `px4_bringup/` — ROS 2 bringup package
- `px4_offboard/` — teleoperation and Offboard control
- `px4_offboard/launch/` — launch files
- `px4_offboard/config/` — configuration files

## Prerequisites

- Ubuntu 24.04 LTS
- ROS 2 Jazzy
- PX4 Autopilot with SITL and Gazebo
- Micro XRCE-DDS Agent
- Compatible `px4_msgs` definitions

Ensure the PX4 and `px4_msgs` versions are compatible.

## Build

```bash
source /opt/ros/jazzy/setup.bash
cd ~/Desktop/px4_ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```

Resolve build errors before relying on the complete workspace.

## Run

Start PX4 SITL with Gazebo and the Micro XRCE-DDS Agent using the commands appropriate for your installation.

Then open another terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/Desktop/px4_ros2_ws/install/setup.bash
ros2 launch px4_offboard keyboard_teleop.launch.py
```

Focus the keyboard teleoperation terminal before sending commands.

## Keyboard Controls

| Key | Action |
|---|---|
| Space | Toggle arm/disarm request |
| W / S | Up / down |
| Up / Down arrows | Forward / backward |
| Left / Right arrows | Left / right |
| A / D | Yaw left / right |
| X | Stop movement |

PX4 uses NED coordinates, so negative Z velocity commands upward motion.

## Diagnostics

```bash
ros2 topic list | grep '/fmu/out/'
ros2 topic echo /offboard_velocity_cmd
ros2 topic echo /fmu/in/trajectory_setpoint
ros2 topic echo /fmu/out/vehicle_status_v4 --once
```

Topic names may vary by PX4 version.

## Safety

This project has been tested in simulation. This does not establish that it is safe for real aircraft. Verify arming checks, Offboard failsafes, and emergency procedures before hardware testing.

## Licensing and Attribution

Preserve applicable upstream copyright notices and license terms for any source code used or adapted.

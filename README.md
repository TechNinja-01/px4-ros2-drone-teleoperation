# PX4 ROS 2 Drone Teleoperation

A beginner-oriented guide to running keyboard or joystick teleoperation
with **PX4 SITL**, **Gazebo**, **ROS 2 Jazzy**, and the **Micro XRCE-DDS
Agent**.

This project contains two ROS 2 packages:

-   `px4_bringup` --- starts PX4 SITL with Gazebo and starts the
    XRCE-DDS Agent.
-   `px4_offboard` --- contains the velocity controller and
    keyboard/joystick teleoperation nodes.

> **Important:** These instructions are for simulation on Ubuntu 24.04
> LTS. Do not try them first on a real drone. The commands assume the
> PX4 source folder is `~/PX4-Autopilot`, and the ROS 2 workspace is
> `~/px4_ros2_ws`. If your folders are elsewhere, substitute your actual
> paths.

## 1. Videos and visual learning

Watch these to understand the overall workflow. They are useful learning
resources, but their code or ROS distribution may differ from this
repository.

1.  **PX4 + ROS 2 integration, joystick and keyboard teleoperation:**
    [Watch the full integration masterclass on
    YouTube](https://www.youtube.com/watch?v=cXdP29a-SEQ). The video
    uses ROS 2 Humble; this project uses Jazzy.
2.  **Keyboard teleoperation and PX4 control concepts:** [Watch PX4 +
    ROS 2 Teleop on
    YouTube](https://www.youtube.com/watch?v=skv9fBnTFDU). The
    implementation differs, but the concepts are useful.
3.  **Ubuntu 24.04 + ROS 2 Jazzy + PX4 SITL setup notes:** [Open the
    Jazzy setup
    guide](https://tianhuagao.github.io/documentation/px4-ros2-gazebo/).
4.  **Official PX4 ROS 2 documentation:** [PX4 ROS 2 User
    Guide](https://docs.px4.io/main/en/ros2/user_guide.html).

## 2. What runs, and why?

The system has four main parts:

-   **PX4 SITL:** the simulated flight controller.
-   **Gazebo:** shows the simulated drone and world.
-   **Micro XRCE-DDS Agent:** connects PX4's uXRCE-DDS client to ROS 2.
-   **This ROS 2 project:** sends control requests and velocity
    setpoints.

The usual startup order is:

1.  Start PX4 SITL and Gazebo.
2.  Start the Micro XRCE-DDS Agent.
3.  Start this project's keyboard or joystick launch.
4.  Check the topics and test movement in simulation.

The included `px4_bringup/minimal.launch.py` starts PX4 and the agent in
separate GNOME Terminal windows. You can use that launch instead of
starting them manually.

## 3. Before you begin

You need:

-   Ubuntu 24.04 LTS.
-   ROS 2 Jazzy installed and working.
-   PX4 Autopilot installed with Gazebo simulation support.
-   Micro XRCE-DDS Agent installed.
-   A compatible `px4_msgs` package in your ROS 2 workspace.
-   GNOME Terminal, because the launch files open new terminal windows.
-   A joystick/game controller only if you want joystick mode.

Official installation instructions:

-   [Install ROS 2
    Jazzy](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)
-   [Install PX4's Ubuntu development
    environment](https://docs.px4.io/main/en/dev_setup/dev_env_linux_ubuntu)
-   [Configure PX4 with ROS
    2](https://docs.px4.io/main/en/ros2/user_guide.html)

Open a terminal and check that ROS 2 is available:

``` bash
source /opt/ros/jazzy/setup.bash
echo $ROS_DISTRO
```

Expected output:

``` text
jazzy
```

If you see `No such file or directory`, install ROS 2 Jazzy before
continuing.

Install common tools if needed:

``` bash
sudo apt update
sudo apt install -y python3-rosdep python3-colcon-common-extensions gnome-terminal
```

If `rosdep` has never been initialized on this computer, run:

``` bash
sudo rosdep init
rosdep update
```

If `sudo rosdep init` says it is already initialized, do not repeat it;
just run `rosdep update`.

## 4. Check your PX4 and Agent installations

### Check PX4

``` bash
ls ~/PX4-Autopilot
```

You should see folders and files from the PX4 source repository. The
included bringup launch expects it at this exact path.

### Check the XRCE-DDS Agent

``` bash
which MicroXRCEAgent
```

If this prints a path, the command is available. If it prints nothing,
follow the Agent setup instructions in the [official PX4 ROS 2
guide](https://docs.px4.io/main/en/ros2/user_guide.html).

The included launch uses this Agent command and port:

``` bash
MicroXRCEAgent udp4 -p 8888
```

PX4's uXRCE-DDS client and the Agent must use compatible settings. Only
one Agent should listen on the same port for this connection.

## 5. Put the project in a ROS 2 workspace

If you already have a working workspace with this project and compatible
`px4_msgs`, skip to Section 6.

Otherwise, create a workspace and clone this repository:

``` bash
mkdir -p ~/px4_ros2_ws/src
cd ~/px4_ros2_ws/src
git clone https://github.com/TechNinja-01/px4-ros2-drone-teleoperation.git
```

Make sure a **complete `px4_msgs` ROS 2 package** is also present under
`~/px4_ros2_ws/src`. The `px4_msgs` directory in this repository is not
a complete package. Use the official PX4 ROS 2 guide to select a version
compatible with your PX4 firmware.

**Version warning:** Do not combine random branches of PX4, `px4_msgs`,
and `px4_ros_com`. A mismatch can cause missing generated message-header
errors during compilation.

## 6. Install dependencies and build

Run these commands from a terminal:

``` bash
source /opt/ros/jazzy/setup.bash
cd ~/px4_ros2_ws
rosdep install --from-paths src --ignore-src -r -y
```

Now build the project packages and the compatible `px4_msgs` package:

``` bash
colcon build --symlink-install --packages-up-to px4_bringup px4_offboard
```

This builds the selected packages and their declared dependencies. If
your `px4_msgs` dependency is not declared by a package, make sure the
compatible `px4_msgs` package is built too, for example:

``` bash
colcon build --symlink-install --packages-select px4_msgs
colcon build --symlink-install --packages-up-to px4_bringup px4_offboard
```

Then source the workspace overlay:

``` bash
source ~/px4_ros2_ws/install/setup.bash
```

Check that ROS 2 can find both packages:

``` bash
ros2 pkg list | grep -E '^(px4_bringup|px4_offboard)$'
```

Expected: both `px4_bringup` and `px4_offboard` appear.

> **If the build fails:** do not continue as if it succeeded. For
> example, a `px4_ros_com` error about `px4_msgs/msg/sensor_gps.hpp` may
> indicate incompatible versions or an outdated example elsewhere in the
> workspace. Align versions or build only the needed compatible
> packages. The `colcon build` command must finish successfully for the
> packages you plan to run.

## 7. Start PX4 SITL, Gazebo and the Agent

Choose **one** of the following methods. Do not start two PX4 instances
or two Agents on the same port.

### Method A --- easiest: use this project's bringup launch

**Terminal 1:** run:

``` bash
source /opt/ros/jazzy/setup.bash
source ~/px4_ros2_ws/install/setup.bash
ros2 launch px4_bringup minimal.launch.py
```

The launch should open separate GNOME Terminal windows for:

-   PX4 SITL + Gazebo, using `make px4_sitl gz_x500`.
-   Micro XRCE-DDS Agent, using UDP port `8888`.

Leave these windows open. Gazebo may take a little time to start.

### Method B --- start components yourself

Use this if you prefer to see each command separately.

**Terminal 1 --- PX4 and Gazebo:**

``` bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500
```

Wait for PX4 and Gazebo to start.

**Terminal 2 --- Micro XRCE-DDS Agent:**

``` bash
MicroXRCEAgent udp4 -p 8888
```

Leave both terminals running. Do not also run Method A.

## 8. Start keyboard teleoperation

Open a **new terminal** after PX4 and the Agent are running:

``` bash
source /opt/ros/jazzy/setup.bash
source ~/px4_ros2_ws/install/setup.bash
ros2 launch px4_offboard keyboard_teleop.launch.py
```

This launch starts the velocity controller and opens another terminal
window for keyboard input.

**Important:** click inside the keyboard teleoperation terminal so it
has keyboard focus before pressing keys.

### Keyboard controls

  Key                   Action
  --------------------- ---------------------------
  `Space`               Toggle arm/disarm request
  `W` / `S`             Up / down
  Up / Down arrows      Forward / backward
  Left / Right arrows   Left / right
  `A` / `D`             Yaw left / yaw right
  `X`                   Stop movement

PX4 commonly uses the NED coordinate frame, where the Z axis points
down. A negative Z velocity therefore corresponds to upward movement.
Test and observe behavior in Gazebo before relying on any control.

## 9. Start joystick teleoperation

Connect your joystick before launching. Then open a new terminal:

``` bash
source /opt/ros/jazzy/setup.bash
source ~/px4_ros2_ws/install/setup.bash
ros2 launch px4_offboard joystick_teleop.launch.py
```

This starts the velocity controller, ROS 2 `joy_node`, and the project's
joystick node. The launch reads settings from
`px4_offboard/config/joy_config.yaml`.

Button and axis mappings depend on your controller and configuration.
Test them in simulation before flight.

If joystick input does not appear, try:

``` bash
ros2 topic list | grep joy
ros2 topic echo /joy
```

## 10. Check whether ROS 2 is receiving data

Open another terminal and source both environments:

``` bash
source /opt/ros/jazzy/setup.bash
source ~/px4_ros2_ws/install/setup.bash
```

List PX4 topics:

``` bash
ros2 topic list | grep '/fmu/'
```

Check the velocity command from the teleoperation node:

``` bash
ros2 topic echo /offboard_velocity_cmd
```

Check trajectory setpoints sent toward PX4:

``` bash
ros2 topic echo /fmu/in/trajectory_setpoint
```

Topic names can differ by PX4 and `px4_msgs` version. To discover
available status topics, run:

``` bash
ros2 topic list | grep vehicle_status
```

If the topic list is empty, check that PX4 is running, the Agent is
connected, and the `px4_msgs` version matches the firmware.

## 11. Troubleshooting

### `ros2: command not found`

Run:

``` bash
source /opt/ros/jazzy/setup.bash
```

If that file does not exist, ROS 2 Jazzy is not installed at the
expected location.

### `Package 'px4_offboard' not found`

Run:

``` bash
source /opt/ros/jazzy/setup.bash
source ~/px4_ros2_ws/install/setup.bash
```

If the package is still missing, check the build output and confirm that
this repository is under the workspace's `src` directory.

### `gnome-terminal` not found

``` bash
sudo apt install -y gnome-terminal
```

### `MicroXRCEAgent` not found

Follow the Agent installation steps in the [PX4 ROS 2
guide](https://docs.px4.io/main/en/ros2/user_guide.html), then check:

``` bash
which MicroXRCEAgent
```

### Missing `sensor_gps.hpp` during build

This often points to incompatible `px4_ros_com` and `px4_msgs` versions
or a stale example. Check the PX4 ROS 2 version guidance and align
packages. Do not assume the workspace built if `colcon` reports an
error.

### Keyboard does nothing

-   Click the separate keyboard terminal to focus it.
-   Check that the keyboard node is still running.
-   Read any error messages in the terminal.
-   Confirm the PX4 and Agent terminals are still running.

### Gazebo or PX4 does not start

Run the PX4 command manually from `~/PX4-Autopilot` and read the error
printed in that terminal. Resolve PX4/Gazebo setup issues before
launching ROS 2 teleoperation.

## 12. Safety

-   Use this guide for simulation and development.
-   A successful simulation does **not** prove that the system is safe
    for a real aircraft.
-   Before any hardware use, validate arming checks, Offboard
    entry/exit, communications-loss behavior, failsafes, and emergency
    procedures.
-   Follow applicable local laws and keep people clear of any real
    aircraft.

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

Please preserve applicable license and copyright notices for upstream
code used or adapted in this repository.

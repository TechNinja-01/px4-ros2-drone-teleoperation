#!/usr/bin/env python3

import sys
import time
import select
import termios
import tty

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    QoSReliabilityPolicy,
    QoSHistoryPolicy,
    QoSDurabilityPolicy,
)

from geometry_msgs.msg import Twist
from std_msgs.msg import Bool


# Conservative speeds for initial testing in Gazebo SITL
XY_SPEED = 0.5       # metres per second
VERTICAL_SPEED = 0.4 # metres per second
YAW_SPEED = 0.6      # radians per second

KEY_TIMEOUT = 0.35   # Stop motion shortly after key-repeat stops
PUBLISH_RATE = 20.0  # Hz


class KeyboardTeleop(Node):

    def __init__(self):
        super().__init__('keyboard_teleop')

        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5,
        )

        self.cmd_pub = self.create_publisher(
            Twist, '/offboard_velocity_cmd', qos
        )
        self.arm_pub = self.create_publisher(
            Bool, '/arm_message', qos
        )

        self.armed = False
        self.key_times = {}

        self.timer = self.create_timer(
            1.0 / PUBLISH_RATE, self.loop
        )

        self.get_logger().info('Keyboard teleop started.')
        self.get_logger().info('SPACE: arm/disarm')
        self.get_logger().info('W: up | S: down')
        self.get_logger().info('UP/DOWN arrows: forward/backward')
        self.get_logger().info('LEFT/RIGHT arrows: left/right')
        self.get_logger().info('A/D: yaw left/right')
        self.get_logger().info('X: stop movement')

    @staticmethod
    def read_char(timeout=0.0):
        ready, _, _ = select.select(
            [sys.stdin], [], [], timeout
        )
        if ready:
            return sys.stdin.read(1)
        return None

    def get_key(self):
        char = self.read_char()

        if char is None:
            return None

        # Read terminal escape sequences for arrow keys.
        if char == '\x1b':
            second = self.read_char(0.04)

            if second is None:
                return None

            if second not in ('[', 'O'):
                return None

            third = self.read_char(0.04)

            if third is None:
                return None

            return char + second + third

        return char

    def handle_key(self, key):
        now = time.monotonic()

        if key == '\x03':
            raise KeyboardInterrupt

        # Space toggles the arm command.
        if key == ' ':
            self.key_times.clear()
            self.armed = not self.armed

            msg = Bool()
            msg.data = self.armed
            self.arm_pub.publish(msg)

            self.get_logger().info(
                'ARM command sent' if self.armed
                else 'DISARM command sent'
            )
            return

        # X immediately clears all movement commands.
        if key.lower() == 'x':
            self.key_times.clear()
            self.publish_velocity(0.0, 0.0, 0.0, 0.0)
            self.get_logger().info('Movement stopped.')
            return

        # Letter keys.
        letter_keys = {
            'w': 'w',
            's': 's',
            'a': 'a',
            'd': 'd',
        }

        normalized = key.lower()

        if normalized in letter_keys:
            self.key_times[letter_keys[normalized]] = now
            self.get_logger().info(
                f'Key pressed: {normalized.upper()}'
            )
            return

        # Support both common arrow-key terminal sequences.
        arrow_keys = {
            '\x1b[A': 'up',
            '\x1bOA': 'up',
            '\x1b[B': 'down',
            '\x1bOB': 'down',
            '\x1b[D': 'left',
            '\x1bOD': 'left',
            '\x1b[C': 'right',
            '\x1bOC': 'right',
        }

        if key in arrow_keys:
            name = arrow_keys[key]
            self.key_times[name] = now
            self.get_logger().info(
                f'Arrow key pressed: {name}'
            )

    def publish_velocity(self, vx, vy, vz, yaw_rate):
        msg = Twist()
        msg.linear.x = float(vx)
        msg.linear.y = float(vy)
        msg.linear.z = float(vz)
        msg.angular.z = float(yaw_rate)
        self.cmd_pub.publish(msg)

    def loop(self):
        key = self.get_key()

        if key is not None:
            self.handle_key(key)

        now = time.monotonic()

        # Expire keys when terminal key-repeat stops.
        expired = [
            name for name, last_time in self.key_times.items()
            if now - last_time > KEY_TIMEOUT
        ]

        for name in expired:
            del self.key_times[name]

        keys = self.key_times

        # PX4 uses NED for setpoints: negative Z is upward.
        vz = (
            -VERTICAL_SPEED if 'w' in keys else 0.0
        ) + (
            VERTICAL_SPEED if 's' in keys else 0.0
        )

        # Body-forward/backward and left/right commands.
        vx = (
            XY_SPEED if 'up' in keys else 0.0
        ) + (
            -XY_SPEED if 'down' in keys else 0.0
        )

        # FLU convention: positive Y is left.
        vy = (
            XY_SPEED if 'left' in keys else 0.0
        ) + (
            -XY_SPEED if 'right' in keys else 0.0
        )

        yaw_rate = (
            -YAW_SPEED if 'a' in keys else 0.0
        ) + (
            YAW_SPEED if 'd' in keys else 0.0
        )

        self.publish_velocity(vx, vy, vz, yaw_rate)


def main(args=None):
    if not sys.stdin.isatty():
        print(
            'Error: keyboard teleop needs an interactive terminal.',
            file=sys.stderr,
        )
        return

    old_settings = termios.tcgetattr(sys.stdin.fileno())
    node = None

    try:
        tty.setraw(sys.stdin.fileno())
        rclpy.init(args=args)
        node = KeyboardTeleop()
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        termios.tcsetattr(
            sys.stdin.fileno(),
            termios.TCSADRAIN,
            old_settings,
        )

        if node is not None:
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

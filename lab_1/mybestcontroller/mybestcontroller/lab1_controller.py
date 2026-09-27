"""Controller entry point for laboratory work 1."""

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
from turtlesim.msg import Pose


ISUID = '503326'
GOALS = [(4.0, 2.0), (7.0, 1.0), (5.0, 4.0)]

GOAL_TOLERANCE = 0.15
ALIGN_TOLERANCE = 0.25
FOLLOW_DISTANCE = 0.7

K_LINEAR = 1.5
K_ANGULAR = 4.0
MAX_LINEAR = 2.0
MAX_ANGULAR = 3.0


class Lab1Controller(Node):
    """Backbone for the student controller implementation."""

    def __init__(self):
        super().__init__('lab1_controller')

        self.namespace = self.get_namespace()
        self.is_follower = 'ns2' in self.namespace

        self.pose = None
        self.leader_pose = None
        self.goal_index = 0
        self.elapsed = None

        self.cmd_publisher = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.create_subscription(Pose, 'turtle1/pose', self.pose_callback, 10)

        if self.is_follower:
            leader_namespace = self.namespace.replace('ns2', 'ns1')
            self.create_subscription(
                Pose,
                leader_namespace + '/turtle1/pose',
                self.leader_pose_callback,
                10,
            )
            self.get_logger().info('Follower mode in ' + self.namespace)
        else:
            self.result_publisher = self.create_publisher(
                Float64, 'result_' + ISUID, 10)
            self.start_time = self.get_clock().now()
            self.create_timer(1.0, self.publish_result)
            self.get_logger().info('Leader mode in ' + self.namespace)

        self.create_timer(0.05, self.control_loop)

    def pose_callback(self, msg):
        self.pose = msg

    def leader_pose_callback(self, msg):
        self.leader_pose = msg

    def control_loop(self):
        if self.pose is None:
            return
        if self.is_follower:
            self.follow_leader()
        else:
            self.visit_goals()

    def visit_goals(self):
        if self.goal_index >= len(GOALS):
            return

        goal_x, goal_y = GOALS[self.goal_index]
        dx = goal_x - self.pose.x
        dy = goal_y - self.pose.y
        distance = math.hypot(dx, dy)

        if distance < GOAL_TOLERANCE:
            self.stop()
            self.goal_index += 1
            self.get_logger().info('Reached point ' + str(self.goal_index))
            if self.goal_index >= len(GOALS):
                duration = self.get_clock().now() - self.start_time
                self.elapsed = duration.nanoseconds / 1e9
                self.get_logger().info('Finished in %.2f s' % self.elapsed)
            return

        self.cmd_publisher.publish(self.steer_towards(dx, dy, distance))

    def follow_leader(self):
        if self.leader_pose is None:
            return

        dx = self.leader_pose.x - self.pose.x
        dy = self.leader_pose.y - self.pose.y
        distance = math.hypot(dx, dy)

        if distance < FOLLOW_DISTANCE:
            self.stop()
            return

        self.cmd_publisher.publish(self.steer_towards(dx, dy, distance))

    def steer_towards(self, dx, dy, distance):
        command = Twist()
        angle_error = self.normalize(math.atan2(dy, dx) - self.pose.theta)
        command.angular.z = self.clamp(K_ANGULAR * angle_error, MAX_ANGULAR)
        if abs(angle_error) < ALIGN_TOLERANCE:
            command.linear.x = min(K_LINEAR * distance, MAX_LINEAR)
        return command

    def stop(self):
        self.cmd_publisher.publish(Twist())

    def publish_result(self):
        if self.elapsed is None:
            return
        message = Float64()
        message.data = self.elapsed
        self.result_publisher.publish(message)

    @staticmethod
    def normalize(angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    @staticmethod
    def clamp(value, limit):
        return max(-limit, min(value, limit))


def main(args=None):
    """Run the laboratory controller node."""
    rclpy.init(args=args)
    node = Lab1Controller()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

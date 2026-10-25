import math

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from lab2_interfaces.srv import A503326


class ServiceClient(Node):
    def __init__(self):
        super().__init__('service_client')
        self.cli = self.create_client(A503326, 'get_error')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')

        self.pose = None
        self.future = None
        self.state = 'ask'
        self.target_angle = 0.0
        self.distance = 0.0
        self.start_x = 0.0
        self.start_y = 0.0

        self.pose_subscriber = self.create_subscription(
            Pose,
            'turtle1/pose',
            self.pose_callback,
            10
        )
        self.cmd_publisher = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.control_step)

    def pose_callback(self, msg):
        self.pose = msg

    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def stop(self):
        self.cmd_publisher.publish(Twist())

    def control_step(self):
        if self.pose is None:
            self.get_logger().info('Waiting for turtle pose...')
            return

        if self.state == 'ask':
            self.ask()
        elif self.state == 'wait':
            self.wait()
        elif self.state == 'turn':
            self.turn()
        elif self.state == 'go':
            self.go()

    def ask(self):
        self.stop()
        if self.pose.linear_velocity != 0.0 or self.pose.angular_velocity != 0.0:
            return

        request = A503326.Request()
        request.xcurrent = self.pose.x
        request.ycurrent = self.pose.y
        self.future = self.cli.call_async(request)
        self.state = 'wait'

    def wait(self):
        if not self.future.done():
            return

        response = self.future.result()

        if response.finished:
            self.get_logger().info('All targets reached')
            self.timer.cancel()
        elif response.success:
            self.get_logger().info('Target reached, next target')
            self.state = 'ask'
        else:
            self.target_angle = response.angle
            self.distance = response.distance
            self.start_x = self.pose.x
            self.start_y = self.pose.y
            self.state = 'turn'

    def turn(self):
        error = self.normalize_angle(self.target_angle - self.pose.theta)

        if abs(error) < 0.01:
            self.stop()
            self.state = 'go'
            return

        cmd = Twist()
        cmd.angular.z = 2.0 * error
        self.cmd_publisher.publish(cmd)

    def go(self):
        dx = self.pose.x - self.start_x
        dy = self.pose.y - self.start_y
        left = self.distance - math.sqrt(dx ** 2 + dy ** 2)

        if left < 0.01:
            self.stop()
            self.state = 'ask'
            return

        cmd = Twist()
        cmd.linear.x = 1.5 * left
        self.cmd_publisher.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ServiceClient()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

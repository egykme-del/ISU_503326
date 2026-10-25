import math

import rclpy
from rclpy.node import Node
from lab2_interfaces.srv import A503326


class ServiceServer(Node):
    def __init__(self):
        super().__init__('service_server')
        self.targets = [(4.0, 2.0), (7.0, 1.0), (5.0, 4.0)]
        self.index = 0
        self.srv = self.create_service(A503326, 'get_error', self.callback)
        self.get_logger().info('Server started')

    def callback(self, request, response):
        if self.index == len(self.targets):
            response.success = True
            response.finished = True
            return response

        target_x, target_y = self.targets[self.index]
        dx = target_x - request.xcurrent
        dy = target_y - request.ycurrent

        response.distance = math.sqrt(dx ** 2 + dy ** 2)
        response.angle = math.atan2(dy, dx)
        response.success = response.distance < 0.1

        if response.success:
            self.index += 1

        response.finished = self.index == len(self.targets)

        self.get_logger().info(
            f'x={request.xcurrent:.2f}, y={request.ycurrent:.2f}, '
            f'target=({target_x}, {target_y}), '
            f'distance={response.distance:.2f}, angle={response.angle:.2f}'
        )
        return response


def main(args=None):
    rclpy.init(args=args)
    node = ServiceServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

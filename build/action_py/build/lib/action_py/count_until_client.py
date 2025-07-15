#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from my_robot_interface.action import CountUntil

class CountUntilClient(Node):
    def __init__(self):
        super().__init__('count_until_client')
        self.get_logger().info('Count Until client has been started.')
        self.count_until_client = ActionClient(self, CountUntil, 'count_until')

    def send_goal(self, target_number, period):
        # waite for the server
        self.count_until_client.wait_for_server()

        #create a goal
        goal =CountUntil.Goal()
        goal.target_number = target_number
        goal.period = period

        #send the goal
        self.get_logger().info(f'Sending goal: target_number={target_number}, period={period}')
        self.count_until_client.send_goal_async(goal)

        
def main(args=None):
    rclpy.init(args=args)
    node = CountUntilClient()
    node.send_goal(target_number=5, period=1.0)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node has been stopped.')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
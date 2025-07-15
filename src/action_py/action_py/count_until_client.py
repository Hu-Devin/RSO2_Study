#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle
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
        self.count_until_client.\
            send_goal_async(goal).\
            add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        self.goal_handle_ : ClientGoalHandle = future.result()
        if self.goal_handle_.accepted:
            self.get_logger().info('Goal accepted by server, waiting for result...')
            self.goal_handle_.get_result_async().\
                add_done_callback(self.result_callback)
    
    def result_callback(self, future):
        result = future.result().result 
        self.get_logger().info(f'Goal completed! Final count: {result.reached_number}')
        
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
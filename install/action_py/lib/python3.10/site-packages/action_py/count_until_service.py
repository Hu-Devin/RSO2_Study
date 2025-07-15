#!/usr/bin/env python3
import rclpy
import time
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle
from my_robot_interface.action import CountUntil

class CountUntilServiceNode(Node):
    def __init__(self):
        super().__init__('count_until_service')
        self.get_logger().info('Count Node has been started.')
        self.count_until_service = ActionServer(
            self, 
            CountUntil, 
            'count_until',
            execute_callback=self.execute_callback
            )
    def execute_callback(self, goal_handle:ServerGoalHandle):
        # Get request from goal
        target_number = goal_handle.request.target_number
        period = goal_handle.request.period

        #Execute the action
        self.get_logger().info(f'Starting count until {target_number} with period {period} seconds.')
        count =0
        for i in range(target_number):
            time.sleep(period)
            count += 1
            self.get_logger().info(f'Count: {count}')
            # Publish feedback
            # goal_handle.publish_feedback(CountUntil.Feedback(count=count))
        # Once done, set goal
        goal_handle.succeed()

        #send result
        result = CountUntil.Result()
        result.reached_number = count
        return result

def main(args=None):
    rclpy.init(args=args)
    node = CountUntilServiceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node stopped cleanly.')
    except Exception as e:
        node.get_logger().error(f'Error: {e}')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
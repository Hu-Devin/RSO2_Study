#!/usr/bin/env python3
import rclpy
import time
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.action.server import ServerGoalHandle
from my_robot_interface.action import CountUntil
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

class CountUntilServiceNode(Node):
    def __init__(self):
        super().__init__('count_until_service')
        self.get_logger().info('Count Node has been started.')
        self.count_until_service = ActionServer(
            self, 
            CountUntil, 
            'count_until',
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            execute_callback=self.execute_callback,
            callback_groups=ReentrantCallbackGroup())


    def goal_callback(self, goal_request: CountUntil.Goal):
        self.get_logger().info(f'Received goal request: target_number={goal_request.target_number}, period={goal_request.period}')
        # Validate the goal request
        if goal_request.target_number <= 0:
            self.get_logger().error('Rejecting the goal: target_number must be greater than 0.')
            return GoalResponse.REJECT
        self.get_logger().info('Accepting the goal request.')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle:ServerGoalHandle):
        self.get_logger().info('Received cancel request.')
        # Here you can handle the cancel request if needed
        # For now, we just return ACCEPT to allow cancellation
        return CancelResponse.ACCEPT # or CancelResponse.REJECT

    def execute_callback(self, goal_handle:ServerGoalHandle):
        # Get request from goal
        target_number = goal_handle.request.target_number
        period = goal_handle.request.period

        #Execute the action
        self.get_logger().info(f'Starting count until {target_number} with period {period} seconds.')
        # add feedback
        feedback = CountUntil.Feedback()
        count =0
        # Initialize the result
        result = CountUntil.Result()
        result.reached_number = count
        for i in range(target_number):
            if goal_handle.is_cancel_requested:
                self.get_logger().info('Goal has been cancelled.')
                goal_handle.canceled() # or goal_handle.abort()
                result.reached_number = count
                return result
            time.sleep(period)
            count += 1

            feedback.current_number = count
            goal_handle.publish_feedback(feedback)
            self.get_logger().info(f'Count: {count}')
            # Publish feedback
            # goal_handle.publish_feedback(CountUntil.Feedback(count=count))
        # Once done, set goal success
        goal_handle.succeed()
        # set goal abort
        #goal_handle.abort()

        #send result
        result.reached_number = count
        return result

def main(args=None):
    rclpy.init(args=args)
    node = CountUntilServiceNode()
    try:
        rclpy.spin(node, MultiThreadedExecutor())
    except KeyboardInterrupt:
        node.get_logger().info('Node stopped cleanly.')
    except Exception as e:
        node.get_logger().error(f'Error: {e}')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle, GoalStatus
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
            send_goal_async(goal,feedback_callback=self.goal_feedback_callback).\
            add_done_callback(self.goal_response_callback)

        #send a cancel request 2 seconds later
        self.timer = self.create_timer(2.0, self.cancel_goal)
    
    def cancel_goal(self):
        self.timer.cancel()
        if self.goal_handle_ is not None:
            self.get_logger().info('Sending cancel request...')
            self.goal_handle_.cancel_goal_async()
            self.timer.cancel()
        else:
            self.get_logger().error('No goal handle available to cancel.')

    def goal_response_callback(self, future):
        self.goal_handle_ : ClientGoalHandle = future.result()
        if self.goal_handle_.accepted:
            self.get_logger().info('Goal accepted by server, waiting for result...')
            self.goal_handle_.get_result_async().\
                add_done_callback(self.result_callback)
        else:
            self.get_logger().error('Goal was rejected by server.')
    
    def result_callback(self, future):
        status = future.result().status
        result = future.result().result 
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f'Goal succeeded ')
        elif status == GoalStatus.STATUS_ABORTED:
            self.get_logger().error(f'Goal Aborted ')
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info(f'Goal was canceled ')

        self.get_logger().info(f'Final count: {result.reached_number}')

    def goal_feedback_callback(self, feedback_msg):
        number = feedback_msg.feedback.current_number
        self.get_logger().info(f'Current count: {number}')

    

def main(args=None):
    rclpy.init(args=args)
    node = CountUntilClient()
    node.send_goal(target_number=6, period=1.0)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node has been stopped.')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
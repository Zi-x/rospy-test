#!  /usr/bin/env python
#coding=utf-8

import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class mylidar():
    def __init__(self):
        self.GOING_SPEED = 0.11 #小车x轴速度
        self.LIDAR_ERR = 0.1
        self.STOP_DISTANCE = 0.3  #20厘米的时候停止
        self._cmd_pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)
        self.rate = rospy.Rate(30)
        self.obstacle()

    def get_scan(self):
        msg = rospy.wait_for_message("scan", LaserScan)
        self.scan_filter = []
        # for i in range(360):
        #     if i <= 15 or i > 345:
        #         if msg.ranges[i] >= self.LIDAR_ERR: 
        #             self.scan_filter.append(msg.ranges[i])
        for i in range(0,15):
            if msg.ranges[i] >= self.LIDAR_ERR: 
                self.scan_filter.append(msg.ranges[i])
    def obstacle(self):
        self.twist = Twist()

        while not rospy.is_shutdown():
            self.get_scan()

            if min(self.scan_filter) < self.STOP_DISTANCE - self.STOP_DISTANCE/10:
                self.twist.linear.x = -self.GOING_SPEED
                self.twist.angular.z = 0.0
                self._cmd_pub.publish(self.twist)
                rospy.loginfo('Stop!')
            elif min(self.scan_filter) > self.STOP_DISTANCE + self.STOP_DISTANCE/10:
                self.twist.linear.x = self.GOING_SPEED
                self.twist.angular.z = 0.0
                self._cmd_pub.publish(self.twist)
                rospy.loginfo('Stop!')
            else:
                self.twist.linear.x = 0.0
                self.twist.angular.z = 0.0
                rospy.loginfo('distance of the obstacle : %f', min(self.scan_filter))

            self._cmd_pub.publish(self.twist)
            self.rate.sleep()

def main():
    rospy.init_node('turtlebot_scan')
    try:
        mylidar1 = mylidar()
    except rospy.ROSInterruptException:
        pass

if __name__ == '__main__':
    main()

#!  /usr/bin/env python

import PyKDL
import rospy
from geometry_msgs.msg import *
from nav_msgs.msg import Odometry
from math import *

current_position = Point()
target_yaw = 72
target_distance = 0.6

def quat_to_angle(quat):
  rot = PyKDL.Rotation.Quaternion(quat.x, quat.y, quat.z, quat.w)
  return rot.GetRPY()[2]

def get_odom(data):
    global current_position,current_yaw
    current_position = data.pose.pose.position
    current_yaw = quat_to_angle(data.pose.pose.orientation)
    current_yaw = degrees(current_yaw)

def cmd_vel_pub():
    global target_distance,state
    rospy.init_node('fiveside',anonymous=False)
    cmd_pub  = rospy.Publisher('cmd_vel',Twist,queue_size = 10)
    odom_sub = rospy.Subscriber('odom',Odometry,get_odom)
    rate = rospy.Rate(20)
    twist = Twist()
    rospy.loginfo('fiveside begin!')
    rospy.sleep(5)
    
    while not rospy.is_shutdown():
        start_postion = current_position
        start_yaw = current_yaw
        state = "line"
        while True:
            error_distance = target_distance - sqrt((current_position.x - start_postion.x)**2 + \
            (current_position.y - start_postion.y)**2)
            error_yaw = target_yaw-(current_yaw - start_yaw)
            if(error_yaw<=72 and error_yaw >= 0):
                error_yaw=error_yaw
            if(error_yaw>72 or error_yaw<0):
                error_yaw = error_yaw - 360
            if(state == "line"):
                if (error_distance>0.1):
                    twist.linear.x= 0.2
                    cmd_pub.publish(twist)
                if(error_distance <= 0.1):
                    twist.linear.x = 0
                    cmd_pub.publish(twist)
                    state = "yaw"
            if(state == "yaw"):
                if(error_yaw<=72 and error_yaw >1):
                    twist.linear.x = 0.1
                    twist.angular.z = 1
                    rospy.loginfo(error_yaw)
                    cmd_pub.publish(twist)
                if(error_yaw <=1):
                    rospy.loginfo(error_yaw)
                    twist.linear.x = 0
                    twist.angular.z =0
                    cmd_pub.publish(twist)
                    state = "over"
            if(state =="over"):
                rospy.loginfo("break")
                break
            rate.sleep()         

if __name__ == '__main__':
    try:
        cmd_vel_pub()
    except rospy.ROSInternalException:
        pass
#!  /usr/bin/env python
#coding=utf-8

import PyKDL
import rospy
from geometry_msgs.msg import *
from nav_msgs.msg import Odometry
from math import *

current_position = Point()
target_yaw = 72     ##目标偏航角
target_distance = 0.7
DISTANCE_VALVE = 0.1
DEGREE_VALVE = 1
YAW_LINEAR_X = 0.1
YAW_LINEAR_Z = 1
LINE_LINEAR_X = 0.2
RATE = 20

def quat_to_angle(quat):
  rot = PyKDL.Rotation.Quaternion(quat.x, quat.y, quat.z, quat.w)
  return rot.GetRPY()[2]

def get_odom(data):
  global current_position,current_yaw
  current_position = data.pose.pose.position
  current_yaw = quat_to_angle(data.pose.pose.orientation)
  current_yaw = degrees(current_yaw)

def line():
    if (error_distance > DISTANCE_VALVE):
        twist.linear.x = LINE_LINEAR_X
        cmd_pub.publish(twist)
        return state
    if(error_distance <= DISTANCE_VALVE):
        twist.linear.x = 0
        cmd_pub.publish(twist)
        return 'yaw'
def yaw():
    if(error_yaw <= target_yaw and error_yaw > DEGREE_VALVE):
        twist.linear.x = YAW_LINEAR_X
        twist.angular.z = YAW_LINEAR_Z
        rospy.loginfo(error_yaw)
        cmd_pub.publish(twist)
        return state
    if(error_yaw <= DEGREE_VALVE):
        rospy.loginfo(error_yaw)
        twist.linear.x = 0
        twist.angular.z =0
        cmd_pub.publish(twist)           
        return 'over'

def default():
    rospy.loginfo("switch error!")

def cmd_vel_pub():
    global target_distance,state,twist,error_distance,error_yaw,cmd_pub
    switch = {'line':line,'yaw':yaw}    #字典方式实现switch
    rospy.init_node('fiveside',anonymous=False)
    cmd_pub  = rospy.Publisher('cmd_vel',Twist,queue_size = 10)
    odom_sub = rospy.Subscriber('odom',Odometry,get_odom)
    rate = rospy.Rate(RATE)
    twist = Twist()
    rospy.loginfo('fiveside begin!')
    rospy.sleep(0.1)
    while not rospy.is_shutdown():
        start_postion = current_position    #重置结束点为新循环的起点坐标
        start_yaw = current_yaw    #重置结束方位角为新循环的起点角
        state = 'line'      #重置state为直线
        while True:     #以一个line加yaw为一个循环
            error_distance = target_distance - sqrt((current_position.x - start_postion.x)**2 + \
            (current_position.y - start_postion.y)**2)  #距离误差
            error_yaw = target_yaw-(current_yaw - start_yaw)  #目标角误差
            #用此方法解决跳跃点问题
            if(error_yaw<=72 and error_yaw >= 0):
                error_yaw=error_yaw
            if(error_yaw>72 or error_yaw<0):
                error_yaw = error_yaw - 360
            state = switch.get(state,default)()#执行state对应函数并获取新的state
            if(state =='over'):     #如果error_yaw小于设置值则跳出true循环
                rospy.loginfo("break")
                break
            rate.sleep()

if __name__ == '__main__':
  try:
    cmd_vel_pub()
  except rospy.ROSInternalException:
    pass
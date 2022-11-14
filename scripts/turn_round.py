#!  /usr/bin/env python
import PyKDL
from nav_msgs.msg import Odometry
import rospy
from geometry_msgs.msg import *
from math import*
def quat_to_angle(quat):
  rot = PyKDL.Rotation.Quaternion(quat.x, quat.y, quat.z, quat.w)
  return rot.GetRPY()[2]

def get_odom(data):
    
    global current_yaw
    #current_quater  = data.pose.pose.orientation
    
    current_yaw = quat_to_angle(data.pose.pose.orientation)
    current_yaw = degrees(current_yaw)
    rospy.loginfo(current_yaw)

def cmd_vel_pub():
    rospy.init_node('turn_round',anonymous=False)
    cmd_pub  = rospy.Publisher('cmd_vel',Twist,queue_size=10)
    odom_sub  = rospy.Subscriber('odom',Odometry,get_odom)
    rate = rospy.Rate(10)
    twist = Twist()
    rospy.loginfo('turn round begin!')
    '''
    for i in range(1,20):
        
        twist.linear.x= 0.1
        twist.angular.z=0.5
        
        rospy.loginfo(i)
        cmd_pub.publish(twist)
        rospy.sleep(0.1)
    '''
    while not rospy.is_shutdown():
        twist.linear.x= 0.1
        twist.angular.z=0.5
        
        cmd_pub.publish(twist)
        rate.sleep()  
    
if __name__ == '__main__':
    try:
        cmd_vel_pub()
    except rospy.ROSInternalException:
        pass
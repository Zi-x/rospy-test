#!  /usr/bin/env python

import rospy
from geometry_msgs.msg import *
from nav_msgs.msg import Odometry,Path
from math import *

path_pub = rospy.Publisher('show_path',Path,queue_size=10)
path = Path()
def get_odom(data):
    global path,path_pub

    this_pose_stamped = PoseStamped()
    this_pose_stamped.pose.position = data.pose.pose.position
    this_pose_stamped.pose.orientation = data.pose.pose.orientation
    this_pose_stamped.header.frame_id = data.header.frame_id
    this_pose_stamped.header.stamp = data.header.stamp

    path.header.frame_id = this_pose_stamped.header.frame_id
    path.header.stamp = this_pose_stamped.header.stamp
    path.poses.append(this_pose_stamped)
    path_pub.publish(path)

def linstener():
    rospy.init_node('show_path',anonymous=False)
    odom_sub = rospy.Subscriber('odom',Odometry,get_odom)
    rospy.loginfo('start show path!')
    #rospy.spin()
    rospy.sleep(100)


if __name__ == '__main__':
  try:
    linstener()
  except rospy.ROSInternalException:
    pass
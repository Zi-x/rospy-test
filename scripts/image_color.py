#!  /usr/bin/env python
#coding=utf-8

import psutil
from cv_bridge import *
import rospy
from sensor_msgs.msg import Image
from geometry_msgs.msg import *
from nav_msgs.msg import Odometry
from math import *
import cv2
import numpy as np
import pytesseract
from PIL import Image as PILImage
import PIL.ImageOps



class image_converter:
    def __init__(self):    
        # 创建cv_bridge，声明图像的发布者和订阅者
        self.image_pub = rospy.Publisher("color_image_test", Image, queue_size=1)
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("/image_raw", Image, self.callback)
        self.mask_pub = rospy.Publisher("/mask_image", Image, queue_size=1)
        self.result_pub = rospy.Publisher("/result_image", Image, queue_size=1)
        self.pub_cmd = rospy.Publisher('cmd_vel', Twist, queue_size=5)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.lower_red = np.array([0, 127, 128])  # 红色阈值下界
        self.higher_red = np.array([10, 255, 255])  # 红色阈值上界
        self.lower_yellow = np.array([15, 230, 230])  # 黄色阈值下界
        self.higher_yellow = np.array([35, 255, 255])  # 黄色阈值上界
        self.lower_blue = np.array([85,240,140])
        self.higher_blue = np.array([100,255,165])
        self.pointx = -1
        self.pointy = -1

    def initTable(self,threshold = 72): #大于这个值为白
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)
        return  table

    def callback(self,data):
        # 使用cv_bridge将ROS的图像数据转换成OpenCV的图像格式
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print (e)
        img_hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        mask_red_fiter = cv2.inRange(img_hsv, self.lower_red, self.higher_red)  # 可以认为是过滤出红色部分，获得红色的掩膜
        mask_red = cv2.medianBlur(mask_red_fiter, 7)  # 中值滤波
        cv2.imshow('img0',mask_red)
        cv2.waitKey(0)
        #close消黑洞，open消白点        
        kernel0 = np.ones((12,12),np.uint8)
        mask_red = cv2.morphologyEx(mask_red,cv2.MORPH_CLOSE,kernel0)
        #cv2.imshow('img1',mask_red)
        #cv2.waitKey(0)
        kernel = np.ones((9,9),np.uint8)
        mask_red = cv2.morphologyEx(mask_red,cv2.MORPH_OPEN,kernel)
        cv2.imshow('img2',mask_red)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        #rospy.loginfo(isinstance(mask_red, np.ndarray))
        #cv2.imshow('img',mask_red)
        #cv2.waitKey(0)
        img,cnts1, hierarchy1 = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 轮廓检测 #红色
        
        for cnt in cnts1:
            (x, y, w, h) = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
            
            #img = img.convert('1')
            #img = img.point(self.initTable(), '1')
            
            
            
            codeimg = cv_image[y:y+h,x:x+w] #y.x
            grayImage = cv2.cvtColor(codeimg,cv2.COLOR_BGR2GRAY)
            fan,codeimg= cv2.threshold(grayImage,107,255,cv2.THRESH_BINARY)
            
            codeimg = PILImage.fromarray(codeimg)
            # codeimg = cv2.cvtColor(codeimg,cv2.COLOR_BGR2RGB)
            # codeimg = PILImage.fromarray(codeimg)
            #process_list0 = []
            # for proc in psutil.process_iter():
            #     process_list0.append(proc)
            # codeimg.show()
            # rospy.sleep(0.2)
            # for proc in psutil.process_iter():
            #     if not proc in process_list0:
            #         proc.kill()
            # codeimg = codeimg.convert('L')
            # #codeimg = PIL.ImageOps.invert(codeimg)
            # codeimg = codeimg.point(self.initTable(), '1')
            # codeimg = codeimg.resize((250,250*h/w))

            process_list = []
            for proc in psutil.process_iter():
                process_list.append(proc)
            codeimg.show()
            rospy.sleep(0.2)
            for proc in psutil.process_iter():
                if not proc in process_list:
                    proc.kill()   
            rospy.loginfo(w/float(h))
            if(w/float(h)>=1.0 and (w/float(h))<2.4 and w + h > 40 ):
                try:
                    code = pytesseract.image_to_string(codeimg,lang='eng',config="--psm 6 \
                    -c tessedit_char_whitelist=ABCDEFGLHR")
                    rospy.loginfo(code)
                    cv2.rectangle(cv_image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 将检测到的颜色框起来
                    cv2.putText(cv_image, 'red', (x, y - 5), self.font, 0.7, (0, 0, 255), 2)
                    if(code =="AB"):
                        
                        cv2.circle(cv_image, (x+w/2, y+h/2), 7, (0,255,0), -1)
                        rospy.loginfo("break")
                        self.pointx = x+w/2
                        self.pointy = y+h/2
                        break
                    else:
                        self.pointx = -1
                        self.pointy = -1
                except:
                    rospy.loginfo("pytesseract error")
        #if(self.pointx > 0 and self.pointy >0):
            #self.twist_calculate(self.pointx,self.pointy,cv_image.shape[1]/2)

        try:
            img_msg = self.bridge.cv2_to_imgmsg(cv_image, "bgr8")
            img_msg.header.stamp = rospy.Time.now()
            self.image_pub.publish(img_msg)

        except CvBridgeError as e:
            print (e)    
            
    def twist_calculate(self,pointx,pointy,width):
        self.twist = Twist()
        self.twist.linear.x = 0
        self.twist.angular.z = 0
        if pointx/float(width) > 0.95 and pointx/float(width) < 1.05:
            self.twist.linear.x = 0.1
        else:

            self.twist.linear.x = 0.1
            self.twist.angular.z = ((width - pointx) / float(width)) / 2.0  #2
            rospy.loginfo(self.twist.angular.z)
            # if abs(self.twist.angular.z) < 0.2:
            #     self.twist.linear.x = 0.2 - self.twist.angular.z/2.0
            # else:
            #     self.twist.linear.x = 0.1
        self.pub_cmd.publish(self.twist)
    
            
        

if __name__ == '__main__':
    try:
        # 初始化ros节点
        rospy.init_node("color_detect_test")
        rospy.loginfo("Starting fllow_color_text node")
        image_converter()
        rospy.spin()
    except KeyboardInterrupt:
        print ("Shutting down cv_bridge_test node.")
        cv2.destroyAllWindows()





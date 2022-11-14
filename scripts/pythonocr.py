#!  /usr/bin/env python
#coding=utf-8

import cv2
from math import *
import pytesseract
from PIL import Image
import numpy as np
import PIL.ImageOps
'''
def initTable(threshold=140):
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    return table

im = Image.open("/home/orangeubuntu/yzm.jpg")
#图片的处理过程
im = im.convert('L')
binaryImage = im.point(initTable(), '1')

im1 = binaryImage.convert('L')
im2 = PIL.ImageOps.invert(im1)
im3 = im2.convert('1')
im4 = im3.convert('L')
im4.show()
#将图片中字符裁剪保留
box = (30,10,90,28) 

region = im4.crop(box)  

#将图片字符放大
out = region.resize((120,38)) 
asd = pytesseract.image_to_string(im4)
print (asd)
'''
def initTable(threshold = 66): #大于这个值为白
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    return table

img = Image.open("/home/orangeubuntu/AB.png")
img2 = cv2.imread("/home/orangeubuntu/AB.png")
img = img.convert('L')
img2 = img2[0:80,0:40] #y.x
cv2.imshow('img2',img2)
cv2.waitKey(0)
#img = img.convert('1')
img = img.point(initTable(), '1')
img.show()
code = pytesseract.image_to_string(img,lang='eng',config='--psm 6')
print (code)

print(pytesseract.__version__)










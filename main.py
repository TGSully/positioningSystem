import numpy as np
import cv2
import math
import socket
import sys
import ctypes

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = ("127.0.0.1" , 8000)
sock.connect(address)

def imageProcess(image):
    lower = (125, 0 ,200)
    upper = (130, 50, 255)

    # lower_pingpong = ()
    # upper_pingpong = 

    
    blur = cv2.GaussianBlur(image, (11,11), 0)
    hsvImage = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    mask =  cv2.inRange(hsvImage, lower, upper)
    mask = cv2.erode(mask, None , iterations = 2)
    mask = cv2.dilate(mask, None , iterations = 2)
    return mask

def getContour(image):
    frame, contours, h = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contour = None
    great_circularity = 0
    for con in contours:
        area = cv2.contourArea(con)
        perimeter = cv2.arcLength(con, True)
        if area < 1000:
            continue
        if perimeter == 0:
            continue
        circularity = 4*math.pi*(area/ (perimeter**2))
        if circularity > great_circularity:
            great_circularity = circularity
            contour = con
    # print(great_circularity)
    return contour

def houghCircle(image):
    circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1, 
        minDist=500,
        param1=70,
        param2=11,
        minRadius=20,
        maxRadius=50)

    # convert circles into expected type
    if (circles is None):
        return []

    circles = np.uint16(np.around(circles))
    return circles


cap = cv2.VideoCapture("psmovedemo.mov")
#cap = cv2.VideoCapture(0)

while(cap.isOpened()):
    ret, rgb = cap.read()
    if (ret == False):
        break
    
    small = cv2.resize(rgb, (0,0), fx = 0.5, fy = 0.5)
    height, width, _ = small.shape 

    frame = imageProcess(small)
    # frame = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    con = getContour(frame)
    # cv2.drawContours(small, [con], -1, (0,255,0), 3)
    if con is not None:
        ((x,y),radius) = cv2.minEnclosingCircle(con)
        cv2.circle(small,(int(x),int(y)), int(radius) ,(0,0,255),2)
        centerX = width/2
        centerY = height/2
        x = ((x-centerX)/(width)) * 255
        y = ((centerY-y)/(height)) * 255
        # x = ((x-(width/2))/(width/2)) * 127
        # y = ((y-(height/2))/(height/2)) * 127
        radius = ((36-radius)/72) * 255

        print(x , y, radius)

        data = bytearray()
        data.append(ctypes.c_uint8(int(x)).value)
        data.append(ctypes.c_uint8(int(y)).value)
        data.append(ctypes.c_uint8(int(radius)).value)
        sock.send(data)
        # print(type(x))

    # circles = houghCircle(frame)
    # #print(len(circles))
    # if (len(circles) == 0):
    #     continue
    # for i in circles[0,:]:
    #     # draw the outer circle
    #     cv2.circle(small,(i[0],i[1]),i[2],(255,0,0),2)
    #     # draw the center of the circle
    #     ###cv2.circle(circles_im,(i[0],i[1]),2,(0,0,255),3)

    cv2.imshow('frame', small)
    # cv2.imshow('frame2', frame)
    

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
#sock.close()
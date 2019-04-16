#import picamera
#import picamera.array
import time
import cv2
import numpy as np
def perspective_transform(img):
    imshape = img.shape
    vertices = np.array([[(0.55*imshape[1], 0.40*imshape[0]), (imshape[1], imshape[0]), (0, imshape[0]), (.45*imshape[1],0.40*imshape[0])]], dtype = np.float32)
    src = np.float32(vertices)
    dst = np.float32([[img.shape[1], 0], [img.shape[1], img.shape[0]], [0*img.shape[1], img.shape[0]], [0*img.shape[1], 0]])
    
    M = cv2.getPerspectiveTransform(src, dst)
    Minv = cv2.getPerspectiveTransform(dst, src)
    img_size = (imshape[1], imshape[0])
    perspective_img = cv2.warpPerspective(img,M,img_size,flags=cv2.INTER_LINEAR)
    #print(vertices)
    #cv2.fillPoly(perspective_img, vertices, 255)
    return perspective_img, Minv
    
#camera = picamera.PiCamera()
#camera.resolution = (640,480)
#camera.framerate=32
#rawCapture = picamera.array.PiRGBArray(camera, size=(640, 480))
#Let camera warm up
time.sleep(0.1)

cap = cv2.VideoCapture('demo2.avi')
while(cap.isOpened()):
    ret,frame=cap.read()
#for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    img=frame
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges=cv2.Canny(gray, 75, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50)
    if ret==True:
        cv2.imshow("Frame",frame)
    for line in lines:
        x1, y1, x2, y2= line[0]
        
      # cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    ret,binarization=cv2.threshold(gray,190,255,cv2.THRESH_BINARY)
    binarization2, MinV = perspective_transform(binarization)
    
    cv2.imshow("Binarizare2", binarization2)
    cv2.imshow("Edges", edges)
    cv2.imshow("Image", img)
    cv2.imshow("binarizare",binarization)
    cv2.waitKey(1)
    #rawCapture.truncate(0)
cv2.release()
cv2.destroyAllWindows()

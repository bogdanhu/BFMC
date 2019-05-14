import cv2
import numpy as np
from StopAndPark import stopOrPark

#cap = cv2.VideoCapture(0) # seteaza camera implicita
cap = cv2.VideoCapture('camera.avi')
FoundBlue = False
while True:
    none, frame = cap.read()
    if stopOrPark(frame):
        print("E ceva aici")
    cv2.imshow("Frame", frame)  # afiseaza ce se inregistreaza live.
    key = cv2.waitKey(0)
    if key == 27:
        break

"""
while False: # loop infinit
    _, frame = cap.read() # incepe sa filmeze
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # converteste culorile din format BGR(Blue, Green, Red) in HSV

    lower_red = np.array([170, 50, 50]) # 170 50 50
    upper_red = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red)

    mask = mask1
    kernel = np.ones((1, 1), np.uint8)
    mask = cv2.erode(mask, kernel)

    contours, none = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) #gaseste contururile unor posibile forme
    for cnt in contours:
        area = cv2.contourArea(cnt)
        approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True) # aproximeaza suprafata
        x = approx.ravel()[0]

        if area > 100:
            if  len(approx) == 8: # 8 este cazul pe care il cautam, semnul de STOP este un octogon
                print("STOP")
                #cv2.putText(frame, "STOP", (x, y), font, 1, (0, 0, 0))
                x, y, width, height = cv2.boundingRect(cnt)
                roi = frame[y:y + height+100,x:x + width+100]
                r_roi = cv2.resize(roi, (500, 500))
                cv2.imshow("Regiune de interes", r_roi)


                MIN_CONTOUR_AREA = 80
                img = r_roi
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                blured = cv2.blur(gray, (5, 5), 0)
                img_thresh = cv2.adaptiveThreshold(blured, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11, 2)
                Contours, none = cv2.findContours(img_thresh, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)


    cv2.imshow("Frame", frame) # afiseaza ce se inregistreaza live.
    cv2.imshow("Mask", mask) # afiseaza fereastra unde se elimina toate culorile inafara de nuantele de rosu

    key = cv2.waitKey(0)
    if key == 27:
        break
"""
cap.release()
cv2.destroyAllWindows()

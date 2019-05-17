import cv2
import numpy as np
from ShapeDetection import ShapeDetector
import imutils
import os

cap = cv2.VideoCapture('cameraG.avi')
os.system('cls' if os.name == 'nt' else 'clear')
ExistaBandaDiscontinua=False

def Analizeaza(frame):
    global ExistaBandaDiscontinua
    img = frame
    mask = np.ones(img.shape, dtype=np.uint8)
    mask.fill(255)

    # points to be cropped
    roi_corners = np.array([[(160, 160), (480, 160), (640, 300), (640, 400), (0, 400), (0, 300)]], dtype=np.int32)
    # fill the ROI into the mask
    cv2.fillPoly(mask, roi_corners, 0)
    masked_image = cv2.bitwise_or(img, mask)

    # and threshold it
    # alternativa este masked_image
    gray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 120, 250, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    cv2.imshow("zz", thresh)
    # find contours in the thresholded image and initialize the
    # shape detector
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)

    cnts = imutils.grab_contours(cnts)
    sd = ShapeDetector()

    # loop over the contours
    NrPatratele = 0

    for c in cnts:
        # compute the center of the contour, then detect the name of the
        # shape using only the contour
        M = cv2.moments(c)
        if (M["m00"] < 1):
            continue
        cX = int((M["m10"] / M["m00"]))
        cY = int((M["m01"] / M["m00"]))

        shape = sd.detect(c)
        area = cv2.contourArea(c)

        if area > 250 or area < 10:
            continue
        if shape == "unidentified":
            continue
        NrPatratele = NrPatratele + 1
        # print(str(area))
        # multiply the contour (x, y)-coordinates by the resize ratio,
        # then draw the contours and the name of the shape on the image
        c = c.astype("float")
        c = c.astype("int")
        cv2.drawContours(img, [c], -1, (0, 255, 0), 2)
        cv2.putText(img, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 2)

        # show the output image
    if (NrPatratele > 2):
        ExistaBandaDiscontinua = True
        return 1
    if (ExistaBandaDiscontinua and NrPatratele < 2):
        cv2.putText(img, "Avem terminat banda discontinua: ", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                    (250, 250, 250), 2)
        print("Am terminat banda discontinua - o luam la dreapta/stanga")
        ExistaBandaDiscontinua = False
        return -1
    return 0

    #cv2.imshow("image", img)

    #cv2.imshow("cropped", masked_image)

    #cv2.waitKey(0)


while (cap.isOpened()):
    ret, frame = cap.read()
    if ret is False:
        break
    img = frame


    AvemBandaDiscontinua=Analizeaza(frame)
    if (AvemBandaDiscontinua==True):
        cv2.putText(img, "Avem banda discontinua: ", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                    (250, 250, 250), 2)
    if(AvemBandaDiscontinua==-1):
        cv2.putText(img, "Avem banda discontinua: ", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                    (250, 250, 250), 2)
    cv2.imshow("image", img)
    cv2.waitKey(0)
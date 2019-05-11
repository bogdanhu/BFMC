import numpy as np
import cv2

font = cv2.FONT_HERSHEY_COMPLEX
def stopOrPark(frame):
    #frame = cv2.resize(frame, None, fx=0.5, fy=0.6, interpolation=cv2.INTER_CUBIC)
    frame = frame[0:350, 320:640]
    counterBlue = 0
    counterRed = 0
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_blue = np.array([90, 80, 50])
    upper_blue = np.array([110, 255, 255])
    maskBlue = cv2.inRange(hsv, lower_blue, upper_blue)

    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red)

    lower_red = np.array([170, 50, 50])  # 170 50 50
    upper_red = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red, upper_red)

    mask = mask1 + mask2
    kernel = np.ones((1, 1), np.uint8)
    maskRed = cv2.erode(mask, kernel)

    lower_white = np.array([0, 0, 0])
    upper_white = np.array([0, 0, 255])
    maskWhite = cv2.inRange(hsv, lower_white, upper_white)


    kernelBlue = np.ones((1, 1), np.uint8)
    maskBlue = cv2.erode(maskBlue, kernelBlue)
    contoursRed, none = cv2.findContours(maskRed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contoursBlue, none = cv2.findContours(maskBlue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contoursWhite, none = cv2.findContours(maskWhite, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contoursRed:
        haveWhite = False
        area = cv2.contourArea(cnt)
        approx = cv2.approxPolyDP(cnt, 0.015 * cv2.arcLength(cnt, True), True)  # aproximeaza suprafata

        if  area > 400:
            counterRed = counterRed + 1
            for cnt2 in contoursWhite:
                approxWhite = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt2, True), True)  # aproximeaza suprafata
                if len(approxWhite) > 5:
                    haveWhite = True
            if counterRed > 1 and haveWhite is True:
                cv2.drawContours(frame, [approx], 0, (0, 0, 0), 1)
                cv2.imshow("ROSU", frame)
                return True

    # ALBASTRU
    for cnt in contoursBlue:
        haveWhite = False
        area = cv2.contourArea(cnt)
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)  # aproximeaza suprafata

        if area > 500:
            counterBlue = counterBlue + 1
            for cnt2 in contoursWhite:
                approxWhite = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt2, True), True)  # aproximeaza suprafata
                if len(approxWhite) > 5:
                    haveWhite = True
            if counterBlue > 1 and haveWhite:
                cv2.drawContours(frame, [approx], 0, (0, 0, 0), 1)
                cv2.imshow("BLUE", frame)
                print(area)
                return True

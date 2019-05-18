import numpy as np
import cv2
import imutils

font = cv2.FONT_HERSHEY_COMPLEX

def stopOrPark(frame,AmParcat): #return AmSTOP,AmParcat
    #frame = cv2.resize(frame, None, fx=0.5, fy=0.6, interpolation=cv2.INTER_CUBIC)
    frame = frame[0:350, 320:640]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red)

    lower_red = np.array([170, 50, 50])  # 170 50 50
    upper_red = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red, upper_red)


    mask = mask1 + mask2
    kernel = np.ones((1, 1), np.uint8)
    #maskRed = cv2.erode(mask, kernel)

    lower_white = np.array([0, 0, 0])
    upper_white = np.array([0, 0, 255])
    maskWhite = cv2.inRange(hsv, lower_white, upper_white)
    if imutils.is_cv3():
        imagex,contoursRed, none = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contoursRed, none = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if imutils.is_cv3() :
        imagex,contoursWhite, none = cv2.findContours(maskWhite, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contoursWhite, none = cv2.findContours(maskWhite, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    counterRed = 0
    for cnt in contoursRed:
        haveWhite = False
        area = cv2.contourArea(cnt)
        approx = cv2.approxPolyDP(cnt, 0.015 * cv2.arcLength(cnt, True), True)  # aproximeaza suprafata

        if  area > 200:
            counterRed = counterRed + 1
            for cnt2 in contoursWhite:
                approxWhite = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt2, True), True)  # aproximeaza suprafata
                if len(approxWhite) > 5:
                    haveWhite = True
            if counterRed > 1 and haveWhite is True:
                cv2.drawContours(frame, [approx], 0, (0, 0, 0), 1)
                cv2.imshow("ROSU", frame)
                print(area)
                return True,False
    ## TODO: verificam orientarea pe GPS
    if not AmParcat:
        # ALBASTRU
        lower_blue = np.array([90, 80, 50])
        upper_blue = np.array([110, 255, 255])
        maskBlue = cv2.inRange(hsv, lower_blue, upper_blue)

        kernelBlue = np.ones((1, 1), np.uint8)#
        counterBlue = 0
        if imutils.is_cv3() :
            nonex,contoursBlue, none = cv2.findContours(maskBlue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else :
            contoursBlue, none = cv2.findContours(maskBlue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)



        for cnt in contoursBlue:
            haveWhite = False
            area = cv2.contourArea(cnt)
            approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)  # aproximeaza suprafata

            if area > 550 and area < 1000:
                counterBlue = counterBlue + 1
                for cnt2 in contoursWhite:
                    approxWhite = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt2, True), True)  # aproximeaza suprafata
                    if len(approxWhite) > 5:
                        haveWhite = True
                if counterBlue > 1 and haveWhite:
                    cv2.drawContours(frame, [approx], 0, (0, 0, 0), 1)
                    cv2.imshow("BLUE", frame)
                    print(area)
                    AmParcat = False,True
                    return AmParcat
    return False,False




if __name__=="__main__":
    cap = cv2.VideoCapture('cameraE.avi')
    counter = 0
    PARCAREDEJA=False
    while (cap.isOpened()) :
        counter = counter + 1
        ret, frame = cap.read()
        if counter < 1500 :
            continue
        EsteStop,EsteParcare=stopOrPark(frame,PARCAREDEJA)
        if EsteParcare:
            PARCAREDEJA=True
        STARE= (EsteStop,EsteParcare)
        print("La cadrul avem starea "+str(PARCAREDEJA))
        cv2.imshow("IMG", frame)
        cv2.waitKey(0)



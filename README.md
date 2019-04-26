# BFMC
boschApp

https://www.dropbox.com/s/83slf9sgkyelphc/demo2.avi?dl=0

Pentru Parcare
==
1. Trebuie gasita o solutie eleganta pentru stari
    1. Starea 1 - gasirea marcajului de Parcare
    2. Starea 2 - activarea comportament parcare laterala
    3. Starea 3 - comportament plecare parcare laterala
    4. Starea 4 - activare comportament reintoarecere la baza
2. Ce facem cu semnul STOP?
    1. Avem STOP - Fata
    2. STOP - Stanga
    3. STOP - FATA
    4. STOP - FATA
    5. STOP - Stanga
    6. am implementat o solutie - insa nu merge cum trebuie


# Am eliminat  

# lower mask (0-10)
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask0 = cv2.inRange(hsv, lower_red, upper_red)

    # upper mask (170-180)
    lower_red = np.array([170, 50, 50])
    upper_red = np.array([180, 255, 255])
binarization2, MinV = perspective_transform(binarization)
cv2.imshow("Binarizare2", binarization2)

    edges = cv2.Canny(gray, 75, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

    # cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # cv2.imshow("Edges", edges)
    #cv2.imshow("Image", img)


# In asteptare
    #copie, Minv25 = perspective_transform(frame)
    #mtx, dist = get_camera_calibration()
    #undist_copy = cv2.undistort(copie, mtx, dist, None, mtx)
    #cv2.imshow("PERSPECTIVA", copie)yt
    #cv2.waitKey(0)
    
    
# Am eliminat asta - 26.04.2019
 RaportIntreBenzi=SectiunePrincipala.MedDistanta/SectiunePrincipala.DistantaBandaFrame
        alphaDegrees = 0
        if (-1 <= RaportIntreBenzi <= 1):
            alphaRadian = np.arccos(RaportIntreBenzi)
            alphaDegrees = np.rad2deg(alphaRadian)
        else:
            print("Nu putem calcula unghiul pt " + str(RaportIntreBenzi))

        
        if (MijlocCamera > (SectiunePrincipala.mijlocCalculat + EroareCentrare)):
            print("O luam spre stanga cu unghiul " + str(alphaDegrees))
        #f.write('2\t' + str(round(alphaDegrees, 2)) + '\n')
        elif (MijlocCamera < (SectiunePrincipala.mijlocCalculat  + EroareCentrare)):
            alphaDegrees = -round(alphaDegrees, 2)
            #$f.write('1\t' + str(round(alphaDegrees, 2)) + '\n')
            print("O luam spre dreapta" + str(alphaDegrees))
        else:
            #f.write('0' + '\n')
            print("Suntem pe centru")


import SerialHandler
import threading
import serial
import time
import sys
import SaveEncoder
global serialHandler
# import picamera
# import picamera.array

# todo1 - calibrare unghi atac camera si salvarea valorii medie in DistantaBanda (o constanta pe care o sa o folosim pentru a determina inclinatia fata de AX
# todo2 - cum intra in curbe
#todo3 - arrowedLine
import time
import cv2
import numpy as np
import math
#from calibration_main import get_camera_calibration
ESTE_PE_MASINA=False
#DISTANTABANDACT = 400 # De ce e 400?
DISTANTABANDACT = 350

def perspective_transform(img):
    imshape = img.shape
    lungimeCadru = 640
    #vertices = np.array([[(0, 0.9 * imshape[0]), (0* imshape[1], 0.5 * imshape[0]), (imshape[1], 0.5 * imshape[0]),
    #                      (imshape[1], 0.9 * imshape[0])]], dtype=np.float32)

    vertices = np.array(((imshape[0] * 2.0 / 3, 0), (imshape[0]*2.0/ 3, lungimeCadru), (imshape[0] * 4.0 / 5, 0), (imshape[0] * 4.0 / 5, lungimeCadru)), dtype=np.float32)
    src = np.float32(vertices)
    dst = np.float32([[img.shape[1], 0], [img.shape[1], img.shape[0]], [0 * img.shape[1], img.shape[0]], [0 * img.shape[1], 0]])

    M = cv2.getPerspectiveTransform(src, dst)
    Minv = cv2.getPerspectiveTransform(dst, src)
    img_size = (imshape[1], imshape[0])
    perspective_img = cv2.warpPerspective(img, M, img_size, flags=cv2.INTER_LINEAR)
    # print(vertices)
    # cv2.fillPoly(perspective_img, vertices, 255)
    return perspective_img, Minv


# camera = picamera.PiCamera()
# camera.resolution = (640,480)
# camera.framerate=32
# rawCapture = picamera.array.PiRGBArray(camera, size=(640, 480))
# Let camera warm up
#time.sleep(0.1)

cap = cv2.VideoCapture('demo.avi')
#cap = cv2.VideoCapture(0)  # pentru camera
#out = cv2.VideoWriter('camera.avi', -1, 20, (640, 480))
counter = 0
DistanteBenzi = np.zeros(0)
#f = open('deplasare.txt', 'w')
# global serialHandler
MedDistanta = 0
CentruImaginar = 0
mijlocCalculat=0
pasAdaptare = 0
global serialHandler
if ESTE_PE_MASINA:
    serialHandler = SerialHandler.SerialHandler("/dev/ttyACM0")
    serialHandler.startReadThread()
while (cap.isOpened()):
    ret, frame = cap.read()
    if ret == False:
        break
    counter = counter + 1
    # print(str(counter))
    LocatieDeInteres = 150  # 1450
    if counter < LocatieDeInteres:
        continue

    # for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    img = frame
    #copie, Minv25 = perspective_transform(frame)
   # mtx, dist = get_camera_calibration()
    #undist_copy = cv2.undistort(copie, mtx, dist, None, mtx)
    #cv2.imshow("PERSPECTIVA", copie)yt
    #cv2.waitKey(0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #gray = abs(255 - gray)

    edges = cv2.Canny(gray, 75, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

    # cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    ret, binarization = cv2.threshold(gray, 190, 255, cv2.THRESH_BINARY)
    binarization2, MinV = perspective_transform(binarization)

    #cv2.imshow("Binarizare2", binarization2)
    # cv2.imshow("Edges", edges)
    #cv2.imshow("Image", img)


    LatimeCadru, lungimeCadru, _ = frame.shape
    cv2.line(img, (0, int(LatimeCadru * 2.0 / 3)), (lungimeCadru, int(LatimeCadru * 2.0 / 3)), (255, 255, 0), 5)
    cv2.line(img, (0, int(LatimeCadru * 4.0 / 5)), (lungimeCadru, int(LatimeCadru * 4.0 / 5)), (0, 255, 0), 5)
    cv2.line(img, (int(lungimeCadru / 2), 0), (int(lungimeCadru / 2), LatimeCadru), (255, 255, 255), 5)
    #if ret == True:
        #cv2.imshow("Frame", frame)

    #  print("Dimensiune imagine:" + str(binarization[160,:].size))
    array = np.argwhere(binarization[int(LatimeCadru * 2.0 / 3), :] > 1)
    interesant = False
    pozitieInteresanta = 0
    interesant2 = False
    pozitieInteresanta2 = 0
    structuri = 0
    structuri2 = 0
    centre = np.zeros(0)
    centre2 = np.zeros(0)
    EroareCentru = 50
    EroareCentruTemporar = 0
    EroareCentru2 = 50
    EroareCentruTemporar2 = 0
    for i in range(1, lungimeCadru):
        if interesant == True:  # ce facem cand e structura extinsa
            if binarization[int(LatimeCadru * 2.0 / 3), i] == 0:
                interesant = False
                if (1 < EroareCentruTemporar < EroareCentru):
                    print("Structuri fals. - Nu salvam valoarea")  # de fapt ar trebui sa recalculam centrul nou
                    continue
                EroareCentruTemporar = 1
                pozitieFinala = i
                structuri = structuri + 1
                pozitieMijloc = int((pozitieInteresanta + pozitieFinala) / 2)
                centre = np.append(centre, pozitieMijloc)
                # np.insert(centre,pozitieMijloc,centre.size())
                pozitieInteresanta = 0
            elif (i == lungimeCadru - 1):
                structuri = structuri + 1
                pozitieMijloc = int((pozitieInteresanta + i) / 2)
                centre = np.append(centre, pozitieMijloc)
        else:
            if (EroareCentruTemporar > 0) and EroareCentruTemporar < EroareCentru:
                EroareCentruTemporar = EroareCentruTemporar + 1
            if (EroareCentruTemporar == EroareCentru):
                EroareCentruTemporar = 0
        if binarization[int(LatimeCadru * 2.0 / 3), i] > 1 and interesant == False:
            interesant = True
            pozitieInteresanta = i
            # *************************************************
    for j in range(1, lungimeCadru):
        if interesant2 == True:
            if binarization[int(LatimeCadru*4.0/5), j] == 0:
                interesant2 = False
                if (1 < EroareCentruTemporar2 < EroareCentru2):
                    print("Structuri fals. - Nu salvam valoarea")  # de fapt ar trebui sa recalculam centrul nou
                    continue
                EroareCentruTemporar2 = 1
                pozitieFinala2 = j
                structuri2 = structuri2 + 1
                pozitieMijloc2 = int((pozitieInteresanta2 + pozitieFinala2) / 2)
                centre2 = np.append(centre2, pozitieMijloc2)
                    # np.insert(centre,pozitieMijloc,centre.size())
                pozitieInteresanta2 = 0

            elif (j == lungimeCadru - 1):
                structuri2 = structuri2 + 1
                pozitieMijloc2 = int((pozitieInteresanta2 + j) / 2)
                centre2 = np.append(centre2, pozitieMijloc2)
        else:
            if (EroareCentruTemporar2 > 0) and EroareCentruTemporar2 < EroareCentru2:
                EroareCentruTemporar2 = EroareCentruTemporar2 + 1
            if (EroareCentruTemporar2 == EroareCentru2):
                EroareCentruTemporar2 = 0
        if binarization[int(LatimeCadru * 4.0 / 5), j] > 1 and interesant2 == False:
                interesant2 = True
                pozitieInteresanta2 = j
    # ****************************************


    print("Benzi gasite:" + str(structuri))
    print("\nCentre:\t" + str(centre))
    print("\nCentre2:\t" + str(centre2))
    MijlocCamera = int(lungimeCadru / 2.0)
    EroareCentrare = 20
    if centre.size == 2:
        DistantaBandaFrame = centre[1] - centre[0]
        print("Distanta dintre banda dreapta si cea stanga este: " + str(DistantaBandaFrame))
        # presupunem ca in primele frameuri masina este pe linie dreapta, primele 10 valori ale distantei dintre benzi sunt stocate intr-un vector
        # dupa ce au fost gasite 10 puncte de centru, incepem sa calculam media lor, fara a mai adauga sau calcula noi centre, presupunand ca
        # MedDistanta retina distanta medie ideala

        if(DistanteBenzi.__len__() < 10):
            DistanteBenzi=np.append(DistanteBenzi, DistantaBandaFrame)
            #print("ELEMENTE IN VECTOR" + str(DistanteBenzi.__len__()))
        else:
            MedDistanta = np.average(DistanteBenzi)
            print("Dupa 10 cadre, distanta medie dintre benzi este: " + str(MedDistanta) )



        # print(str(DistantaBandaFrame))
        x = MedDistanta / DistantaBandaFrame
        alphaDegrees = 0
        if (-1 <= x <= 1):
            alphaRadian = np.arccos(x)
            alphaDegrees = np.rad2deg(alphaRadian)
            mijlocCalculat = int((centre[0] + centre[1]) / 2)
        else:
            print("Nu putem calcula unghiul pt " + str(x))
            mijlocCalculat = int((centre[0] + centre[1]) / 2)
            DistantaFataDeAx = abs(mijlocCalculat - int(lungimeCadru / 2))
        if (MijlocCamera > (mijlocCalculat + EroareCentrare)):
            print("O luam spre stanga cu unghiul " + str(alphaDegrees))
        #f.write('2\t' + str(round(alphaDegrees, 2)) + '\n')
        elif (MijlocCamera < (mijlocCalculat + EroareCentrare)):
            alphaDegrees = -round(alphaDegrees, 2)
            #$f.write('1\t' + str(round(alphaDegrees, 2)) + '\n')
            print("O luam spre dreapta" + str(alphaDegrees))
        else:
            #f.write('0' + '\n')
            print("Suntem pe centru")
        for centru in centre:
            # print(int(centru))
            cv2.putText(img, str(centru), (int(centru - 20), int(LatimeCadru * 2.0 / 3)), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 0), 2)
        for centru2 in centre2:
            cv2.putText(img, str(centru2), (int(centru2 - 20), int(LatimeCadru * 4.0 / 5)), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 0), 2)
    if mijlocCalculat is  None:
        continue
    if centre.size > 1:
        cv2.line(img, (int(mijlocCalculat), 0), (int(mijlocCalculat), LatimeCadru), (255, 125, 125), 5)

    if centre.size == 1: #cazul in care nu ai 2 benzi
        #if centre[0] is not None and DistanteBenzi.__len__() > 10:
        if(centre <= 320):
            print("Avem o banda pe stanga")
            CentruImaginar = centre[0] + MedDistanta
            print("Nu exista banda pe partea dreapta, pozitia ei aproximata este " + str(CentruImaginar))
        else:
            print("Avem o banda pe dreapta")
            CentruImaginar = centre[0] - MedDistanta
            print("Nu exista banda pe partea stanga, pozitia ei aproximata este " + str(CentruImaginar))

        #if centre[0] is not None and MedDistanta > 0:
            #print("Nu exista banda pe partea stanga, pozitia ei aproximata este " + str(centre[1] - MedDistanta))

        for centru in centre:
            # print(int(centru))
            cv2.putText(img, str(centru), (int(centru - 20), int(LatimeCadru * 2.0 / 3)), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255), 2)
    if centre2.size == 1:
        for centru2 in centre2:
            cv2.putText(img, str(centru2), (int(centru2 - 20), int(LatimeCadru * 4.0 / 5)), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255), 2)

    if centre.size == 2 and centre2.size == 2:
        alphaAnglesLeft = math.atan(((LatimeCadru * 4.0 / 5) - (LatimeCadru * 2.0 /3 ))/(centre[0] - centre2[0]))
        alphaAnglesRight = math.atan(((LatimeCadru * 4.0 / 5) - (LatimeCadru * 2.0 / 3)) / (centre[1] - centre2[1]))
        alphaAnglesLeft = abs(np.rad2deg(alphaAnglesLeft))
        alphaAnglesRight = abs(np.rad2deg(alphaAnglesRight))

        panta1 = (((LatimeCadru * 4.0 / 5) - (LatimeCadru * 2.0 /3 ))/(centre[0] - centre2[0]))
        panta2 = (((LatimeCadru * 4.0 / 5) - (LatimeCadru * 2.0 / 3)) / (centre[1] - centre2[1]))

        unghiViraj = math.atan(panta1-panta2 / 1 + panta1*panta2)
        unghiViraj = abs(np.rad2deg(unghiViraj) - 45)
        print ("UNGHIUL DE VIRAJ ESTE: " + str(unghiViraj))
        if 0 < abs(alphaAnglesRight) - abs(alphaAnglesLeft ) < 10:
            print("ESTI PE CENTRU, STAI ASA")
        if alphaAnglesRight - alphaAnglesLeft > 10:
            print("->>>>>>")
        if alphaAnglesRight - alphaAnglesLeft < 0:
            print("<<<<<<<-")
        print("PE STANGA, UNGHIUL ESTE " + str(alphaAnglesLeft))
        print("PE DREAPTA UNGHIUL ESTE " + str(alphaAnglesRight))
    
        if centre2.size == 2 and centre.size == 2:
            cv2.rectangle(img, (int(centre2[0] - 20 ), int(lungimeCadru * 2.0 /3)), (int(centre2[1] + 20 ), int(lungimeCadru * 2.0 / 3)), (0, 0, 255), 5, lineType = 8)
            
    try:
        DiferentaFataDeMijloc=MijlocCamera - mijlocCalculat
        if  DiferentaFataDeMijloc > EroareCentrare:
            print("<<<<")
            pasAdaptare = pasAdaptare - 5
            if (pasAdaptare<(-23)):
                pasAdaptare=-22
            if ESTE_PE_MASINA:
                serialHandler.sendMove(0.0, pasAdaptare)
            print("PAS ADAPTARE: " + str(pasAdaptare))
        else:
            print("Nu merge boss")
            if -EroareCentrare < MijlocCamera - mijlocCalculat < EroareCentrare:
                if ESTE_PE_MASINA:
                    serialHandler.sendMove(0.0, 0.0)
                pasAdaptare = 0
            else:
                if ESTE_PE_MASINA:
                    serialHandler.sendMove(0.0, 5.0 + pasAdaptare)
                print("PAS ADAPTARE PE DREAPTA" + str(pasAdaptare))
                pasAdaptare = pasAdaptare + 5
            
    except Exception as e:
        print(e)
#        print("Nu merge boss2")
        pass
    # print("Dimensiune vector:"+str(array.size))
    # print("Vector analizat:"+str(array))
    # print("Valoare Medie Benzi:"+str(np.average(DistanteBenzi)))
    cv2.imshow("Image", img)
    #cv2.imshow("PERSPECTIVA NECALIBRATA", copie)
    #cv2.imshow("PERSPECTIVA CALIBRATA", undist_copy)
    #cv2.imshow("binarizare", binarization)
    # out.write(frame)
    cv2.waitKey(1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# rawCapture.truncate(0)
if ESTE_PE_MASINA:
    serialHandler.sendPidActivation(False)
    serialHandler.close()


# parcurgem centru si afisam cu cv2.putText(frame,"text",(coordx,coordy,cv2.FONT_fONT_HERSHEY_SIMPLEX,0.3,255)
cap.release()
cv2.destroyAllWindows()

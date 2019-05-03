import SerialHandler
import threading
import serial
import sys
import SaveEncoder
import time
import cv2
import numpy as np
import math
#from calibration_main import get_camera_calibration

global serialHandler

#TEST COMMIT3232

DEBUG_ALL_DATA = True
ESTE_PE_MASINA = False
DISTANTABANDACT = 350

# todo1 - calibrare unghi atac camera si salvarea valorii medie in DistantaBanda (o constanta pe care o sa o folosim pentru a determina inclinatia fata de AX
# todo2 - cum intra in curbe
# TODO3 - istorie cu ultimele directii ca sa eliminam false positive la mijlocCalculat
# TODO : cum testam timpul de reactie
# exemplu cand nu mai vede ambele benzii si curba depaseste mijlocul camerei, el marcheaza mijlocul imaginar in partea stanga

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


cap = cv2.VideoCapture('camera.avi')
#cap = cv2.VideoCapture(0)  # pentru camera
#out = cv2.VideoWriter('camera.avi', -1, 20, (640, 480))
counter = 0
#f = open('deplasare.txt', 'w')
# global serialHandler
CentruImaginar = 0
DistanteBenzi = np.zeros(0)
mijlocCalculat=0
pasAdaptare = 0
pozitieMijlocAnterior = -1
global serialHandler

if ESTE_PE_MASINA:
    serialHandler = SerialHandler.SerialHandler("/dev/ttyACM0")
    serialHandler.startReadThread()

class Directie:
    STANGA = -1
    CENTRU = 0
    DREAPTA = -1

class SectiuneBanda:
    def __init__(self):
        self.inaltimeSectiune=0
        self.interesant = False
        self.pozitieInteresanta = 0
        self.NumarStructuri = 0
        self.centre = np.zeros(0)
        self.EroareCentru = 50
        self.EroareCentruTemporar = 0
        self.pozitieMijloc=0
        self.pozitieFinala=0
        self.DistantaBandaFrame=0
        self.DistantaBandaFrameMediata=0
        self.DistantaBenziVector=np.zeros(0)
        self.MedDistanta=0
        self.mijlocCalculat=0

    def setInaltimeSectiune(self,valoare):
        self.inaltimeSectiune=int(valoare)

    def CalculDistantaBanda(self):
        global lungimeCadru
        if self.centre.size == 2 :
            self.DistantaBandaFrame = self.centre[1] - self.centre[0]
            print("Distanta dintre banda dreapta si cea stanga este: " + str(self.DistantaBandaFrame))
            self.MediereDistantaBanda()
            self.mijlocCalculat = int((self.centre[0] + self.centre[1]) / 2)
            self.DistantaFataDeAx = abs(self.mijlocCalculat - int(lungimeCadru / 2))

    def MediereDistantaBanda(self):
        if (self.DistantaBenziVector.__len__() < 10) :
            self.DistantaBenziVector = np.append(self.DistantaBenziVector, self.DistantaBandaFrame)
        else :
            self.MedDistanta = np.average(self.DistanteBenzi)
            print("Dupa 10 cadre, distanta medie dintre benzi este: " + str(self.MedDistanta))

    def ObtineStructuri(self,lungimeCadruAnalizat):
        global binarization,LatimeCadru
        for j in range(1, lungimeCadruAnalizat):
            if self.interesant == True:
                if binarization[self.inaltimeSectiune, j] == 0:
                    self.interesant = False
                    if (1 < self.EroareCentruTemporar < self.EroareCentru):
                        print("Structuri false. - Nu salvam valoarea")  # de fapt ar trebui sa recalculam centrul nou
                        continue
                    self.EroareCentruTemporar = 1
                    self.pozitieFinala = j
                    self.NumarStructuri= self.NumarStructuri + 1
                    self.pozitieMijloc = int((self.pozitieInteresanta + self.pozitieFinala) / 2)
                    self.centre = np.append(self.centre, self.pozitieMijloc)
                    self.pozitieInteresanta = 0

                elif (j == lungimeCadruAnalizat - 1):
                    self.NumarStructuri = self.NumarStructuri + 1
                    self.pozitieMijloc = int((self.pozitieInteresanta + j) / 2)
                    self.centre = np.append(self.centre, self.pozitieMijloc)
            else:
                if (self.EroareCentruTemporar > 0) and self.EroareCentruTemporar < self.EroareCentru:
                    self.EroareCentruTemporar = self.EroareCentruTemporar + 1
                if (self.EroareCentruTemporar == self.EroareCentru):
                    self.EroareCentruTemporar = 0
            if binarization[self.inaltimeSectiune, j] > 1 and self.interesant == False:
                    self.interesant = True
                    self.pozitieInteresanta = j

class TwoLanes:
    def __init__(self, SectiunePrincipala, SectiuneSecundara):
        self.SectiunePrincipala = SectiunePrincipala
        self.SectiuneSecundara = SectiuneSecundara
        self.MedDistanta=0

    def draw(self):
        global DiferentaFataDeMijloc
        if SectiuneSecundara.centre.size == 2 and SectiunePrincipala.centre.size == 2:
            cv2.rectangle(img, (int(SectiuneSecundara.centre[0] - 20), int(lungimeCadru * 2.0 / 3)),
                          (int(SectiuneSecundara.centre[1] + 20), int(lungimeCadru * 2.0 / 3)), (0, 0, 255), 5,
                          lineType=8)
            for centru in SectiunePrincipala.centre:
                # print(int(centru))
                cv2.putText(img, str(centru), (int(centru - 20), int(LatimeCadru * 2.0 / 3)), cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 0, 0), 2)
            for centru2 in SectiuneSecundara.centre:
                cv2.putText(img, str(centru2), (int(centru2 - 20), int(LatimeCadru * 4.0 / 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 0, 0), 2)

        if SectiunePrincipala.centre.size > 1:
            cv2.arrowedLine(img, (int(lungimeCadru / 2), 300), (int(self.mijlocCalculat), 300), (255, 255, 125), 2)
            cv2.putText(img, "Dist: " + str(DiferentaFataDeMijloc), (int(lungimeCadru / 2 + 50), 300),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 0, 60), 1)
            cv2.line(img, (int(self.mijlocCalculat), 0), (int(self.mijlocCalculat), LatimeCadru), (255, 125, 125), 5)

    def setDistantaDrum(self,valoare):
        self.MedDistanta=valoare
    def CalculMedDist(self, SectiunePrincipala, SectiuneSecundara):
        global EroareCentrare
        global MijlocCamera
        global DistanteBenzi
        if SectiunePrincipala.centre.size == 2:

            # presupunem ca in primele frameuri masina este pe linie dreapta, primele 10 valori ale distantei dintre benzi sunt stocate intr-un vector
            # dupa ce au fost gasite 10 puncte de centru, incepem sa calculam media lor, fara a mai adauga sau calcula noi centre, presupunand ca
            # MedDistanta retina distanta medie ideala

            if (DistanteBenzi.__len__() < 10):
                DistanteBenzi = np.append(DistanteBenzi, SectiunePrincipala.DistantaBandaFrame)
            else:
                self.setDistantaDrum(np.average(DistanteBenzi))
                print("BAAAAAAAAAADupa 10 cadre, distanta medie dintre benzi este: " + str(self.MedDistanta))

            RaportIntreBenzi = SectiunePrincipala.MedDistanta / SectiunePrincipala.DistantaBandaFrame
            alphaDegrees = 0

            self.mijlocCalculat = SectiunePrincipala.mijlocCalculat
            DistantaFataDeAx = SectiunePrincipala.DistantaFataDeAx
            # DistantaFataDeAx = abs(mijlocCalculat - int(lungimeCadru / 2))

            if (-1 <= RaportIntreBenzi <= 1):
                alphaRadian = np.arccos(RaportIntreBenzi)
                alphaDegrees = np.rad2deg(alphaRadian)
            else:
                print("Nu putem calcula unghiul pt " + str(RaportIntreBenzi))

            if (MijlocCamera > (self.mijlocCalculat + EroareCentrare)):
                print("O luam spre stanga cu unghiul " + str(alphaDegrees))
            # f.write('2\t' + str(round(alphaDegrees, 2)) + '\n')
            elif (MijlocCamera < (self.mijlocCalculat + EroareCentrare)):
                alphaDegrees = -round(alphaDegrees, 2)
                # $f.write('1\t' + str(round(alphaDegrees, 2)) + '\n')
                print("O luam spre dreapta" + str(alphaDegrees))
            else:
                # f.write('0' + '\n')
                print("Suntem pe centru")

        return self.MedDistanta


class OneLane:
    def __init__(self, SectiunePrincipala, SectiuneSecundara):
        self.CentruImaginar = 0
        self.Referinta=0
        global MedDistanta
        if SectiunePrincipala.centre.size == 1:  # cazul in care nu ai 2 benzi
            # if centre[0] is not None and DistanteBenzi.__len__() > 10:
            if SectiuneSecundara.centre.size == 1:
                if (SectiuneSecundara.centre <= lungimeCadru / 2):
                    self.Referinta=SectiuneSecundara.centre[0]
                    self.CentruImaginar =  self.Referinta + MedDistanta / 2
                    if ESTE_PE_MASINA:
                        print("Avem o banda pe stanga")
                        print("Nu exista banda pe partea dreapta, pozitia ei aproximata este " + str(self.CentruImaginar))
                    else:
                        cv2.putText(img, "Pozitie Relativa Mijloc Imaginar: " + str(self.CentruImaginar), (10, 420),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

                else:
                    self.Referinta = SectiuneSecundara.centre[0]
                    self.CentruImaginar = self.Referinta - MedDistanta / 2
                    if ESTE_PE_MASINA:
                        print("Avem o banda pe dreapta")
                        print("Nu exista banda pe partea stanga, pozitia ei aproximata este " + str(self.CentruImaginar))
                    else:
                        cv2.putText(img, "Pozitie Relativa Mijloc Imaginar: " + str(self.CentruImaginar), (10, 420),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            else:
                if (SectiunePrincipala.centre <= lungimeCadru / 2):
                    self.Referinta = SectiunePrincipala.centre[0]
                    self.CentruImaginar = self.Referinta + MedDistanta / 2
                    if ESTE_PE_MASINA:
                        print("Avem o banda pe stanga")
                        print("Nu exista banda pe partea dreapta, pozitia ei aproximata este " + str(self.CentruImaginar))
                    else:
                        cv2.putText(img, "Pozitie Relativa Mijloc Imaginar: " + str(self.CentruImaginar), (10, 420),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                else:
                    self.Referinta = SectiunePrincipala.centre[0]
                    self.CentruImaginar = self.Referinta - MedDistanta / 2
                    if ESTE_PE_MASINA:
                        print("Avem o banda pe dreapta")
                        print("Nu exista banda pe partea stanga, pozitia ei aproximata este " + str(self.CentruImaginar))
                    else:
                        cv2.putText(img, "Pozitie Relativa Mijloc Imaginar: " + str(self.CentruImaginar), (10, 420),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # if centre[0] is not None and MedDistanta > 0:
            # print("Nu exista banda pe partea stanga, pozitia ei aproximata este " + str(centre[1] - MedDistanta))

            for centru in SectiunePrincipala.centre:
                # print(int(centru))
                cv2.putText(img, str(centru), (int(centru - 20), int(LatimeCadru * 2.0 / 3)), cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 0, 255), 2)


    def draw(self):
        global MijlocCamera
        if SectiunePrincipala.centre.size == 1:  # cazul in care nu ai 2 benzi
            cv2.line(img, (int(self.CentruImaginar), 0), (int(self.CentruImaginar), LatimeCadru), (125, 125, 0), 5)
            cv2.arrowedLine(img, (int(lungimeCadru / 2), 300), (int(self.CentruImaginar), 300), (255, 255, 125), 2)
            cv2.putText(img, "Avem Mijloc Imaginar", (10, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            cv2.putText(img, "Dist: " + str(abs(int(MijlocCamera-self.CentruImaginar))), (int(lungimeCadru / 2 + 50), 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 0, 60), 1)

        if SectiuneSecundara.centre.size == 1:
            for centru2 in SectiuneSecundara.centre:
                cv2.putText(img, str(centru2), (int(centru2 - 20), int(LatimeCadru * 4.0 / 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 0, 255), 2)


def PutLines():
    LatimeCadru, lungimeCadru, _ = frame.shape
    cv2.line(img, (0, int(LatimeCadru * 2.0 / 3)), (lungimeCadru, SectiunePrincipala.inaltimeSectiune), (255, 255, 0), 2)
    cv2.line(img, (0, int(LatimeCadru * 4.0 / 5)), (lungimeCadru, SectiuneSecundara.inaltimeSectiune), (0, 255, 0), 2)
    cv2.line(img, (int(lungimeCadru / 2), 0), (int(lungimeCadru / 2), LatimeCadru), (255, 255, 255), 2)


while (cap.isOpened()):
    ret, frame = cap.read()
    if ret == False:
        break
    counter = counter + 1
    LocatieDeInteres = 0  # 1450
    if counter < LocatieDeInteres:
        continue
    # for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    img = frame
    # if DEBUG_RECORD:
    #out.write(frame)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #gray = abs(255 - gray) # in caz ca vrem inversare
    ret, binarization = cv2.threshold(gray, 190, 255, cv2.THRESH_BINARY)
    LatimeCadru, lungimeCadru, _ = frame.shape

    #  print("Dimensiune imagine:" + str(binarization[160,:].size))
    #array = np.argwhere(binarization[int(LatimeCadru * 2.0 / 3), :] > 1)
    SectiunePrincipala = SectiuneBanda()
    SectiuneSecundara = SectiuneBanda()



    SectiunePrincipala.setInaltimeSectiune(LatimeCadru * 2.0 / 3)#66.6 % din camera
    SectiuneSecundara.setInaltimeSectiune(LatimeCadru * 4.0 / 5) #80 % din camera - jos

    SectiunePrincipala.ObtineStructuri(lungimeCadru)
    SectiuneSecundara.ObtineStructuri(lungimeCadru)

    PutLines()

    if SectiunePrincipala.centre.size == 2:
        ObiectDrum = TwoLanes(SectiunePrincipala, SectiuneSecundara)
    else:
        ObiectBanda = OneLane(SectiunePrincipala, SectiuneSecundara)

    if DEBUG_ALL_DATA:
        print("Benzi gasite:" + str(SectiunePrincipala.NumarStructuri))
        print("\nCentre:\t" + str(SectiunePrincipala.centre))
        print("\nCentre2:\t" + str(SectiuneSecundara.centre))
    else:
        cv2.putText(img, "Benzi identificate: "+ str(SectiunePrincipala.NumarStructuri), (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    MijlocCamera = int(lungimeCadru / 2.0)
    EroareCentrare = 50
    SectiunePrincipala.CalculDistantaBanda()

        #END OF TODO DE refactoring

        # Afisare centre?

        # END Afisare Centre
    if mijlocCalculat is  None:
        continue

    if ObiectDrum is not None:
        MedDistanta = ObiectDrum.CalculMedDist(SectiunePrincipala, SectiuneSecundara)
        MijlocGeneric=ObiectDrum.mijlocCalculat
    else:
        MijlocGeneric=ObiectBanda.CentruImaginar

    #MedDistanta=SectiunePrincipala.MedDistanta



    try:
        DiferentaFataDeMijloc = abs(MijlocCamera - MijlocGeneric)
        if  DiferentaFataDeMijloc > EroareCentrare:
            DirectieIdentificata = Directie.STANGA # TODO poate facem asta cu verificare
            pasAdaptare = pasAdaptare - 5
            if (pasAdaptare<(-23)):
                pasAdaptare=-22
            if ESTE_PE_MASINA:
                serialHandler.sendMove(0.0, pasAdaptare)
                print("<<<<")
                print("Unghi Adaptat pentru stanga: " + str(pasAdaptare))
        else:
            if -EroareCentrare < DiferentaFataDeMijloc < EroareCentrare:
                DirectieIdentificata = Directie.CENTRU #TODO
                if ESTE_PE_MASINA:
                    serialHandler.sendMove(0.0, 0.0)
                    print("suntem pe centru")
                pasAdaptare = 0
            else:
                DirectieIdentificata = Directie.DREAPTA #TODO
                if ESTE_PE_MASINA:
                    serialHandler.sendMove(0.0, 5.0 + pasAdaptare)
                    print(">>>>>>")
                    print("Unghi Adaptat pentru dreapta:\t" + str(pasAdaptare))
                pasAdaptare = pasAdaptare + 5
                if (pasAdaptare > (23)):
                    pasAdaptare = 22
    except Exception as e:
        print(e)
        pass

    if SectiunePrincipala.centre.size == 2 and not ESTE_PE_MASINA:
           ObiectDrum.draw()
    else:
           ObiectBanda.draw()


    ### END OF AFISARE

    # print("Valoare Medie Benzi:"+str(np.average(DistanteBenzi)))
    if(not ESTE_PE_MASINA):
        cv2.imshow("Image", img)
        cv2.imshow("binarizare", binarization)
        cv2.waitKey(1)
    #cv2.imshow("PERSPECTIVA NECALIBRATA", copie)
    #cv2.imshow("PERSPECTIVA CALIBRATA", undist_copy)q


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if not ESTE_PE_MASINA:
        time.sleep(1)

# rawCapture.truncate(0)
if ESTE_PE_MASINA:
    serialHandler.sendPidActivation(False)
    serialHandler.close()

# parcurgem centru si afisam cu cv2.putText(frame,"text",(coordx,coordy,cv2.FONT_fONT_HERSHEY_SIMPLEX,0.3,255)
cap.release()
cv2.destroyAllWindows()

import SerialHandler
import threading
import serial
import sys
import SaveEncoder
import time
import cv2
import numpy as np
from Banda import Banda
from Observer import DeplasareMasina
from StopAndPark import stopOrPark

global serialHandler
DEBUG_ALL_DATA = False
ESTE_PE_MASINA = False
VIDEO_RECORD = False
AMPARCAT=False

## VARIABILE
cap = cv2.VideoCapture('cameraE.avi')
CentruImaginar = 0
EroareCentrare = 30
DistanteBenzi = np.zeros(0)
mijlocCalculat=0
pasAdaptare = 0
pozitieMijlocAnterior = -1
counter = 0
masina = DeplasareMasina()
## END OF VARIABLE

global serialHandler

if VIDEO_RECORD:
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    out = cv2.VideoWriter('cameraJ.avi', fourcc, 20,(640, 480))

if ESTE_PE_MASINA:
    serialHandler = SerialHandler.SerialHandler("/dev/ttyACM0")
    serialHandler.startReadThread()

class Indicator:
    STOP = 1
    PARCARE = 2
    Eroare = 3

class Drum:
    def __init__(self):
        self.BandaStanga = Banda()
        self.BandaDreapta = Banda()
        self.Centru = 0
        self.MedDistanta = 0

    def __init__(self, Benzi):
        global lungimeCadru
        if len(Benzi)==0:
            return
        if len(Benzi)==2:
            self.BandaStanga = Benzi[0]
            self.BandaDreapta = Benzi[1]
            self.Centru = int((self.BandaStanga.mijlocCalculat + self.BandaDreapta.mijlocCalculat) / 2)
        if len(Benzi)==1:
            if Benzi[0].pozitieMijloc<=lungimeCadru/2:
                self.BandaStanga = Benzi[0]
                self.Referinta = Benzi[0].mijlocCalculat + (MedDistanta / 2)
                self.Centru = int((self.BandaStanga.mijlocCalculat + self.Referinta) / 2)
            else:
                self.BandaDreapta = Benzi[0]
                self.Referinta = Benzi[0].mijlocCalculat - (MedDistanta / 2)
                self.Centru = int((self.Referinta + self.BandaDreapta.mijlocCalculat) / 2)

class TwoLanes:
    def __init__(self, Sectiune):
        self.Sectiune = Sectiune
        self.MedDistanta=0
    def draw(self):
        global DiferentaFataDeMijloc
             #  DE REVIZUIT 1)

            #cv2.rectangle(img, (int(SectiuneSecundara.centre[0] - 20), int(lungimeCadru * 2.0 / 3)),

             #             (int(SectiuneSecundara.centre[1] + 20), int(lungimeCadru * 2.0 / 3)), (0, 0, 255), 5,

             #             lineType=8)
        for centru in self.Sectiune.centre:
            cv2.putText(img, str(centru), (int(centru - 20), int(LatimeCadru * 2.0 / 3)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        if self.Sectiune.centre.size > 1:
            cv2.arrowedLine(img, (int(lungimeCadru / 2), 300), (int(self.mijlocCalculat), 300), (255, 255, 125), 2)
            cv2.putText(img, "Dist: " + str(DiferentaFataDeMijloc), (int(lungimeCadru / 2 + 50), 300),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 0, 60), 1)
            cv2.line(img, (int(self.mijlocCalculat), 0), (int(self.mijlocCalculat), LatimeCadru), (255, 125, 125), 5)

    def setDistantaDrum(self,valoare):
        self.MedDistanta=valoare

    def CalculMedDist(self):
        global EroareCentrare
        global MijlocCamera
        global DistanteBenzi
        if self.Sectiune.centre.size == 2:
            if (DistanteBenzi.__len__() < 3):
                DistanteBenzi = np.append(DistanteBenzi, self.Sectiune.DistantaBandaFrame)
            else:
                self.setDistantaDrum(np.average(DistanteBenzi))
                print("BAAAAAAAAAADupa 3 cadre, distanta medie dintre benzi este: " + str(self.MedDistanta))
            self.mijlocCalculat = self.Sectiune.mijlocCalculat
        return self.MedDistanta

class OneLane:
    def __init__(self, Sectiune):
        self.Sectiune = Sectiune
        self.CentruImaginar = 0
        self.Referinta = 0
        global MedDistanta
        if 'MedDistanta' not in globals():
            MedDistanta=350

        if self.Sectiune.centre.size == 1:  # cazul in care nu ai 2 benzi
            if self.Sectiune.centre < lungimeCadru / 2:
                self.Referinta = self.Sectiune.centre[0]
                self.CentruImaginar = self.Referinta + (MedDistanta / 2)

                print("Avem o banda pe stanga")
                print("Nu exista banda pe partea dreapta, pozitia ei aproximata este " + str(self.CentruImaginar))
                cv2.putText(img, "Pozitie Relativa Mijloc Imaginar: " + str(self.CentruImaginar), (10, 420),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            else:
                self.Referinta = self.Sectiune.centre[0]
                self.CentruImaginar = self.Referinta - (MedDistanta / 2)
                print("Avem o banda pe dreapta")
                print("Nu exista banda pe partea stanga, pozitia ei aproximata este " + str(self.CentruImaginar))
                cv2.putText(img, "Pozitie Relativa Mijloc Imaginar: " + str(self.CentruImaginar), (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            for centru in self.Sectiune.centre:
                cv2.putText(img, str(centru), (int(centru - 20), int(LatimeCadru * 2.0 / 3)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def draw(self):
        global MijlocCamera
        if self.Sectiune.centre.size == 1:  # cazul in care nu ai 2 benzi
            cv2.line(img, (int(self.CentruImaginar), 0), (int(self.CentruImaginar), LatimeCadru), (125, 125, 0), 5)
            cv2.arrowedLine(img, (int(lungimeCadru / 2), 300), (int(self.CentruImaginar), 300), (255, 255, 125), 2)
            cv2.putText(img, "Avem Mijloc Imaginar", (10, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            cv2.putText(img, "Dist: " + str(abs(int(MijlocCamera - self.CentruImaginar))), (int(lungimeCadru / 2 + 50), 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 0, 60), 1)

def PutLines():
    LatimeCadru, lungimeCadru, _ = frame.shape
    cv2.line(img, (0, int(LatimeCadru * 2.0 / 3)), (lungimeCadru, Sectiune.inaltimeSectiune), (255, 255, 0), 2)
    cv2.line(img, (int(lungimeCadru / 2), 0), (int(lungimeCadru / 2), LatimeCadru), (255, 255, 255), 2)


counterStop=0

while (cap.isOpened()):
    ret, frame = cap.read()
    if ret is False:
        break
    img = frame

    EsteStop,EsteParcare = stopOrPark(frame, AMPARCAT)

    counter = counter + 1
    if counter < 5 :
        continue
    if VIDEO_RECORD:
        out.write(frame)
    if not ESTE_PE_MASINA:
        cv2.putText(img, "Cadrul: " + str(counter), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                    (250, 250, 250), 2)

    if EsteStop :
        print("avem stop")
        print(str(masina.current_state))
        if (masina.current_state == masina.initializare) :  # verific ca sunt in starea initiala
            counterStop = counterStop + 1
            masina.stoptodo()
            CounterFolositPentruAMasuraStarea = 1
        else :
            print("dar nu sunt in starea de mers")
    if EsteParcare:
        print("avem parcare")
        if (masina.current_state == masina.initializare) :  # verific ca sunt in starea initial
                AMPARCAT = True
                masina.Parcheaza()
                CounterFolositPentruAMasuraStarea = 1
        else :
            print("dar nu sunt in starea de mers")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, binarization = cv2.threshold(gray, 190, 255, cv2.THRESH_BINARY)
    LatimeCadru, lungimeCadru, _ = frame.shape
    MijlocCamera = int(lungimeCadru / 2.0)
    Sectiune = Banda()
    Sectiune.setInaltimeSectiune(LatimeCadru * 2.0 / 3)#66.6 % din camera
    #BenziPrincipale = ObtineStructuri(int(LatimeCadru * 2.0 / 3), binarization)
    #DrumPrincipal=Drum(BenziPrincipale)
    Sectiune.ObtineStructuri(lungimeCadru, binarization)
    Sectiune.SetNumeBanda("Sect. Pp")
    Sectiune.CalculDistantaBanda(lungimeCadru)
    fps = cap.get(cv2.CAP_PROP_FPS)


    if not ESTE_PE_MASINA:
        cv2.putText(img, "FPS: " + str(fps), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (50, 50, 50), 2)
    else:
        print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))
    if not ESTE_PE_MASINA:
        PutLines()
    try:
        del ObiectDrum
    except:
        pass
    try:
        del ObiectBanda
    except:
        pass
    if Sectiune.centre.size == 2:
        ObiectDrum = TwoLanes(Sectiune)
    else:
        ObiectBanda = OneLane(Sectiune)

    if DEBUG_ALL_DATA and ESTE_PE_MASINA:
        print("Benzi gasite:" + str(Sectiune.NumarStructuri))
        print("\nCentre:\t" + str(Sectiune.centre))
    else:
        cv2.putText(img, "Benzi identificate: "+ str(Sectiune.NumarStructuri), (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    if mijlocCalculat is  None:
        continue

    if 'ObiectDrum' in locals() :
        MedDistanta = ObiectDrum.CalculMedDist()
        MijlocGeneric = ObiectDrum.mijlocCalculat
    else:
        MijlocGeneric = ObiectBanda.CentruImaginar



    try:

        DiferentaFataDeMijloc = MijlocCamera - MijlocGeneric
        if  DiferentaFataDeMijloc > EroareCentrare:
            pasAdaptare = pasAdaptare - 2
            if (pasAdaptare<(-22)):
                pasAdaptare=-20
            if ESTE_PE_MASINA:
                serialHandler.sendMove(0.20, pasAdaptare)
                print("<<<<")
                print("Unghi Adaptat pentru stanga: " + str(pasAdaptare))
            else:
                cv2.putText(img, "O luam la stanga", (10, 380),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        else:
            if -EroareCentrare < DiferentaFataDeMijloc < EroareCentrare:
                if ESTE_PE_MASINA:
                    serialHandler.sendMove(0.20, 0.0)
                    print("suntem pe centru")
                pasAdaptare = 0
            else:
                if ESTE_PE_MASINA:
                    serialHandler.sendMove(0.20, 2.0 + pasAdaptare)
                    print(">>>>>>")
                    print("Unghi Adaptat pentru dreapta:\t" + str(pasAdaptare))
                else:
                    cv2.putText(img, "O luam la dreapta", (10, 380),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                pasAdaptare = pasAdaptare + 5
                if (pasAdaptare > (22)):
                    pasAdaptare = 20

    except Exception as e:
        print(e)
        pass


    if Sectiune.centre.size == 2:
        ObiectDrum.draw()
    else:
        ObiectBanda.draw()

    if (not ESTE_PE_MASINA) :
        cv2.putText(img, "Stare: " + str(masina.current_state.value), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                    (250, 250, 250), 2)
    else :
        print(masina.current_state.value)
    if (not ESTE_PE_MASINA) :
        cv2.imshow("Image", img)
        cv2.imshow("binarizare", binarization)
        cv2.waitKey(0)
        time.sleep(0.5)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    #if stopOrPark(img, False) == 1:
    #    print("STOP")
    #    serialHandler.sendBrake(0)
if ESTE_PE_MASINA:
    serialHandler.sendPidActivation(False)
    serialHandler.close()

cap.release()
cv2.destroyAllWindows()
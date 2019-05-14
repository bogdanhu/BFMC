import SerialHandler
import threading
import serial
import sys
import SaveEncoder
import time
import cv2
import numpy as np
import math
from Banda import Banda
#from calibration_main import get_camera_calibration
def ObtineStructuri(lungimeCadruAnalizat,inaltimeSectiune,binarization) :
    EroareCentruTemporar = 0
    interesant=False
    EroareCentru = 10
    pozitieFinala=0
    NumarStructuri=0
    Benzi = np.zeros(0)
    BandaNoua=None

    for j in range(1, lungimeCadruAnalizat) :
        if interesant == True :
            if binarization[inaltimeSectiune, j] == 0 :
                interesant = False
                if (1 < EroareCentruTemporar < EroareCentru) :
                    if (DEBUG_ALL_DATA and ESTE_PE_MASINA):
                        print("Structuri false. - Nu salvam valoarea")  # de fapt ar trebui sa recalculam centrul nou
                    continue
                if (int(pozitieFinala - pozitieInitiala) > 150) :
                    print("eliminam o structura prea mare")
                    continue
                EroareCentruTemporar = 1
                pozitieFinala = j
                NumarStructuri = NumarStructuri + 1

                pozitieMijloc = int((pozitieInitiala + pozitieFinala) / 2)
                BandaNoua=Banda()
                BandaNoua.SetMijlocCalculat(pozitieMijloc)
                Benzi = np.append(Benzi, BandaNoua)
                pozitieInitiala = 0

            elif (j == lungimeCadruAnalizat - 1) :
                NumarStructuri = NumarStructuri + 1
                pozitieMijloc = int((pozitieInitiala + j) / 2)
                BandaNoua = Banda()
                BandaNoua.SetMijlocCalculat(pozitieMijloc)
                Benzi = np.append(Benzi, BandaNoua)
                #Aici adaugam o banda !
        else :
            if (EroareCentruTemporar > 0) and EroareCentruTemporar < EroareCentru :
                EroareCentruTemporar = EroareCentruTemporar + 1
            if (EroareCentruTemporar == EroareCentru) :
                EroareCentruTemporar = 0
        if binarization[inaltimeSectiune, j] > 1 and interesant == False :
            interesant = True
            pozitieInitiala = j
    return Benzi
import imutils
from Observer import DeplasareMasina
from StopAndPark import stopOrPark

global serialHandler
DEBUG_ALL_DATA = True
ESTE_PE_MASINA = False
DISTANTABANDACT = 350
AMPARCAT=False

#TEST COMMIT3232



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


cap = cv2.VideoCapture('demo.avi')
#cap = cv2.VideoCapture(0)  # pentru camera
#fourcc = cv2.VideoWriter_fourcc(*'DIVX')
#out = cv2.VideoWriter('camera.avi', fourcc, 20,(640, 480))
counter = 0
#f = open('deplasare.txt', 'w')
# global serialHandler
CentruImaginar = 0
EroareCentrare = 50
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

class Indicator:
    STOP = 1
    PARCARE = 2
    Eroare = 3

class Drum:
    def __init__(self):
        self.BandaStanga= Banda()
        self.BandaDreapta=Banda()
        self.Centru=0
        self.MedDistanta=0
    def __init__(self,Benzi):
        global lungimeCadru
        if(len(Benzi)==0):
            return
        if(len(Benzi)==2):
            self.BandaStanga = Benzi[0]
            self.BandaDreapta = Benzi[1]
            self.Centru = int((self.BandaStanga.mijlocCalculat + self.BandaDreapta.mijlocCalculat) / 2)
        if(len(Benzi)==1):
            if(Benzi[0].pozitieMijloc<=lungimeCadru/2):
                self.BandaStanga=Benzi[0]
              #  self.BandaDreapta=Benzi[1]
            #    self.Centru=int((self.BandaStanga+self.BandaDreapta.mijlocCalculat)/2)
            else:
                self.BandaDreapta=Benzi[0]

        #calculam
        #for Banda in Benzi:

        #self.BandaStanga = BandaStanga
        #self.BandaDreapta = BandaDreapta
        #self.Centru = (BandaStanga.pozitieMijloc+BandaDreapta.pozitieMijloc)/2
        #self.MedDistanta = abs(BandaStanga.pozitieMijloc-BandaDreapta.pozitieMijloc)
    #def __init__(self, BandaNecunoscuta) :
     #   if (BandaNecunoscuta.pozitieMijloc<320):
      #      self.BandaStanga=BandaNecunoscuta
       #     #self.BandaDrepta=calculeazaBanda(pozitieMijloc,mediaUltimelorDrumuriBanda)
        #    pass
        #self.Centru = (BandaStanga.pozitieMijloc + BandaDreapta.pozitieMijloc) / 2
        #self.MedDistanta = mediaUltimelorDrumuriBanda

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
        for centru in SectiunePrincipala.centre :
            # print(int(centru))
            cv2.putText(img, str(centru), (int(centru - 20), int(LatimeCadru * 2.0 / 3)), cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 0), 2)
        for centru2 in SectiuneSecundara.centre :
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

            if (DistanteBenzi.__len__() < 3):
                DistanteBenzi = np.append(DistanteBenzi, SectiunePrincipala.DistantaBandaFrame)
            else:
                self.setDistantaDrum(np.average(DistanteBenzi))
                print("BAAAAAAAAAADupa 3 cadre, distanta medie dintre benzi este: " + str(self.MedDistanta))

            RaportIntreBenzi = SectiunePrincipala.MedDistanta / SectiunePrincipala.DistantaBandaFrame
            alphaDegrees = 0

            self.mijlocCalculat = SectiunePrincipala.mijlocCalculat
            DistantaFataDeAx = SectiunePrincipala.DistantaFataDeAx
            # DistantaFataDeAx = abs(mijlocCalculat - int(lungimeCadru / 2))

        return self.MedDistanta


class OneLane:
    def __init__(self, SectiunePrincipala, SectiuneSecundara):
        self.CentruImaginar = 0
        self.Referinta=0
        global MedDistanta
        if 'MedDistanta' not in globals():
            MedDistanta=350
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

counterTemp=0

SectiunePrincipalaIstoric = Banda()
SectiuneSecundaraIstoric = Banda()
masina = DeplasareMasina()

while (cap.isOpened()):
    if (masina.current_state == masina.initializare) :
        masina.PleacaDeLaStart()
    ret, frame = cap.read()
    if ret == False:
        break

    counterTemp=counterTemp+1
    if counterTemp<2:
        continue
    else:
        counterTemp=0
    counter = counter + 1

    LocatieDeInteres = 0




    if (not ESTE_PE_MASINA):
        LocatieDeInteres = 0  # 1450
    if counter < LocatieDeInteres:
        continue
    # for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    img = frame

    AnalizaCadru=stopOrPark(frame)
    if AnalizaCadru is not None:
        if AnalizaCadru==Indicator.STOP:
            print("avem stop")
        elif AnalizaCadru==Indicator.PARCARE:
            print("avem parcare")
    cv2.imshow("Frame", frame)  # afiseaza ce se inregistreaza live.



    # if DEBUG_RECORD:
    #out.write(frame)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #gray = abs(255 - gray) # in caz ca vrem inversare
    ret, binarization = cv2.threshold(gray, 190, 255, cv2.THRESH_BINARY)
    LatimeCadru, lungimeCadru, _ = frame.shape

    #  print("Dimensiune imagine:" + str(binarization[160,:].size))
    #array = np.argwhere(binarization[int(LatimeCadru * 2.0 / 3), :] > 1)
    SectiunePrincipala = Banda()
    SectiuneSecundara = Banda()

    SectiunePrincipala.setInaltimeSectiune(LatimeCadru * 2.0 / 3)#66.6 % din camera
    SectiuneSecundara.setInaltimeSectiune(LatimeCadru * 4.0 / 5) #80 % din camera - jos


    BenziPrincipale=ObtineStructuri(lungimeCadru,int(LatimeCadru * 2.0 / 3),binarization)
    BenziSecundare= ObtineStructuri(lungimeCadru, int(LatimeCadru * 4.0 / 5), binarization)

    # aici calculez MedDistanta
    Benzi=np.append(BenziPrincipale,BenziSecundare)
    DrumPrincipal=Drum(BenziPrincipale)
    DrumSecundar=Drum(BenziSecundare)

    if (len(BenziPrincipale)==2 and len(BenziSecundare)==2): #trigger de drum
        if (masina.current_state == masina.MergiInainte) :  #verific ca sunt in starea initiala
            masina.stop()

        if (DEBUG_ALL_DATA and not ESTE_PE_MASINA):
            print("Diferenta intre Drumuri:"+str(DrumPrincipal.Centru-DrumSecundar.Centru))
        if(abs(DrumPrincipal.Centru-DrumSecundar.Centru)>EroareCentrare):
            print("Urmeaza o curba")
            cv2.waitKey(0)
    SectiunePrincipala.ObtineStructuri(lungimeCadru,binarization,LatimeCadru)
    SectiuneSecundara.ObtineStructuri(lungimeCadru,binarization,LatimeCadru)
    SectiunePrincipala.SetNumeBanda("Sect. Pp")
    SectiuneSecundara.SetNumeBanda("Sect. Sec")

    SectiunePrincipala.CalculDistantaBanda(lungimeCadru)
    SectiuneSecundara.CalculDistantaBanda(lungimeCadru)

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not(ESTE_PE_MASINA):
        cv2.putText(img, "FPS: " + str(fps), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (50, 50, 50), 2)
    else:
        print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))

    PutLines()
    ## Aici nu e ok, TODO
    try:
        del ObiectDrum
    except:
        pass
    try:
        del ObiectBanda
    except:
        pass

    if SectiunePrincipala.centre.size == 2:
        ObiectDrum = TwoLanes(SectiunePrincipala, SectiuneSecundara)
    else:
        ObiectBanda = OneLane(SectiunePrincipala, SectiuneSecundara)

    if DEBUG_ALL_DATA and ESTE_PE_MASINA:
        print("Benzi gasite:" + str(SectiunePrincipala.NumarStructuri))
        print("\nCentre:\t" + str(SectiunePrincipala.centre))
        print("\nCentre2:\t" + str(SectiuneSecundara.centre))
    else:
        cv2.putText(img, "Benzi identificate: "+ str(SectiunePrincipala.NumarStructuri), (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    MijlocCamera = int(lungimeCadru / 2.0)



        #END OF TODO DE refactoring

        # Afisare centre?

        # END Afisare Centre
    if mijlocCalculat is  None:
        continue
    if 'ObiectDrum' in locals() :
        MedDistanta = ObiectDrum.CalculMedDist(SectiunePrincipala, SectiuneSecundara)
        MijlocGeneric=ObiectDrum.mijlocCalculat
    else:
        MijlocGeneric=ObiectBanda.CentruImaginar

    #MedDistanta=SectiunePrincipala.MedDistanta



    try:
        DiferentaFataDeMijloc = MijlocCamera - MijlocGeneric
        if  DiferentaFataDeMijloc > EroareCentrare:
            DirectieIdentificata = Directie.STANGA # TODO poate facem asta cu verificare
            pasAdaptare = pasAdaptare - 5
            if (pasAdaptare<(-23)):
                pasAdaptare=-22
            if ESTE_PE_MASINA:
                serialHandler.sendMove(20.0, pasAdaptare)
                print("<<<<")
                print("Unghi Adaptat pentru stanga: " + str(pasAdaptare))
            else:
                cv2.putText(img, "O luam la stanga", (10, 380),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        else:
            if -EroareCentrare < DiferentaFataDeMijloc < EroareCentrare:
                DirectieIdentificata = Directie.CENTRU #TODO
                if ESTE_PE_MASINA:
                    serialHandler.sendMove(20.0, 0.0)
                    print("suntem pe centru")
                pasAdaptare = 0
            else:
                DirectieIdentificata = Directie.DREAPTA #TODO
                if ESTE_PE_MASINA:
                    serialHandler.sendMove(20.0, 5.0 + pasAdaptare)
                    print(">>>>>>")
                    print("Unghi Adaptat pentru dreapta:\t" + str(pasAdaptare))
                else:
                    cv2.putText(img, "O luam la dreapta", (10, 380),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                pasAdaptare = pasAdaptare + 5
                if (pasAdaptare > (23)):
                    pasAdaptare = 22
    except Exception as e:
        print(e)
        pass

    if SectiunePrincipala.centre.size == 2:
           ObiectDrum.draw()
    else:
           ObiectBanda.draw()


    ### END OF AFISARE

    if (not ESTE_PE_MASINA) :
        cv2.putText(img, "Stare: " + str(masina.current_state.value), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                    (250, 250, 250), 2)
    else :
        print(masina.current_state.value)

    if (not ESTE_PE_MASINA) :
        cv2.imshow("Image", img)
        cv2.imshow("binarizare", binarization)
        cv2.waitKey(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break




# rawCapture.truncate(0)
if ESTE_PE_MASINA:
    serialHandler.sendPidActivation(False)
    serialHandler.close()

# parcurgem centru si afisam cu cv2.putText(frame,"text",(coordx,coordy,cv2.FONT_fONT_HERSHEY_SIMPLEX,0.3,255)
#out.release()
cap.release()
cv2.destroyAllWindows()

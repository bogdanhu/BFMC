import numpy as np
class Banda:
    def __init__(self):
        self.inaltimeSectiune=0
        self.interesant = False
        self.pozitieInitiala = 0
        self.NumarStructuri = 0 # Banda e o structura de sters
        self.centre = np.zeros(0) # centru benzii e mijloc - de sters
        self.EroareCentru = 50
        self.pozitieMijloc = 0
        self.pozitieFinala = 0
        self.DistantaBandaFrame = 0
        self.DistantaBenziVector = np.zeros(0)
        self.MedDistanta = 0
        self.mijlocCalculat = 0
        self.nume = "Neinitializat"

    def SetNumeBanda(self, NumeBanda):
        self.nume=NumeBanda

    def SetMijlocCalculat(self, mijloc):
        self.mijlocCalculat=mijloc


    def setInaltimeSectiune(self, valoare):
        self.inaltimeSectiune=int(valoare)

    def MediereDistantaBanda(self) :
        self.MedDistanta = self.DistantaBandaFrame

    def CalculDistantaBanda(self, lungimeCadru):
        if self.centre.size == 2 :
            self.DistantaBandaFrame = self.centre[1] - self.centre[0]
            print("La "+str(self.nume)+ " - distanta dintre banda dreapta si cea stanga este: " + str(self.DistantaBandaFrame))
            self.MediereDistantaBanda()
            self.mijlocCalculat = int((self.centre[0] + self.centre[1]) / 2)
            self.DistantaFataDeAx = abs(self.mijlocCalculat - int(lungimeCadru / 2))

    def ObtineStructuri(self, lungimeCadruAnalizat, binarization):
        EroareCentruTemporar=0
        for j in range(1, lungimeCadruAnalizat):
            if self.interesant:
                if binarization[self.inaltimeSectiune, j] == 0:
                    self.interesant = False
                    if (1 < EroareCentruTemporar < self.EroareCentru):
                        print("Structuri false. - Nu salvam valoarea")  # de fapt ar trebui sa recalculam centrul nou
                        continue
                    if(int(self.pozitieFinala-self.pozitieInitiala)>150):
                        print("eliminam o structura prea mare")
                        continue
                    EroareCentruTemporar = 1
                    self.pozitieFinala = j
                    self.NumarStructuri= self.NumarStructuri + 1
                    self.pozitieMijloc = int((self.pozitieInitiala + self.pozitieFinala) / 2)
                    self.centre = np.append(self.centre, self.pozitieMijloc)
                    self.pozitieInitiala = 0

                elif (j == lungimeCadruAnalizat - 1):
                    self.NumarStructuri = self.NumarStructuri + 1
                    self.pozitieMijloc = int((self.pozitieInitiala + j) / 2)
                    self.centre = np.append(self.centre, self.pozitieMijloc)
            else:
                if (EroareCentruTemporar > 0) and EroareCentruTemporar < self.EroareCentru:
                    EroareCentruTemporar = EroareCentruTemporar + 1
                if (EroareCentruTemporar == self.EroareCentru):
                    EroareCentruTemporar = 0
            if binarization[self.inaltimeSectiune, j] > 1 and self.interesant == False:
                    self.interesant = True
                    self.pozitieInitiala = j
        return self.centre
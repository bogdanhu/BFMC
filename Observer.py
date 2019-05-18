from statemachine import StateMachine, State
#import SerialHandler
import time
#import statemachine
#https://pypi.org/project/python-statemachine/

class DeplasareMasina(StateMachine):
    initializare = State('initializare', initial=True)
    MergiInainte = State('MergiInainte')
    MergiInainteSiCautaParcare=State('MergiInainteSiCautaParcare')
    Opreste = State('Opreste')
    CurbaDreapta = State('IaCurbaDreapta')
    ParcareLaterala= State('ParcheazaLaterala')
    PlecareDinParcare=State('PleacaDinParcare')
    CurbaStangaDupaStopActiune=State('CurbaStangaDupaStop')

    PleacaDeLaStart = initializare.to(MergiInainte)
    stop = MergiInainte.to(Opreste)
    stoptodo = initializare.to(Opreste)
    PleacaDeLaStop = Opreste.to(MergiInainte)
    CurbaStangaDupaStop=Opreste.to(CurbaStangaDupaStopActiune)
    MergiInainteDupaStop=CurbaStangaDupaStopActiune.to(MergiInainte)
    MergiLaDreapta=MergiInainte.to(CurbaDreapta)
    MergiInainteDupaCurba=CurbaDreapta.to(MergiInainte)

    Parcheaza=initializare.to(ParcareLaterala) #TODO: ar trebui in loc de initializare ceva de genu MergInainteDupaU
    PleacaDinParcare=ParcareLaterala.to(PlecareDinParcare)
    MergiInainteDupaParcare=PlecareDinParcare.to(MergiInainte)

    def on_PleacaDeLaStart(self):
        print('Hai ca plecam')
        #cautam stopul

    def on_stop(self):
        print('STOP.')

    def on_PleacaDeLaStop(self):
        print('GO GO GO!')
        #cautam Drumul
    def on_MergiLaDreapta(self):
        print('o luam la dreapta - sendMove()')
        #cautam Drumul

    def on_Parcheaza(self):
        global serialHandler
        serialHandler = SerialHandler.SerialHandler("/dev/ttyACM0")
        try :
            ## PARCARE STARE
            serialHandler.sendPidActivation(True)
            serialHandler.sendMove(-0.2, 22.0)
            time.sleep(2.7)
            serialHandler.sendMove(-0.2, -22.0)
            time.sleep(2.5)
            serialHandler.sendBrake(0.0)
            time.sleep(2.5)
            ### END OF PARCARE

            ### START PLECARE DIN PARCARE
            serialHandler.sendMove(0.2, -22.0)
            time.sleep(2.2)
            serialHandler.sendMove(0.2, 22.0)
            time.sleep(2.7)
        except:
            print("wtf - n")
#cautam stopul
#masina.stop()
#masina.PleacaDeLaStop()
#masina.
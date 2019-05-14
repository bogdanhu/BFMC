from statemachine import StateMachine, State
#https://pypi.org/project/python-statemachine/

class DeplasareMasina(StateMachine):
    initializare = State('initializare', initial=True)
    MergiInainte = State('MergiInainte')
    Opreste = State('Opreste')
    CurbaDreapta = State('IaCurbaDreapta')
    ParcareLaterala= State('ParcheazaLaterala')
    PlecareDinParcare=State('PleacaDinParcare')
    CurbaStangaDupaStopActiune=State('CurbaStangaDupaStop')

    PleacaDeLaStart = initializare.to(MergiInainte)
    stop = MergiInainte.to(Opreste)
    PleacaDeLaStop = Opreste.to(MergiInainte)
    CurbaStangaDupaStop=Opreste.to(CurbaStangaDupaStopActiune)
    MergiInainteDupaStop=CurbaStangaDupaStopActiune.to(MergiInainte)
    MergiLaDreapta=MergiInainte.to(CurbaDreapta)
    MergiInainteDupaCurba=CurbaDreapta.to(MergiInainte)

    Parcheaza=MergiInainte.to(ParcareLaterala) # ar trebui in loc de MergiInainte ceva de genu MergInainteDupaU
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
        print('parcam lateral')




#cautam stopul
    #masina.stop()
#masina.PleacaDeLaStop()
#masina.
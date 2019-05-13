from statemachine import StateMachine, State
#https://pypi.org/project/python-statemachine/

class DeplasareMasina(StateMachine):
    initializare = State('initializare', initial=True)
    MergiInainte = State('MergiInainte')
    Opreste = State('Opreste')
    CurbaDreapta = State('IaCurbaDreapta')



    PleacaDeLaStart = initializare.to(MergiInainte)
    stop = MergiInainte.to(Opreste)
    PleacaDeLaStop = Opreste.to(MergiInainte)
    MergiLaDreapta=MergiInainte.to(CurbaDreapta)
    MergiInainteDupaCurba=CurbaDreapta.to(MergiInainte)

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


masina = DeplasareMasina()
print(masina.current_state)
print(masina.current_state == DeplasareMasina.initializare == masina.initializare)
masina.PleacaDeLaStart()
print(masina.current_state)
#cautam stopul
    #masina.stop()
#masina.PleacaDeLaStop()
#masina.
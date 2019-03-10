# -*- coding: utf-8 -*-
'''
Created on 17 avr. 2014

@author: S0087931
'''


from time import sleep, time

import RPIO  


class MCZEmitterService(object):
    '''
    classdocs
    '''

    '''Durée fronts'''
    dureeFront = 0.000390;
    '''Durée entre 2 données'''
    dureeInterDonnees = 0.000860;
    '''Durée entre 2 messages'''
    dureeInterMessage = 0.005080;
    '''Nombre d'envois du message'''
    nbEnvois = 5;

    def __init__(self, txPin):
        '''
        Constructor
        '''
        self.txPin = txPin
        
        
    def sendMessage(self, message):
        # set up GPIO output channel
        RPIO.setup(self.txPin, RPIO.OUT)
        for i in range(1,self.nbEnvois) :
            RPIO.output(self.txPin, False)
            for data in range(0,6):
                RPIO.output(self.txPin, True)
                sleep(self.dureeInterDonnees)
                for bit in range(0,11):
                    self.__sendBit(str(message)[data][bit == '1'])                    
            RPIO.output(self.txPin, False)
            sleep(self.dureeInterMessage)
        RPIO.cleanup()
        
    def __sendBit(self, bit):
        if bit :
            RPIO.output(self.txPin, True)
            sleep(self.dureeFront)  
            RPIO.output(self.txPin, False)
            sleep(self.dureeFront)
        else :
            RPIO.output(self.txPin, False)
            sleep(self.dureeFront)
            RPIO.output(self.txPin, True)
            sleep(self.dureeFront)

if __name__ == '__main__':
    None      
        
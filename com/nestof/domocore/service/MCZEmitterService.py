# -*- coding: utf-8 -*-
'''
Created on 17 avr. 2014

@author: S0087931
'''


from time import sleep, time

import wiringpi  


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
        self.io = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_SYS)
        self.io.pinMode(self.txPin,self.io.OUTPUT)  # Setup txPin
        
    def sendMessage(self, message):
        for i in range(1,self.nbEnvois) :
            self.io.digitalWrite(18,self.io.LOW)
            for data in range(0,6):
                self.io.digitalWrite(18,self.io.HIGH)
                sleep(self.dureeInterDonnees)
                for bit in range(0,11):
                    self.__sendBit(str(message)[data][bit == '1'])                    
            self.io.digitalWrite(18,self.io.LOW)
            sleep(self.dureeInterMessage)
        
    def __sendBit(self, bit):
        if bit :
            self.io.digitalWrite(18,self.io.HIGH)
            sleep(self.dureeFront)  
            self.io.digitalWrite(18,self.io.LOW)
            sleep(self.dureeFront)
        else :
            self.io.digitalWrite(18,self.io.LOW)
            sleep(self.dureeFront)
            self.io.digitalWrite(18,self.io.HIGH)
            sleep(self.dureeFront)
            
        
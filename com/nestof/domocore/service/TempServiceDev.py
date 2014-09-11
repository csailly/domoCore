# -*- coding: utf-8 -*-
'''
Created on 16 avr. 2014

@author: nestof
'''
import logging

class TempServiceDev(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(__name__)
        self.logger.debug("##################################")
        self.logger.debug("# TempService Developpement Mode #")
        self.logger.debug("##################################")        
        
    def readTemp(self):
        temp = 18.0
        self.logger.debug("Current temp : " + str(temp) + " °C")                  
        return temp
    
if __name__ == '__main__':
    tempServiceDev = TempServiceDev()
    print(tempServiceDev.readTemp())
        

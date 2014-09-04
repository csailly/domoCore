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
        print("##################################")
        print("# TempService Developpement Mode #")
        print("##################################")        
        
    def readTemp(self):
        temp = 25.0
        self.logger.debug("Current temp : " + str(temp) + " °C");          
        return temp
        

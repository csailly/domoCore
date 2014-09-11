# -*- coding: utf-8 -*-
'''
Created on 16 avr. 2014

@author: nestof
'''
import smbus

class TempService(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.__bus = smbus.SMBus(1)
        self.__address = 0x48
        
    def readTemp(self):
        tmp = self.__bus.read_word_data(self.__address , 0x00)
        Lo = (tmp & 0xff00) >> 8 ;    Hi = (tmp & 0x00ff)
        temp = (((Hi * 256) + Lo) >> 4) * 0.0625      
        return temp
  
if __name__ == '__main__':
    tempService = TempService()
    print(tempService.readTemp())      

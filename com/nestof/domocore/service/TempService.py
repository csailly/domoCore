# -*- coding: utf-8 -*-
'''
Created on 16 avr. 2014

@author: nestof
'''
import glob
import os
import time
import smbus


class Tmp102(object):
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

class DS18B20(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        self.__base_dir = '/sys/bus/w1/devices/'
        self.__device_folder = glob.glob(self.__base_dir + '28*')[0]
        self.__device_file = self.__device_folder + '/w1_slave'

    def read_temp_raw(self):
        f = open(self.__device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def readTemp(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c

  
if __name__ == '__main__':
    tmp102 = Tmp102()
    print(tmp102.readTemp())      

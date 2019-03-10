'''
Created on 9 avr. 2014

@author: S0087931

exemple of usage :

from com.nestof.domocore import utils
....
utils.binaryStringToHex('1100')


'''

from datetime import datetime
import time


def binaryStringToHex(chaine):    
    """ Transform a binary string in hexadecimal value and return it """
    temp = ''
    hexString = ''    
    for bit in chaine:        
        temp += str(bit)
        if(len(temp) == 4):
            hexString += hex(int(temp, 2))[2:]
            temp = ''
    return hexString.upper()
    

def getCurrentDateTime():
    """Return the current dateTime"""
    return datetime.fromtimestamp(time.time())

def getCurrentDate():
    """Return the current date"""
    """Ex. 2014-09-09"""
    return datetime.now().strftime("%Y-%m-%d")

def getCurrentTime():
    """Return the current time"""
    """Ex. 13:19:24"""
    return datetime.now().strftime("%H:%M:%S")

def intToBin3(intValue):
    """Return the binary representation of the int value, with 3 bits length"""
    return bin(intValue)[2:].zfill(3)

def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True


    

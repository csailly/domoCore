'''
Created on 9 avr. 2014

@author: S0087931
'''

from datetime import datetime
import time


        
def binaryStringToHex(chaine):
    """Transform a binary string in hexadecimal value and return it"""
    temp = ''
    hexString = ''    
    for bit in chaine:        
        temp += str(bit)
        if(len(temp) == 4):
            hexString += hex(int(temp,2))[2:]
            temp = ''
    return hexString.upper()
    

def getCurrentDateTime(self):
    return datetime.fromtimestamp(time.time())
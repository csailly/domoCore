'''
Created on 9 avr. 2014

@author: S0087931
'''

class Utils(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def binaryStringToHex(self, chaine):
        temp = ''
        hexString = ''    
        for bit in chaine:        
            temp += str(bit)
            if(len(temp) == 4):
                hexString += hex(int(temp,2))[2:]
                temp = ''
        return hexString.upper()
    
    def temp(self):
        None
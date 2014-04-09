'''
Created on 6 avr. 2014

@author: nestof
'''
from com.nestof.domocore.Utils import Utils

class MCZProtocolService(object):
    '''
    classdocs
    '''

    __remoteCode1 = 0x97d
    __remoteCode2 = 0x999
    __remoteCode3 = 0x813
    
    MODE_AUTO = 1
    MODE_MANU = 2
    
    ETAT_ON = 1
    ETAT_OFF = 2
    
    ACTEUR_SYSTEME = 1
    ACTEUR_UTILISATEUR = 2
    
    PUISS_NIV1 = 1
    PUISS_NIV2 = 2
    PUISS_NIV3 = 3
    PUISS_NIV4 = 4
    PUISS_NIV5 = 5
    
    VENT_NIV1 = 1
    VENT_NIV2 = 2
    VENT_NIV3 = 3
    VENT_NIV4 = 4
    VENT_NIV5 = 5
    VENT_AUTO = 6
    
    __ORDRE_OFF = 0b000
    __ORDRE_ON_AUTO = 0b100
    __ORDRE_ON_MANU = 0b010

    def __init__(self, databaseService):
        '''
        Constructor
        '''
        self.__databaseSevice = databaseService
        self.__utils = Utils()
        
    def getTrame(self, puissance, ventilation, mode, etat, acteur):
        ordre = None
        if (etat == self.ETAT_OFF) :
            ordre = self.__ORDRE_OFF
        elif (mode == self.MODE_AUTO):
            ordre = self.__ORDRE_ON_AUTO
        else :
            ordre = self.__ORDRE_ON_MANU
        
        '''TODO Déterminer flag'''
        flag = 1
        
        trame = self.__getRemoteCode() 
        trame += self.__getData4(puissance, ventilation, ordre)  
        trame += self.__getData5(acteur, flag)  
        trame += self.__getData6(puissance, ventilation, ordre)  
        trame += self.__getData7(acteur,mode, flag)
        return trame
    
    def __getRemoteCode(self):
        return bin(self.__remoteCode1)[2:].zfill(12) + bin(self.__remoteCode2)[2:].zfill(12) + bin(self.__remoteCode3)[2:].zfill(12)
    
    def __getData4(self, puissance, ventilation, ordre):
        data4 = '1' 
        data4 += self.__getBin3(ventilation)  
        data4 += self.__getBin3(puissance)  
        data4 += self.__getBin3(ordre)
        data4 += self.__getParityBit(data4)  
        data4 += '1'
        
        return data4
    
    def __getData5(self, acteur, flag): 
        data5 = '1'
        if(acteur == self.ACTEUR_SYSTEME):
            data5 += '0'
        else:
            data5 += '1'
        data5 += '0'
        data5 += '0'
        data5 += str(flag)
        data5 += '0'
        data5 += '1'
        data5 += '0'
        data5 += '1'
        data5 += '0'
        data5 += self.__getParityBit(data5)
        data5 += '1'
                   
        return data5
    
    def __getData6(self,puissance, ventilation,ordre):
        binVentilation = self.__getBin3(ventilation)
        binPuissance = self.__getBin3(puissance)
        binOrdre = self.__getBin3(ordre)
        
        data6 = '1'
        data6 += str((int(binVentilation[0])^int(binVentilation[1]))^int(binPuissance[2]))
        data6 += str(1^((int(binVentilation[1])^int(binVentilation[2]))^int(binOrdre[0]))) 
        data6 += str(1^((int(ventilation%2 == 0)^int(binPuissance[0]))^int(binOrdre[1])))
        data6 += str(1^int(binPuissance[0]))
        data6 += str(int(binVentilation[0])^int(binPuissance[1]))
        data6 += str(int(binVentilation[1])^int(binPuissance[2]))
        data6 += str(int(ventilation%2 == 0)^int(binOrdre[0]))
        data6 += str(1^(int(binPuissance[0])^int(binOrdre[1])))
        data6 += '0'
        data6 += self.__getParityBit(data6)        
        data6 += '1'

        return data6
    
    def __getData7(self, acteur, mode, flag):      
        data7 = '1'
        if(acteur == self.ACTEUR_SYSTEME):
            data7 += '1'
        else:
            data7 += '0'
        data7 += '1'
        data7 += str(1^flag)
        data7 += str(flag)
        if (acteur == self.ACTEUR_SYSTEME):
            data7 += '0'
        else:
            data7 += '1'
        data7 += '1'
        data7 += '0'
        data7 += str(flag)
        data7 += '0'
        data7 += self.__getParityBit(data7)
        data7 += '1'

        return data7
    
    def __getBin3(self, value):
        return bin(value)[2:].zfill(3)
    
    def __getParityBit(self, value):
        return str(str(value.count('1') %2).count('0'))
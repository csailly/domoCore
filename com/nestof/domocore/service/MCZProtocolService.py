# -*- coding: utf-8 -*-
'''
Created on 6 avr. 2014

@author: nestof
'''


from datetime import datetime

from com.nestof.domocore import  enumeration, utils
from com.nestof.domocore.dao.HistoTrameMczDao import HistoTrameMczDao
from com.nestof.domocore.domain.HistoTrameMCZ import HistoTrameMCZ
from com.nestof.domocore.dto.TrameMcz import TrameMcz


class MCZProtocolService(object):
    '''
    classdocs
    '''

    __remoteCode1 = 0x97d
    __remoteCode2 = 0x999
    __remoteCode3 = 0x813
    

    def __init__(self, database):
        '''
        Constructor
        '''
        self.__database = database
        self.__histoTrameMczDao = HistoTrameMczDao(database)
        
    def getTrame(self, mode, etat, actionneur, puissance, ventilation):
        trame = TrameMcz()
        
        trame._actionneur = actionneur
        trame._order = enumeration.getOrdre(mode, etat)
        trame._flag = self.__getFlag(trame._order, puissance, ventilation, actionneur);
        trame._puissance = puissance
        trame._ventilation = ventilation
         
        message = self.__getRemoteCode() 
        message += self.__getData4(puissance, ventilation, trame._order)  
        message += self.__getData5(actionneur, trame._flag)  
        message += self.__getData6(puissance, ventilation, trame._order)  
        message += self.__getData7(actionneur, mode, trame._flag)
        
        trame._message = message
        
        return trame
    
    def getLastTrame(self):
        lastTrameMCZ = self.__histoTrameMczDao.getLast()
        return lastTrameMCZ
    
    def saveTrame(self, trame):
        histoTrameMcz = HistoTrameMCZ()
        histoTrameMcz._sendDate = utils.getCurrentDateTime()
        histoTrameMcz._actionneur = trame._actionneur  
        histoTrameMcz._puissance = trame._puissance
        histoTrameMcz._ventilation = trame._ventilation
        histoTrameMcz._order = trame._order
        histoTrameMcz._flag = trame._flag
        histoTrameMcz._message = trame._message
    
        histoTrameMczDao = HistoTrameMczDao(self.__database)
        histoTrameMczDao.save(histoTrameMcz)
    
    def __getRemoteCode(self):
        return bin(self.__remoteCode1)[2:].zfill(12) + bin(self.__remoteCode2)[2:].zfill(12) + bin(self.__remoteCode3)[2:].zfill(12)
    
    def __getData4(self, puissance, ventilation, ordre):
        """ 
        Construct the data #4 
        - bit 1 => 1
        - bits 2 à 4 => niveau de ventilation
        - bits 5 à 7 => puissance chauffe
        - bits 8 à 10 => ordre
        - bit 11 => bit de parité sur les bits 1 à 10
        - bit 12 => 1
        """
        
        data4 = '1' 
        data4 += ventilation.getBinValue() 
        data4 += puissance.getBinValue()   
        data4 += ordre.getBinValue() 
        data4 += self.__getParityBit(data4)  
        data4 += '1'
        
        return data4
    
    def __getData5(self, actionneur, flag):
        """
        Construct the data #5
        - bit 1 => 1
        - bit 2 => (actionneur == utilisateur)
        - bit 3 => 0
        - bit 4 => 0
        - bit 5 => flag
        - bit 6 => 0
        - bit 7 => 1
        - bit 8 => 0
        - bit 9 => 1
        - bit 10 => 0
        - bit 11 => bit de parité sur les bits 1 à 10
        - bit 12 => 1
        """
        
        data5 = '1'
        if(actionneur == enumeration.Actionneur.systeme):
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
    
    def __getData6(self, puissance, ventilation, ordre):
        """
        Construct the data #6
        - bit 1 => 1
        - bit 2 => XOR (XOR (1er bit Ventilation, 2e bit Ventilation), 3e bit Puissance)
        - bit 3 => NOT (XOR (XOR (2e bit Ventilation,3e bit Ventilation), 1e bit Ordre))
        - bit 4 => NOT (XOR (XOR (Ventilation pair, 1er bit Puissance), 2e bit Ordre))
        - bit 5 => NOT (1er bit Puissance)
        - bit 6 => XOR (1er bit Ventilation, 2e bit Puissance)
        - bit 7 => XOR (2e bit Ventilation, 3e bit Puissance)
        - bit 8 => XOR (Ventilation pair, 1e bit Ordre))
        - bit 9 => NOT (XOR (1er bit Puissance, 2e bit Ordre))
        - bit 10 => 0
        - bit 11 => Bit de parité des bits 2 à 10
        - bit 12 => 1
        """
        
        binVentilation = ventilation.getBinValue() 
        binPuissance = puissance.getBinValue() 
        binOrdre = ordre.getBinValue() 
        
        data6 = '1'
        data6 += str((int(binVentilation[0]) ^ int(binVentilation[1])) ^ int(binPuissance[2]))
        data6 += str(1 ^ ((int(binVentilation[1]) ^ int(binVentilation[2])) ^ int(binOrdre[0]))) 
        data6 += str(1 ^ ((int(ventilation.value % 2 == 0) ^ int(binPuissance[0])) ^ int(binOrdre[1])))
        data6 += str(1 ^ int(binPuissance[0]))
        data6 += str(int(binVentilation[0]) ^ int(binPuissance[1]))
        data6 += str(int(binVentilation[1]) ^ int(binPuissance[2]))
        data6 += str(int(ventilation.value % 2 == 0) ^ int(binOrdre[0]))
        data6 += str(1 ^ (int(binPuissance[0]) ^ int(binOrdre[1])))
        data6 += '0'
        data6 += self.__getParityBit(data6)        
        data6 += '1'

        return data6
    
    def __getData7(self, actionneur, mode, flag):
        """
        Construct the data #7
        - bit 1 => 1
        - bit 2 => (actionneur == systeme)
        - bit 3 => 1
        - bit 4 => NOT(flag)
        - bit 5 => flag
        - bit 6 => (actionneur == utilisateur)
        - bit 7 => 1
        - bit 8 => 0
        - bit 9 => flag
        - bit 10 => 0
        - bit 11 => Bit de parité des bits 2 à 10
        - bit 12 => 1
        """
              
        data7 = '1'
        if(actionneur == enumeration.Actionneur.systeme):
            data7 += '1'
        else:
            data7 += '0'
        data7 += '1'
        data7 += str(1 ^ flag)
        data7 += str(flag)
        if (actionneur == enumeration.Actionneur.systeme):
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
    

    
    def __getParityBit(self, value):
        return str(str(value.count('1') % 2).count('0'))
    
    def __getFlag(self, ordre, puissance, ventilation, actionneur):
        """ Return the flag to use to construct the new trame message """
        
        lastTrameMCZ = self.__histoTrameMczDao.getLast()
        lastTrameMCZActionneur = self.__histoTrameMczDao.getLastForActionneur(actionneur)
    
        if lastTrameMCZ == None or lastTrameMCZActionneur == None:
            return 1
    
        if lastTrameMCZ._actionneur == actionneur and lastTrameMCZ._order == ordre and  lastTrameMCZ._puissance == puissance and  lastTrameMCZ._ventilation == ventilation :
            return 1 ^ int(lastTrameMCZActionneur._flag)
        
        return int(lastTrameMCZActionneur._flag)
    
    
    def getNiveauPuissance(self, currentTemp, consigne):
        """ Return the power level according to current temperature and wanted temperature """
        if currentTemp >= consigne :
            return enumeration.NiveauPuissance.niveau1
        else :
            """ Durée écoulée depuis dernièr allumage """
            lastPowerOnElapsedTime = self.getLastPowerOnElapsedTime()
            
            if (lastPowerOnElapsedTime == None or lastPowerOnElapsedTime <= float(30)):
                return enumeration.NiveauPuissance.niveau5
            else:
                if currentTemp >= consigne - 1 :
                    return enumeration.NiveauPuissance.niveau2
                elif currentTemp >= consigne - 2 :
                    return enumeration.NiveauPuissance.niveau3
                elif currentTemp >= consigne - 3 :
                    return enumeration.NiveauPuissance.niveau4
                else :
                    return enumeration.NiveauPuissance.niveau5
            
    def getLastTrameElapsedTime(self):
        """ Return the elapsed time since the last trame in minute"""
        lastTrame = self.getLastTrame()
        if lastTrame == None :
            return 0   
        lastTime = lastTrame._sendDate
        currentTime = utils.getCurrentDateTime()            
        delta = currentTime - datetime.strptime(lastTime, "%Y-%m-%d %H:%M:%S.%f")
        return (delta.days * 24 * 60 * 60 + delta.seconds) / 60
    
    def isTrameSameAsLastTrame(self, mode, etat, puissance, ventilation):
        """ Test if the current trame and the last trame are same"""
        lastTrame = self.getLastTrame()
                
        if lastTrame == None :
            return False                
        if lastTrame._order != enumeration.getOrdre(mode, etat) :
            return False
        if lastTrame._puissance != puissance :
            return False
        if lastTrame._ventilation != ventilation :
            return False
        return True
        
    def getLastPowerOffElapsedTime(self):
        """ Return  the elapsed time since the last power off in minute"""
        lastPowerOff = self.__histoTrameMczDao.getLastPowerOff()
        if lastPowerOff == None :
            return None   
        lastTime = lastPowerOff._sendDate
        currentTime = utils.getCurrentDateTime()            
        delta = currentTime - datetime.strptime(lastTime, "%Y-%m-%d %H:%M:%S.%f")
        return (delta.days * 24 * 60 * 60 + delta.seconds) / 60    
        
    def getLastPowerOnElapsedTime(self):
        """ Return  the elapsed time since the last power off in minute"""
        lastPowerOff = self.__histoTrameMczDao.getLastPowerOn()
        if lastPowerOff == None :
            return None   
        lastTime = lastPowerOff._sendDate
        currentTime = utils.getCurrentDateTime()            
        delta = currentTime - datetime.strptime(lastTime, "%Y-%m-%d %H:%M:%S.%f")
        return (delta.days * 24 * 60 * 60 + delta.seconds) / 60    
    
    

'''
Created on 6 avr. 2014

@author: nestof
'''
from com.nestof.domocore import  enumeration, utils
from com.nestof.domocore.dao.HistoTrameMczDao import HistoTrameMczDao
from com.nestof.domocore.domain.HistoTrameMCZ import HistoTrameMCZ


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
        
    def getTrame(self, puissance, ventilation, mode, etat, actionneur):
        ordre = enumeration.getOrdre(mode, etat)
        flag = self.getFlag(ordre, puissance, ventilation, actionneur);
        
        trame = self.__getRemoteCode() 
        trame += self.__getData4(puissance, ventilation, ordre)  
        trame += self.__getData5(actionneur, flag)  
        trame += self.__getData6(puissance, ventilation, ordre)  
        trame += self.__getData7(actionneur,mode, flag)
        return trame
    
    def __getRemoteCode(self):
        return bin(self.__remoteCode1)[2:].zfill(12) + bin(self.__remoteCode2)[2:].zfill(12) + bin(self.__remoteCode3)[2:].zfill(12)
    
    def __getData4(self, puissance, ventilation, ordre):
        data4 = '1' 
        data4 += ventilation.getBinValue() 
        data4 += puissance.getBinValue()   
        data4 += ordre.getBinValue() 
        data4 += self.__getParityBit(data4)  
        data4 += '1'
        
        return data4
    
    def __getData5(self, actionneur, flag): 
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
    
    def __getData6(self,puissance, ventilation,ordre):
        binVentilation = ventilation.getBinValue() 
        binPuissance = puissance.getBinValue() 
        binOrdre = ordre.getBinValue() 
        
        data6 = '1'
        data6 += str((int(binVentilation[0])^int(binVentilation[1]))^int(binPuissance[2]))
        data6 += str(1^((int(binVentilation[1])^int(binVentilation[2]))^int(binOrdre[0]))) 
        data6 += str(1^((int(ventilation.value%2 == 0)^int(binPuissance[0]))^int(binOrdre[1])))
        data6 += str(1^int(binPuissance[0]))
        data6 += str(int(binVentilation[0])^int(binPuissance[1]))
        data6 += str(int(binVentilation[1])^int(binPuissance[2]))
        data6 += str(int(ventilation.value%2 == 0)^int(binOrdre[0]))
        data6 += str(1^(int(binPuissance[0])^int(binOrdre[1])))
        data6 += '0'
        data6 += self.__getParityBit(data6)        
        data6 += '1'

        return data6
    
    def __getData7(self, actionneur, mode, flag):      
        data7 = '1'
        if(actionneur == enumeration.Actionneur.systeme):
            data7 += '1'
        else:
            data7 += '0'
        data7 += '1'
        data7 += str(1^flag)
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
        return str(str(value.count('1') %2).count('0'))
    
    def getFlag(self, ordre, puissance, ventilation, actionneur):
        lastTrameMCZ = self.__histoTrameMczDao.getLast()
        lastTrameMCZActionneur = self.__histoTrameMczDao.getLastForActionneur(actionneur)
    
        if lastTrameMCZ == None or lastTrameMCZActionneur == None:
            return 1
    
        if lastTrameMCZ._actionneur == actionneur and lastTrameMCZ._order == ordre and  lastTrameMCZ._puissance == puissance and  lastTrameMCZ._ventilation == ventilation :
            return 1^int(lastTrameMCZActionneur._flag)
        
        return lastTrameMCZActionneur._flag
    
    
    
# -*- coding: utf-8 -*-
'''
Created on 6 avr. 2014

@author: nestof
'''
from com.nestof.domocore import enumeration
from com.nestof.domocore.dao.ModeDao import ModeDao
from com.nestof.domocore.dao.ParameterDao import ParameterDao
from com.nestof.domocore.dao.PeriodDao import PeriodDao
from com.nestof.domocore.dao.HistoTempDao import HistoTempDao
from com.nestof.domocore.domain.Mode import Mode
from com.nestof.domocore.domain.HistoTemp import HistoTemp


class DatabaseService(object):
    '''
    classdocs
    '''


    def __init__(self, database):
        '''
        Constructor
        '''
        self._database = database
        self._periodDao = PeriodDao(database)
        self._modeDao = ModeDao(database)
        self._parametrageDao = ParameterDao(database)
        self._histoTempDao = HistoTempDao(database)    
        
    def findCurrentMode(self):
        """ Return the active mode """
        
        periode = self._periodDao.findCurrent()
    
        mode = None
        
        if periode != None :        
            mode = self._modeDao.findByPk(periode._modeId)
            
        return mode
    
    def findForcedMode(self):
        mode = Mode()  # TODO Récupérer le mode forcé
        mode._libelle = "Forcé"
        mode._cons = float(self._parametrageDao.getValue('TEMP_CONSIGNE_MARCHE_FORCEE'))
        mode._max = float(self._parametrageDao.getValue('TEMP_MAXI_MARCHE_FORCEE'))
        return mode
    
    def findManualMode(self):
        mode = Mode()  # TODO Récupérer le mode manuel
        mode._libelle = "Manuel"
        mode._cons = float(self._parametrageDao.getValue('TEMP_CONSIGNE_MARCHE_FORCEE'))
        mode._max = float(self._parametrageDao.getValue('TEMP_MAXI_MARCHE_FORCEE'))
        return mode
    
    def getStoveActive(self):
        return self._parametrageDao.getValue('POELE_ETAT') == 'ON'
    
    def setStoveActive(self, active):
        if active :
            self._parametrageDao.saveValue('POELE_ETAT', 'ON')
        else :
            self._parametrageDao.saveValue('POELE_ETAT', 'OFF')
    
    def getForcedOn(self):
        return self._parametrageDao.getValue('POELE_MARCHE_FORCEE') == 'TRUE'
    
    def getForcedOff(self):
        return self._parametrageDao.getValue('POELE_ARRET_FORCE') == 'TRUE'
    
    def setForcedOn(self, onForced):
        if onForced:
            self._parametrageDao.saveValue('POELE_MARCHE_FORCEE', 'TRUE')
        else :
            self._parametrageDao.saveValue('POELE_MARCHE_FORCEE', 'FALSE')
    
    def setForcedOff(self, offForced):
        if offForced == True :
            self._parametrageDao.saveValue('POELE_ARRET_FORCE', 'TRUE')
        else :
            self._parametrageDao.saveValue('POELE_ARRET_FORCE', 'FALSE')
            
    def getLastModeId(self):
        return self._parametrageDao.getValue('DERNIER_MODE')
    
    def setLastModeId(self, modeId):
        self._parametrageDao.saveValue('DERNIER_MODE', modeId)
        
    def getConfig(self):
        return enumeration.ConfigurationPeole().getEnum(self._parametrageDao.getValue('POELE_CONFIG'))
    
    def getOrdreManu(self):
        return enumeration.OrdreManuel().getEnum(self._parametrageDao.getValue('ORDRE_MANU'))
    
    def saveTemp(self, date, time, temp):
        histoTemp = HistoTemp()
        histoTemp.date = date
        histoTemp.heure = time
        histoTemp.temp = temp
        
        self._histoTempDao.save(histoTemp)
        

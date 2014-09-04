# -*- coding: utf-8 -*-
'''
Created on 6 avr. 2014

@author: nestof
'''
from com.nestof.domocore.dao.ModeDao import ModeDao
from com.nestof.domocore.dao.ParameterDao import ParameterDao
from com.nestof.domocore.dao.PeriodDao import PeriodDao
from com.nestof.domocore.domain.Mode import Mode
from com.nestof.domocore import enumeration


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
        mode._cons = 19
        mode._max = 22
        return mode
    
    def findManualMode(self):
        mode = Mode()  # TODO Récupérer le mode manuel
        mode._libelle = "Manuel"
        mode._cons = 19
        mode._max = 22
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
        

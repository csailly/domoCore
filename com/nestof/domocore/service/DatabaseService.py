# -*- coding: utf-8 -*-
'''
Created on 6 avr. 2014

@author: nestof
'''
from datetime import datetime, timedelta

from com.nestof.domocore import enumeration
from com.nestof.domocore.dao.HistoTempDao import HistoTempDao
from com.nestof.domocore.dao.ModeDao import ModeDao
from com.nestof.domocore.dao.ParameterDao import ParameterDao
from com.nestof.domocore.dao.PeriodDao import PeriodDao
from com.nestof.domocore.domain.HistoTemp import HistoTemp
from com.nestof.domocore.domain.Mode import Mode
from com.nestof.domocore.dto.PeriodDto import PeriodDto


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
    
    def findNextPeriode(self, currentPeriode):
        if currentPeriode == None:
            return None
        
        nextPeriodDto = None
                  
        _hour, _minute = list(map(int, currentPeriode._endHour.split(':')))
        nextPeriodeTime = datetime.now().replace(hour=_hour, minute=_minute)
        nextPeriodeTime += timedelta(minutes=1)
        
        nextPeriode = self._periodDao.findAtDatetime(nextPeriodeTime)        
        nextMode = None
        
        if nextPeriode != None :        
            nextMode = self._modeDao.findByPk(nextPeriode._modeId)
            nextPeriode._mode = nextMode
        
            nextPeriodDto= PeriodDto(nextPeriode, nextMode)
            
            _hour, _minute = list(map(int, nextPeriode._startHour.split(':')))
            nextPeriodDto._startDatetime = nextPeriodeTime.replace(hour=_hour, minute=_minute)
            
            _hour, _minute = list(map(int, nextPeriode._endHour.split(':')))
            nextPeriodDto._endDatetime = nextPeriodeTime.replace(hour=_hour, minute=_minute)
        
        return nextPeriodDto
    
    def findCurrentPeriode(self):
        periodDto = None
        
        
        now = datetime.now()
        currentPeriode = self._periodDao.findAtDatetime(now)
        currentMode = None
        
        if currentPeriode != None :  
            currentMode = self._modeDao.findByPk(currentPeriode._modeId)
        
            periodDto = PeriodDto(currentPeriode, currentMode)
            
            _hour, _minute = list(map(int, currentPeriode._startHour.split(':')))
            periodDto._startDatetime = now.replace(hour=_hour, minute=_minute)
            
            _hour, _minute = list(map(int, currentPeriode._endHour.split(':')))
            periodDto._endDatetime = now.replace(hour=_hour, minute=_minute)
        
        return periodDto
    
    def findForcedMode(self):
        mode = Mode()
        mode._libelle = "Forcé"
        mode._cons = float(self._parametrageDao.getValue('TEMP_CONSIGNE_MARCHE_FORCEE'))
        mode._max = float(self._parametrageDao.getValue('TEMP_MAXI_MARCHE_FORCEE'))
        return mode
    
    def findManualMode(self):
        mode = Mode()
        mode._libelle = "Manuel"
        mode._cons = float(self._parametrageDao.getValue('TEMP_CONSIGNE_MARCHE_FORCEE'))
        mode._max = float(self._parametrageDao.getValue('TEMP_MAXI_MARCHE_FORCEE'))
        return mode
    
    def isCheckDelays(self):
        return self._parametrageDao.getValue('EMITTER_CHECK_DELAYS') == 'TRUE'
    
    def isStoveActive(self):
        return self._parametrageDao.getValue('POELE_ETAT') == 'ON'
    
    def setStoveActive(self, active):
        if active :
            self._parametrageDao.saveValue('POELE_ETAT', 'ON')
        else :
            self._parametrageDao.saveValue('POELE_ETAT', 'OFF')
    
    def isForcedOn(self):
        return self._parametrageDao.getValue('POELE_MARCHE_FORCEE') == 'TRUE'
    
    def isForcedOff(self):
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
    
    def saveOrdreManu(self, on):
        if on :
            self._parametrageDao.saveValue('ORDRE_MANU', 'ON')
        else :
            self._parametrageDao.saveValue('ORDRE_MANU', 'OFF')
    
    def saveTemp(self, date, time, temp, idSonde):
        histoTemp = HistoTemp()
        histoTemp.date = date
        histoTemp.heure = time
        histoTemp.temp = temp
        histoTemp.sonde = idSonde
        
        self._histoTempDao.save(histoTemp)
        
    def getEmitterSameStartTrameDelay(self):
        return self._parametrageDao.getValue('EMITTER_SAME_START_TRAME_DELAY')
    
    def getEmitterSameStopTrameDelay(self):
        return self._parametrageDao.getValue('EMITTER_SAME_STOP_TRAME_DELAY')
    
    def getEmitterStopTrameSendDuration(self):
        return self._parametrageDao.getValue('EMITTER_STOP_TRAME_SEND_DURATION')
    
    def getEmitterOffMinDuration(self):
        return self._parametrageDao.getValue('EMITTER_OFF_MIN_DURATION')
        
    def getEmitterBoostDuration(self):
        return self._parametrageDao.getValue('EMITTER_BOOST_DURATION')
    
    def getEmitterStartLimitBeforeEndPeriod(self):
        return self._parametrageDao.getValue('EMITTER_START_LIMIT_BEFORE_END_PERIOD')


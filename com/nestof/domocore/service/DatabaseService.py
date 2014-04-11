'''
Created on 6 avr. 2014

@author: nestof
'''
from com.nestof.domocore.dao.ModeDao import ModeDao
from com.nestof.domocore.dao.ParameterDao import ParameterDao
from com.nestof.domocore.dao.PeriodDao import PeriodDao
from com.nestof.domocore.dao.HistoTrameMczDao import HistoTrameMczDao


class DatabaseService(object):
    '''
    classdocs
    '''


    def __init__(self,database):
        '''
        Constructor
        '''
        self._database = database
        self._periodDao = PeriodDao(database)
        self._modeDao = ModeDao(database)
        self._parametrageDao = ParameterDao(database)        
        
    def findCurrentMode(self):
        periode = self._periodDao.findCurrent()
    
        mode = None
        
        if periode != None :        
            mode = self._modeDao.findByPk(periode._modeId)
            
        return mode
    
    def getPoeleActive(self):
        return self._parametrageDao.getValue('POELE_ETAT') == 'ON'
    
    def getForcedOn(self):
        return self._parametrageDao.getValue('POELE_MARCHE_FORCEE') == 'TRUE'
    
    def getForcedOff(self):
        return self._parametrageDao.getValue('POELE_ARRET_FORCE') == 'TRUE'
        
# -*- coding: utf-8 -*-
'''
Created on 23 mars 2014

@author: nestof
'''

class HistoTrameMCZ(object):
    '''
    classdocs
    '''
    tableName = 'histoTrameMCZ'
    colSendDateName = 'dateEnvoi'
    colOrderName = 'ordre'
    colPuissanceName ='puissance'
    colVentilationName = 'ventilation'
    colFlagName = 'flagTrame'
    colActionneurName = 'typeOrdre'
    colMessageName = 'message'

    def __init__(self):
        '''
        Constructor
        '''
        self._sendDate = None
        self._order = None
        self._puissance = None
        self._ventilation = None
        self._flag = None
        self._actionneur = None
        self._message = None
        
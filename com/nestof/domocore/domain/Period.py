# -*- coding: utf-8 -*-
'''
Created on 21 mars 2014

@author: S0087931
'''



class Period(object):
    '''
    classdocs
    '''

    tableName = 'periode'
    colIdName = 'id'
    colDayName = 'jour'
    colStartDateName = 'dateDebut'
    colEndDateName = 'dateFin'
    colStartHourName = 'heureDebut'
    colEndHourName = 'heureFin'
    colModeIdName = 'modeId'

    def __init__(self):
        '''
        Constructor
        '''
        self._id = None
        self._day = None
        self._startDate = None
        self._endDate = None
        self._startHour = None
        self._endHour = None
        self._modeId = None
        
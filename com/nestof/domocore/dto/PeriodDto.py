# -*- coding: utf-8 -*-
'''
Created on 21 mars 2014

@author: S0087931
'''



class PeriodDto(object):
    '''
    classdocs
    '''



    def __init__(self, period, mode):
        '''
        Constructor
        '''
        self._id = period._id
        self._day = period._day
        self._startDate = period._startDate
        self._endDate = period._endDate
        self._startHour = period._startHour
        self._endHour = period._endHour
        self._mode = mode
        self._startDatetime = None
        self._endDatetime = None
        
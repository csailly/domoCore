# -*- coding: utf-8 -*-
'''
Created on 23 mars 2014

@author: nestof
'''

class HistoTemp(object):
    '''
    classdocs
    '''
    tableName = 'histo_temp'
    colDate = 'date'
    colTime = 'heure'
    colTemp = 'temp'
    colSonde = 'sonde'

    def __init__(self):
        '''
        Constructor
        '''
        self.date = None
        self.heure = None
        self.temp = None
        self.sonde = None        
        
# -*- coding: utf-8 -*-
'''
Created on 23 mars 2014

@author: nestof
'''

class Mode(object):
    '''
    classdocs
    '''

    tableName = 'mode'
    colIdName = 'id'
    colLibelleName = 'libelle'
    colConsName = 'cons'
    colMaxName = 'max'

    def __init__(self):
        '''
        Constructor
        '''
        self._id = None
        self._libelle = None
        self._cons = None
        self._max = None
        
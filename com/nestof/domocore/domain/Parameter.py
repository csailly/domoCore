# -*- coding: utf-8 -*-
'''
Created on 23 mars 2014

@author: nestof
'''

class Parameter(object):
    '''
    classdocs
    '''
    tableName = 'parametrage'
    colCodeName = 'code'
    colTypeName = 'type'
    colValueName = 'valeur'
    colCommentName = 'commentaire'

    def __init__(self):
        '''
        Constructor
        '''
        self._code = None
        self._type = None
        self._value = None
        self._comment = None
        
# -*- coding: utf-8 -*-
'''
Created on 11 avr. 2014

@author: S0087931
'''
import sqlite3

from com.nestof.domocore import enumeration, utils
from com.nestof.domocore.domain.HistoTemp import HistoTemp


class HistoTempDao(object):
    '''
    classdocs
    '''


    def __init__(self, database):
        '''
        Constructor
        '''
        self._database = database
       
    def save(self, histoTemp):
        try :
            db = sqlite3.connect(self._database)
            cursor = db.cursor()
            requete = 'INSERT INTO ' + HistoTemp.tableName
            requete += '( '
            requete += HistoTemp.colDate + ','
            requete += HistoTemp.colTime + ','
            requete += HistoTemp.colTemp 
            requete += ' ) '
            requete += ' VALUES(?,?,?)'
            
            cursor.execute(requete, (histoTemp.date, histoTemp.heure, histoTemp.temp))
            
            db.commit()            
        except Exception as e:
            # Roll back any change if something goes wrong
            db.rollback()
            raise e
        finally:
            # Close the db connection
            db.close()
            
            
    

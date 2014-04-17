# -*- coding: utf-8 -*-
'''
Created on 2 avr. 2014

@author: nestof
'''
import sqlite3

from com.nestof.domocore.domain.Period import Period


class PeriodDao(object):
    '''
    classdocs
    '''


    def __init__(self, database):
        '''
        Constructor
        '''
        self._database = database
        
    def findCurrent(self):
        periode = None
        
        try :
            db = sqlite3.connect(self._database)
            cursor = db.cursor()
            
            requete = '''select * from ('''
            requete += ''' SELECT * FROM ''' + Period.tableName + ''' p where '''
            ''' On récupère la période à la date courante '''
            requete += ''' ((p.''' + Period.colStartDateName + ''' <= date('now') and p.''' + Period.colEndDateName + ''' > date('now'))     and p.''' + Period.colStartHourName + ''' <= time('now', 'localtime') and p.''' + Period.colEndHourName + ''' > time('now', 'localtime')) '''
            requete += ''' or '''
            ''' Ou la période du jour calendaire '''
            requete += ''' (p.jour = strftime('%w') and p.''' + Period.colStartHourName + ''' <= time('now', 'localtime') and p.''' + Period.colEndHourName + ''' > time('now', 'localtime')) '''
            ''' On trie pour obtenir en priorité la période à la date courante '''
            requete += ''' order by  p.''' + Period.colStartDateName + ''' desc, p.''' + Period.colEndDateName + ''' asc '''
            ''' On ne retient alors que le 1er résultat '''
            requete += ''' ) limit 1 ''' 
            
            cursor.execute(requete)
    
            result = cursor.fetchone()
            
            
            
            if result == None :
                print('Aucune période de définie')
            else :
                periode = Period()
                periode._id = result[0]
                periode._day = result[1]
                periode._startDate = result[2]
                periode._endDate = result[3]
                periode._startHour = result[4]
                periode._endHour = result[5]
                periode._modeId = result[6]
            
        except Exception as e:
            # Roll back any change if something goes wrong
            db.rollback()
            raise e
        finally:
            # Close the db connection
            db.close()
            return periode
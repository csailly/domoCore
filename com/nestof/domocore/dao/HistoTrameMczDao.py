# -*- coding: utf-8 -*-
'''
Created on 11 avr. 2014

@author: S0087931
'''
import sqlite3
import logging

from com.nestof.domocore import enumeration, utils
from com.nestof.domocore.domain.HistoTrameMCZ import HistoTrameMCZ


class HistoTrameMczDao(object):
    '''
    classdocs
    '''


    def __init__(self, database):
        '''
        Constructor
        '''
        self._logger = logging.getLogger(__name__)
        self._database = database
        
    def getLast(self):
        histoTrameMcz = None
        
        try :
            db = sqlite3.connect(self._database)
            cursor = db.cursor()
            
            requete = 'SELECT * FROM ' + HistoTrameMCZ.tableName
            requete += ' order by ' + HistoTrameMCZ.colSendDateName + ' DESC '
            requete += ' limit 1 ' 
            
            cursor.execute(requete)
    
            result = cursor.fetchone()
            
            
            
            if result == None :
                self._logger.debug('Aucune trame')
            else :
                histoTrameMcz = HistoTrameMCZ()
                histoTrameMcz._actionneur = enumeration.Actionneur().getEnum(int(result[5]))
                histoTrameMcz._flag = result[4]
                histoTrameMcz._order = enumeration.Ordre().getEnum(int(result[1]))
                histoTrameMcz._puissance = enumeration.NiveauPuissance().getEnum(int(result[2]))
                histoTrameMcz._sendDate = result[0]
                histoTrameMcz._ventilation = enumeration.NiveauVentilation().getEnum(int(result[3]))
                
                
            
        except Exception as e:
            # Roll back any change if something goes wrong
            db.rollback()
            raise e
        finally:
            # Close the db connection
            db.close()
            return histoTrameMcz
                                
    def getLastForActionneur(self, actionneur):
        histoTrameMcz = None
        
        try :
            db = sqlite3.connect(self._database)
            cursor = db.cursor()
            
            requete = 'SELECT * FROM ' + HistoTrameMCZ.tableName
            requete += ' WHERE '
            requete += HistoTrameMCZ.colActionneurName + ' = ?'
            requete += ' order by ' + HistoTrameMCZ.colSendDateName + ' DESC '
            requete += ' limit 1 ' 
            
            cursor.execute(requete, (str(actionneur.value)))
    
            result = cursor.fetchone()
            
            
            
            if result == None :
                self._logger.debug('Aucune trame')
            else :
                histoTrameMcz = HistoTrameMCZ()
                histoTrameMcz._actionneur = enumeration.Actionneur().getEnum(int(result[5]))
                histoTrameMcz._flag = result[4]
                histoTrameMcz._order = enumeration.Ordre().getEnum(int(result[1]))
                histoTrameMcz._puissance = enumeration.NiveauPuissance().getEnum(int(result[2]))
                histoTrameMcz._sendDate = result[0]
                histoTrameMcz._ventilation = enumeration.NiveauVentilation().getEnum(int(result[3]))
                
                
            
        except Exception as e:
            # Roll back any change if something goes wrong
            db.rollback()
            raise e
        finally:
            # Close the db connection
            db.close()
            return histoTrameMcz
        
    def save(self, histoTrameMcz):
        try :
            db = sqlite3.connect(self._database)
            cursor = db.cursor()
            requete = 'INSERT INTO ' + HistoTrameMCZ.tableName
            requete += '( '
            requete += HistoTrameMCZ.colSendDateName + ','
            requete += HistoTrameMCZ.colOrderName + ','
            requete += HistoTrameMCZ.colPuissanceName + ','
            requete += HistoTrameMCZ.colVentilationName + ','
            requete += HistoTrameMCZ.colFlagName + ','
            requete += HistoTrameMCZ.colActionneurName + ','
            requete += HistoTrameMCZ.colMessageName
            requete += ' ) '
            requete += ' VALUES(?,?,?,?,?,?,?)'
            
            cursor.execute(requete, (histoTrameMcz._sendDate, histoTrameMcz._order.value, histoTrameMcz._puissance.value, histoTrameMcz._ventilation.value, histoTrameMcz._flag, histoTrameMcz._actionneur.value, utils.binaryStringToHex(histoTrameMcz._message)))
            
            db.commit()            
        except Exception as e:
            # Roll back any change if something goes wrong
            db.rollback()
            raise e
        finally:
            # Close the db connection
            db.close()
            
            
    def getLastPowerOff(self):
        histoTrameMcz = None
        
        try :
            db = sqlite3.connect(self._database)
            cursor = db.cursor()
            
            requete = 'SELECT * FROM ' + HistoTrameMCZ.tableName + ' h1' 
            requete += ' WHERE h1.' + HistoTrameMCZ.colOrderName + ' = 0 and h1.' + HistoTrameMCZ.colSendDateName + ' > ' 
            requete += ' (SELECT h.' + HistoTrameMCZ.colSendDateName + ' FROM ' + HistoTrameMCZ.tableName + ' h WHERE h.' + HistoTrameMCZ.colOrderName + ' <> 0 order by h.' + HistoTrameMCZ.colSendDateName + ' desc limit 1) ' 
            requete += ' ORDER BY h1.' + HistoTrameMCZ.colSendDateName + ' ASC limit 1 '
             
            
            cursor.execute(requete)
    
            result = cursor.fetchone()
            
            
            
            if result == None :
                self._logger.debug('Aucune trame')
            else :
                histoTrameMcz = HistoTrameMCZ()
                histoTrameMcz._actionneur = enumeration.Actionneur().getEnum(int(result[5]))
                histoTrameMcz._flag = result[4]
                histoTrameMcz._order = enumeration.Ordre().getEnum(int(result[1]))
                histoTrameMcz._puissance = enumeration.NiveauPuissance().getEnum(int(result[2]))
                histoTrameMcz._sendDate = result[0]
                histoTrameMcz._ventilation = enumeration.NiveauVentilation().getEnum(int(result[3]))
                
                
            
        except Exception as e:
            # Roll back any change if something goes wrong
            db.rollback()
            raise e
        finally:
            # Close the db connection
            db.close()
            return histoTrameMcz

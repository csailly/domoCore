'''
Created on 6 avr. 2014

@author: nestof
'''
import sqlite3

from com.nestof.domocore.domain.Mode import Mode


class ModeDao(object):
    '''
    classdocs
    '''


    def __init__(self, database):
        '''
        Constructor
        '''
        self._database = database
        
    def findByPk(self, modeId):
        try :
            db = sqlite3.connect(self._database)
            cursor = db.cursor()
            
            requete = 'SELECT * FROM ' + Mode.tableName + ' where '+ Mode.colIdName+'=?'
            
            cursor.execute(requete, (modeId,))
            
            result = cursor.fetchone()
            
            mode = None
            
            if result == None :
                print('Aucun mode trouvé')
            else :
                mode = Mode()
                mode._id = result[0]
                mode._libelle = result[1]
                mode._cons = result[2]
                mode._max = result[3]
        
        except Exception as e:
            # Roll back any change if something goes wrong
            db.rollback()
            raise e
        finally:
            # Close the db connection
            db.close()
            return mode
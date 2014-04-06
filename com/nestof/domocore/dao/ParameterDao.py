'''
Created on 2 avr. 2014

@author: nestof
'''
import sqlite3

from com.nestof.domocore.domain.Parameter import Parameter


class ParameterDao(object):
    '''
    classdocs
    '''


    def __init__(self, database):
        '''
        Constructor
        '''
        self._database = database
        
    def getValue(self, code):
        value = None
        
        try :
            db = sqlite3.connect(self._database)
            
            cursor = db.cursor()
            cursor.execute('''SELECT ''' + Parameter.colValueName + ''' FROM ''' + Parameter.tableName + ''' WHERE ''' + Parameter.colCodeName + '''=?''', (code,))
            result = cursor.fetchone()

            value = result[0] 
    
        except Exception as e:
            # Roll back any change if something goes wrong
            db.rollback()
            raise e
        finally:
            # Close the db connection
            db.close()
            return value
    
    def saveValue(self, code, value):
        try :
            db = sqlite3.connect(self._database)

            cursor = db.cursor()
            cursor.execute('''UPDATE ''' + Parameter.tableName + ''' SET ''' + Parameter.colValueName + '''=? WHERE ''' + Parameter.colCodeName + '''=?''', (value, code))
            db.commit()
    
        except Exception as e:
            # Roll back any change if something goes wrong
            db.rollback()
            raise e
        finally:
            # Close the db connection
            db.close()
        
'''
Created on 21 mars 2014

@author: S0087931
'''
from com.nestof.domocore.Periode import Periode
import sqlite3

if __name__ == '__main__':
    print("Toto")
    periode = Periode()
    periode.jour = 1
    
    
    db = sqlite3.connect('D:/+sandbox/nginx-1.5.7/html/domotique.sqlite')
    
    db.close()
    
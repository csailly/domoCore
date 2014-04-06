'''
Created on 21 mars 2014

@author: S0087931
'''
from com.nestof.domocore.dao.ModeDao import ModeDao
from com.nestof.domocore.dao.ParameterDao import ParameterDao
from com.nestof.domocore.dao.PeriodDao import PeriodDao


if __name__ == '__main__':
 
    database = 'd:/tmp/domotique.sqlite'
    
    periodDao = PeriodDao(database)
    periode = periodDao.findCurrent()
    
    if periode != None :
        modeDao = ModeDao(database)
        mode = modeDao.findByPk(periode._modeId)
        print(mode._libelle)
        print(mode._cons)
    
    parametrageDao = ParameterDao(database)
    valeur = parametrageDao.getValue('POELE_ETAT')
    print(valeur)

    

'''
Created on 21 mars 2014

@author: S0087931
'''

from com.nestof.domocore.Utils import Utils
from com.nestof.domocore.service.DatabaseService import DatabaseService
from com.nestof.domocore.service.MCZProtocolService import MCZProtocolService


if __name__ == '__main__':
 
    database = 'd:/tmp/domotique.sqlite'
    
    databaseService = DatabaseService(database)
    
    mode = databaseService.findCurrentMode();
    print(mode._libelle)
    
    
    print(databaseService.getForcedOff())
    print(databaseService.getForcedOn())
    print(databaseService.getPoeleActive())
    
    mczProtocolService = MCZProtocolService(databaseService);
    
    puissance = MCZProtocolService.PUISS_NIV1
    ventilation = MCZProtocolService.VENT_NIV5
    mode = MCZProtocolService.MODE_MANU
    etat = MCZProtocolService.ETAT_ON
    acteur = MCZProtocolService.ACTEUR_UTILISATEUR
    
    
    trame = mczProtocolService.getTrame(puissance, ventilation, mode, etat, acteur)
   
    
    utils = Utils()
    print(utils.binaryStringToHex(trame))


    

    

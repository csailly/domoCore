'''
Created on 21 mars 2014

@author: S0087931
'''



from com.nestof.domocore import enumeration
from com.nestof.domocore import utils
from com.nestof.domocore.service.DatabaseService import DatabaseService
from com.nestof.domocore.service.MCZProtocolService import MCZProtocolService


if __name__ == '__main__':
    
    
    databasePath = "D:\+sandbox\work\domocore\domotique.sqlite"
    
    databaseService = DatabaseService(databasePath)
    mczProtocolService = MCZProtocolService(databasePath)
    
    
    
    currentMode = databaseService.findCurrentMode()
    if currentMode  != None : 
        print("Mode : " + currentMode._libelle)
        print("Consigne : " + str(currentMode._cons))
        print("Max : " + str(currentMode._max))

       
    trame = mczProtocolService.getTrame(enumeration.NiveauPuissance.niveau3, enumeration.NiveauVentilation.niveau3, enumeration.Mode.automatique, enumeration.Etat.on, enumeration.Actionneur.utilisateur)
    print("Trame message : " + utils.binaryStringToHex(trame._message))
   
    mczProtocolService.saveTrame(trame)

    
    
    
    

        
    
    
    
    
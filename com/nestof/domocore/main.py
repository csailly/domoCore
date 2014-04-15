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
    
    
    onPeriode = currentMode  != None
    offPeriode = currentMode  == None
    
    if onPeriode : 
        print("Mode : " + currentMode._libelle)
        print("Consigne : " + str(currentMode._cons))
        print("Max : " + str(currentMode._max))


    poeleActive = databaseService.getPoeleActive() 
    forcedOn = databaseService.getForcedOn()
    forcedOff = databaseService.getForcedOff()

    print("Poêle actif : " + str(poeleActive))
    print("Marche forcée : " + str(forcedOn))
    print("Arrêt forcé : " + str(forcedOff))
    
    
    
    
    """RAZ forced stat"""
    if offPeriode and forcedOff :
        #TODO RAZ forcedOff
        None
    elif onPeriode and forcedOn :
        #TODO RAZ forcedOn
        None
        
    """ Init start and stop """
    start = False
    stop = False
    if onPeriode or forcedOn :
        start = True
        stop = False
    elif offPeriode or forcedOff :
        start = False
        stop = True
    
    if onPeriode :
        #TODO Read current temp
        currentTemp = 17.0
        if currentTemp >= currentMode._cons :
            stop = True
            start = False
        else :
            #TODO déterminer les niveaux
            None
    
       
    trame = mczProtocolService.getTrame(enumeration.NiveauPuissance.niveau3, enumeration.NiveauVentilation.niveau3, enumeration.Mode.automatique, enumeration.Etat.on, enumeration.Actionneur.utilisateur)
    print("Trame message : " + utils.binaryStringToHex(trame._message))
   
    mczProtocolService.saveTrame(trame)

    
    
    
    

        
    
    
    
    
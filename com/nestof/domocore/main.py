'''
Created on 21 mars 2014

@author: S0087931
'''



from os.path import os

from com.nestof.domocore import enumeration
from com.nestof.domocore import utils
from com.nestof.domocore.service.DatabaseService import DatabaseService
from com.nestof.domocore.service.MCZProtocolService import MCZProtocolService



if __name__ == '__main__':
    

    
    #databasePath = "D:\+sandbox\work\domocore"
    databasePath = "D:\Documents\Work\domoCore"
    databaseFilename = "domotique.sqlite"
    
    databaseService = DatabaseService(databasePath+"\\"+databaseFilename)
    mczProtocolService = MCZProtocolService(databasePath+"\\"+databaseFilename)
    
    """ Current Mode"""    
    currentMode = databaseService.findCurrentMode()

    onPeriode = currentMode  != None
    if onPeriode : 
        print("Mode            : " + currentMode._libelle)
        print("Consigne        : " + str(currentMode._cons) + "°C")
        print("Max             : " + str(currentMode._max) + "°C")

    """ Stove state"""
    stoveIsOn = databaseService.getStoveActive()
    print("\nPoêle actif     : " + str(stoveIsOn))
    
    """ Forced flags""" 
    onForced = databaseService.getForcedOn()
    offForced = databaseService.getForcedOff()
    print("\nMarche forcée   : " + str(onForced))
    print("Arrêt forcé     : " + str(offForced))
    
    """ Forced mode """
    forcedMode = databaseService.findForcedMode()
    print("\nMode            : " + forcedMode._libelle)
    print("Consigne        : " + str(forcedMode._cons) + "°C")
    print("Max             : " + str(forcedMode._max) + "°C")
    
    """ The current temp """    
    currentTemp = 19.0#tempService.readTemp();
    print("\nTempérature     : " + str(currentTemp) + "°C")
    
    """ current mode temp zones"""
    tempZone1 = currentTemp < currentMode._cons
    tempZone3 =  currentTemp >= currentMode._max
    tempZone2 = not tempZone1 and not tempZone3
    
    """ forced mode temp zones"""
    tempForcedZone1 = currentTemp < forcedMode._cons
    tempForcedZone3 =  currentTemp >= forcedMode._max
    tempForcedZone2 = not tempForcedZone1 and not tempForcedZone3
    
    """RAZ forced flags"""
    if (onForced and offForced) :
        databaseService.setForcedOff(False)
        databaseService.setForcedOn(False)
        onForced = False
        offForced = False
    elif (offForced and not onPeriode):
        databaseService.setForcedOff(False)
        offForced = False
        None
    elif (onForced and onPeriode):
        if stoveIsOn :
            databaseService.setForcedOn(False)
            onForced = False
        elif tempZone1 or tempZone3 :
            databaseService.setForcedOn(False)
            onForced = False
    
     
    startStove = False
    shutdownStove = False
    
    
    niveauPuissance = enumeration.NiveauPuissance.niveau1
    niveauVentilation = enumeration.NiveauVentilation.auto
    trameMode = enumeration.Mode.automatique
    trameEtat = enumeration.Etat.off
    trameActionneur = enumeration.Actionneur.utilisateur
    
          
    """ Start / Continue cases"""
    if onPeriode:
        if (not onForced and not offForced and tempZone1) or (not onForced and not offForced and tempZone2 and stoveIsOn) or (not stoveIsOn and onForced and tempZone2):
            niveauPuissance = mczProtocolService.getNiveauPuissance(currentTemp, currentMode._cons);
            startStove = True
    elif onForced and (tempForcedZone1 or tempForcedZone2) :
        if tempForcedZone1 :
            niveauPuissance = mczProtocolService.getNiveauPuissance(currentTemp, forcedMode._cons);
            startStove = True
    
    if startStove:
        trameEtat = enumeration.Etat.on
    else : 
        """ Stop cases """    
        if stoveIsOn :
            if (not onPeriode and not onForced and not offForced) or (onPeriode and not onForced and offForced) or (onPeriode and not onForced and not offForced and tempZone3) or (not onPeriode and onForced and not offForced and tempForcedZone3) :
                shutdownStove = True
        
    if shutdownStove :
        trameEtat = enumeration.Etat.off
        lastTrame = mczProtocolService.getLastTrame()
        if lastTrame != None :
            niveauPuissance = lastTrame._puissance
            niveauVentilation = lastTrame._ventilation                        
        
            

    print("\nstartStove     : " + str(startStove))
    print("shutdownStove  : " + str(shutdownStove))
    
   
   
    if startStove or shutdownStove :
        print("\nEnvoi trame")
        print("Etat            : " + trameEtat.name)
        print("Mode            : " + trameMode.name)
        print("Actionneur      : " + trameActionneur.name)
        print("Puissance       : " + niveauPuissance.name)
        print("Ventilation     : " + niveauVentilation.name)
        
        trame = mczProtocolService.getTrame(trameMode, trameEtat, trameActionneur, niveauPuissance, niveauVentilation)
        print("Trame message bin: " + trame._message)
        print("Trame message hex: " + utils.binaryStringToHex(trame._message))
                   
        try:
            #TODO Envoyer la trame ici
            if startStove : 
                databaseService.setStoveActive(True)
            else :
                databaseService.setStoveActive(False)
            mczProtocolService.saveTrame(trame)        
        except Exception as e:
            # TODO ajouter log en base
            None
        finally:
            None
        
    print(os.getpid())

    
    
    
    

        
    
    
    
    
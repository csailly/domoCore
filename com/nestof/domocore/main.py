# -*- coding: utf-8 -*-
'''
Created on 21 mars 2014

@author: S0087931
'''

from os.path import os, sys

pathname = os.path.dirname(sys.argv[0])
sys.path.append(os.path.abspath(pathname)+"/../../../")

from com.nestof.domocore import enumeration
from com.nestof.domocore import utils
from com.nestof.domocore.service.DatabaseService import DatabaseService
from com.nestof.domocore.service.MCZEmitterService import MCZEmitterService
from com.nestof.domocore.service.MCZProtocolService import MCZProtocolService
from com.nestof.domocore.service.TempService import TempService






if __name__ == '__main__':
    
    print( utils.getCurrentDateTime())
    """ Database configuration """
    databasePath = None
    
    if sys.platform.startswith('linux') :
        databasePath = "/home/pi/syno/"
    elif sys.platform.startswith('win') :
        #databasePath = "D:\+sandbox\work\domocore\\"
        databasePath = "D:\Documents\Work\domoCore\\"
    else :
        print("Unknown Operating System : " + sys.platform)
        exit(1)
        
    databaseFilename = "domotique.sqlite"


    try:
        with open(databasePath+databaseFilename) as file:
            pass
    except IOError as e:
        print("Unable to open file "+ databasePath+databaseFilename) #Does not exist OR no read permissions
        exit(1)

    """ Send message program  """
    emmitterCommand = ""
    emmitterTxPin = 11    

    """ Services """    
    databaseService = DatabaseService(databasePath+databaseFilename)
    mczProtocolService = MCZProtocolService(databasePath+databaseFilename)
    tempService = TempService()
    mczEmitterService = MCZEmitterService(emmitterTxPin)
    
    """ Current Mode"""    
    currentMode = databaseService.findCurrentMode()

    onPeriode = currentMode  != None
    if onPeriode :
        print("Mode            : " + currentMode._libelle)
        print("Consigne        : " + str(currentMode._cons) + "°C")
        print("Max             : " + str(currentMode._max) + "°C")

    """ Last mode id """
    lastModeId = databaseService.getLastModeId()
    print("Dernier mode :" + str(databaseService))

    """ Stove state"""
    stoveIsOn = databaseService.getStoveActive()
    print("Poêle actif     : " + str(stoveIsOn))
    
    """ Forced flags""" 
    onForced = databaseService.getForcedOn()
    offForced = databaseService.getForcedOff()
    print("Marche forcée   : " + str(onForced))
    print("Arrêt forcé     : " + str(offForced))
    
    """ Forced mode """
    forcedMode = databaseService.findForcedMode()
    print("Mode            : " + forcedMode._libelle)
    print("Consigne        : " + str(forcedMode._cons) + "°C")
    print("Max             : " + str(forcedMode._max) + "°C")
    
    """ The current temp """    
    currentTemp = tempService.readTemp();
    print("\nTempérature     : " + str(currentTemp) + "°C")
    
    """ current mode temp zones"""
    if onPeriode :        
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
    elif lastModeId != None and currentMode != None and currentMode._id != lastModeId :
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
    trameActionneur = enumeration.Actionneur.systeme
    
          
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
        if offForced and stoveIsOn:
            trameActionneur = enumeration.Actionneur.utilisateur
            
    if startStove :
        if onForced and not stoveIsOn :
            trameActionneur = enumeration.Actionneur.utilisateur
        
            

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
        
        
        lastTrameIsSame = mczProtocolService.isTrameSameAsLastTrame(trame)
        lastTrameElapsesTime = mczProtocolService.getLastTrameElapsedTime()
        
        print("Dernière trame identique : "+ str(lastTrameIsSame))
        print("Temps écoulé : "+ str(lastTrameElapsesTime))


        if (not lastTrameIsSame or (lastTrameIsSame and lastTrameElapsesTime >= 15.0)) :
            print("On envoie")                
            try:
                #TODO Envoyer la trame ici
                os.system("sudo /home/pi/scripts/poele/emetteur/emetteurMCZBis 0 " + trame._message)
                #mczEmitterService.sendMessage(trame._message)
                if startStove : 
                    databaseService.setStoveActive(True)
                else :
                    databaseService.setStoveActive(False)
                mczProtocolService.saveTrame(trame)        
            except Exception as e:
                # TODO ajouter log en base
                raise
            finally:
                None
        else :
            print("Même trame, délai insuffisant :" + str(lastTrameElapsesTime))
        


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
    
    
    """ Current Mode"""    
    currentMode = databaseService.findCurrentMode()

    onPeriode = currentMode  != None
    if onPeriode : 
        print("Mode            : " + currentMode._libelle)
        print("Consigne        : " + str(currentMode._cons) + "°C")
        print("Max             : " + str(currentMode._max) + "°C")

    """ Poele state"""
    onPoele = databaseService.getPoeleActive()
    print("\nPoêle actif     : " + str(onPoele))
    
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
    currentTemp =19.0; #TODO Récupérer la température
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
        if onPoele :
            databaseService.setForcedOn(False)
            onForced = False
        elif tempZone1 or tempZone3 :
            databaseService.setForcedOn(False)
            onForced = False
    
     
    debug_start = False
    debug_shutdown = False
    
    
    niveauPuissance = enumeration.NiveauPuissance.niveau1
    niveauVentilation = enumeration.NiveauVentilation.auto
    trameMode = enumeration.Mode.automatique
    trameEtat = enumeration.Etat.off
    trameActionneur = enumeration.Actionneur.systeme
    
          
    """ Start / Continue cases"""
    if onPeriode:
        if not onForced and not offForced and tempZone1:
            # TODO Envoyer On
            niveauPuissance = mczProtocolService.getNiveauPuissance(currentTemp, currentMode._cons);
            trameEtat = enumeration.Etat.on
            debug_start = True
        elif not onForced and not offForced and tempZone2 and onPoele :
            # TODO Envoyer On
            niveauPuissance = mczProtocolService.getNiveauPuissance(currentTemp, currentMode._cons);
            trameEtat = enumeration.Etat.on
            debug_start = True
        elif not onPoele and onForced and tempZone2 :
            # TODO Envoyer On
            niveauPuissance = mczProtocolService.getNiveauPuissance(currentTemp, currentMode._cons);
            trameEtat = enumeration.Etat.on
            debug_start = True
    elif onForced :
        if tempForcedZone1 :
            # TODO Envoyer On
            niveauPuissance = mczProtocolService.getNiveauPuissance(currentTemp, forcedMode._cons);
            trameEtat = enumeration.Etat.on
            debug_start = True
        elif tempForcedZone2 :
            # TODO Envoyer On
            niveauPuissance = mczProtocolService.getNiveauPuissance(currentTemp, forcedMode._cons);
            trameEtat = enumeration.Etat.on
            debug_start = True
    
    
    """ Stop cases """    
    if onPoele :
        if not onPeriode and not onForced and not offForced :
            # TODO Envoyer Off
            lastTrame = mczProtocolService.getLastTrame()
            if lastTrame != None :
                niveauPuissance = lastTrame._puissance
                niveauVentilation = lastTrame._ventilation                        
            trameEtat = enumeration.Etat.off
            debug_shutdown = True
        elif onPeriode and not onForced and offForced :
            # TODO Envoyer Off
            lastTrame = mczProtocolService.getLastTrame()
            if lastTrame != None :
                niveauPuissance = lastTrame._puissance
                niveauVentilation = lastTrame._ventilation                        
            trameEtat = enumeration.Etat.off
            trameEtat = enumeration.Etat.off
            debug_shutdown = True
        elif onPeriode and not onForced and not offForced and tempZone3 :
            # TODO Envoyer Off
            lastTrame = mczProtocolService.getLastTrame()
            if lastTrame != None :
                niveauPuissance = lastTrame._puissance
                niveauVentilation = lastTrame._ventilation                        
            trameEtat = enumeration.Etat.off
            trameEtat = enumeration.Etat.off
            debug_shutdown = True
        elif not onPeriode and onForced and not offForced and tempForcedZone3 :
            # TODO Envoyer Off
            lastTrame = mczProtocolService.getLastTrame()
            if lastTrame != None :
                niveauPuissance = lastTrame._puissance
                niveauVentilation = lastTrame._ventilation                        
            trameEtat = enumeration.Etat.off
            trameEtat = enumeration.Etat.off
            debug_shutdown = True
        

    print("\ndebug_start     : " + str(debug_start))
    print("debug_shutdown  : " + str(debug_shutdown))
    
   
   
    if debug_start or debug_shutdown :
        print("\nEnvoi trame")
        print("Etat            : " + trameEtat.name)
        print("Mode            : " + trameMode.name)
        print("Actionneur      : " + trameActionneur.name)
        print("Puissance       : " + niveauPuissance.name)
        print("Ventilation     : " + niveauVentilation.name)
        
        trame = mczProtocolService.getTrame(trameMode, trameEtat, trameActionneur, niveauPuissance, niveauVentilation)
        print("Trame message   : " + utils.binaryStringToHex(trame._message))
                   
        try:
            #TODO Envoyer la trame ici
            if debug_start : 
                databaseService.setPoeleActive(True)
            elif debug_shutdown :
                databaseService.setPoeleActive(False)
            mczProtocolService.saveTrame(trame)        
        except Exception as e:
            # TODO ajouter log en base
            None
        finally:
            None
        
        

    
    
    
    

        
    
    
    
    
# -*- coding: utf-8 -*-
'''
Created on 22 mai 2014

@author: nestof
'''

from datetime import datetime
import logging
from os.path import os


from com.nestof.domocore import  enumeration


class MCZService(object):
    '''
    classdocs
    '''


    def __init__(self, databaseService, tempService, mczProtocolService, config):
        '''
        Constructor
        '''
        self._logger = logging.getLogger(__name__)
        """ Services """    
        self._databaseService = databaseService
        self._tempService = tempService
        self._config = config
        self._mczProtocolService = mczProtocolService

        
    def launchAuto(self):
        self._logger.debug("---------- Launching Auto Mode ----------")        
        
        """ Mode en cours """
        currentPeriode = self._databaseService.findCurrentPeriode()        
        currentPeriodDefined = currentPeriode != None
        previousPeriode =  self._databaseService.findPreviousPeriode(currentPeriode)
        nextPeriode = self._databaseService.findNextPeriode(currentPeriode)
    
        """ Id du dernier mode """
        lastModeId = self._databaseService.getLastModeId()   
    
        """ Etat de fonctionnement du poêle """
        stoveIsOn = self._databaseService.isStoveActive()    
        
        """ Indicateurs de forçage """ 
        onForced = self._databaseService.isForcedOn()
        offForced = self._databaseService.isForcedOff()
        
        """ Mode forcé """
        forcedMode = self._databaseService.findForcedMode()
        
        """ Température courante """    
        currentTemp = self._tempService.readTemp();
        
        """ Zones de températures du mode en cours """
        if currentPeriodDefined :        
            tempZone1 = currentTemp < currentPeriode._mode._cons
            tempZone3 = currentTemp >= currentPeriode._mode._max
            tempZone2 = not tempZone1 and not tempZone3
        
        """ Zones de températures du mode forcé """
        tempForcedZone1 = currentTemp < forcedMode._cons
        tempForcedZone3 = currentTemp >= forcedMode._max
        tempForcedZone2 = not tempForcedZone1 and not tempForcedZone3      
        
        """ ------- DEBUG ------ """
        if currentPeriodDefined :
            self._logger.debug("  Mode en cours   : " + currentPeriode._mode._libelle)
            self._logger.debug("  Consigne        : " + str(currentPeriode._mode._cons) + "°C")
            self._logger.debug("  Max             : " + str(currentPeriode._mode._max) + "°C")
        self._logger.debug("  Dernier mode    : " + str(lastModeId))
        self._logger.debug("  Poêle actif     : " + str(stoveIsOn))
        self._logger.debug("  Marche forcée   : " + str(onForced))
        self._logger.debug("  Arrêt forcé     : " + str(offForced))
        self._logger.debug("  Température     : " + str(currentTemp) + "°C")
        """ ------- DEBUG ------ """
     
        """ Initialisation des paramètres de la trame """
        """ Niveau de chauffe """    
        niveauPuissance = enumeration.NiveauPuissance.niveau1
        """ Niveau de ventilation """
        niveauVentilation = enumeration.NiveauVentilation.auto
        """ Mode de fonctionnement """
        trameMode = enumeration.Mode.automatique
        """ Etat """
        trameEtat = enumeration.Etat.off
        """ Actionneur """
        trameActionneur = enumeration.Actionneur.systeme        
     
        """ Detection de l'actionneur """
        if onForced and not offForced and not stoveIsOn :
            trameActionneur = enumeration.Actionneur.utilisateur
        if offForced and not onForced and stoveIsOn:
            trameActionneur = enumeration.Actionneur.utilisateur
     
        
        """RAZ des indicateurs de forçage"""
        if (onForced and offForced) :
            """ Les 2 indicateurs sont actifs => RAZ des indicateurs """
            self._databaseService.setForcedOff(False)
            self._databaseService.setForcedOn(False)
            onForced = False
            offForced = False
        elif lastModeId != None and currentPeriodDefined and str(currentPeriode._mode._id) != str(lastModeId) :
            """ On change de mode => RAZ des indicateurs """
            self._databaseService.setForcedOff(False)
            self._databaseService.setForcedOn(False)
            onForced = False
            offForced = False
        elif (offForced and not currentPeriodDefined):
            """ On est en arrêt forcé et aucun mode n'est défini => RAZ indicateur arrêt forcé """
            self._databaseService.setForcedOff(False)
            offForced = False
        elif (onForced and currentPeriodDefined):
            """ On est en marche forcée et un mode est défini """
            if stoveIsOn :
                """ Le poêle est allumé => RAZ indicateur marche forcée """
                self._databaseService.setForcedOn(False)
                onForced = False
            elif tempZone1 or tempZone3 :            
                """ Le poêle est éteint et on est dans les zones de température 1 ou 3 => RAZ indicateur marche forcée """
                self._databaseService.setForcedOn(False)
                onForced = False
        
        """ Mise à jour dernier mode """
        if currentPeriodDefined:
            self._databaseService.setLastModeId(currentPeriode._mode._id)
        else:
            None
            """@TODO self._databaseService.setLastModeId(None)"""
                      
        """ Allumage / Arrêt du poêle """
        """ Allumage du poêle ou maintient allumé """ 
        startStove = False
        """ Arrêt du poêle ou maintient éteint """
        shutdownStove = False
        
        """ Calcul du nombre de minutes depuis le début de la période """
        minutesFromStartPeriode = None
        if currentPeriodDefined and currentPeriode._startDatetime != None:
            if previousPeriode != None  and currentPeriode._mode._id == previousPeriode._mode._id: 
                minutesFromStartPeriode = datetime.now() - previousPeriode._startDatetime 
            else:
                minutesFromStartPeriode = datetime.now() - currentPeriode._startDatetime
            minutesFromStartPeriode = (minutesFromStartPeriode.seconds) / 60
        
        """ Test si on peut activer le boost au démarrage """
        boostDuration = self._databaseService.getEmitterBoostDuration()
        
        boostActive = False 
        if (minutesFromStartPeriode <= float(boostDuration)):
            boostActive = True
        
        """ Calcul du nombre de minutes avant la fin de la période """
        minutesToEndPeriode = None
        if currentPeriodDefined and currentPeriode._endDatetime != None:
            if nextPeriode != None  and currentPeriode._mode._id == nextPeriode._mode._id: 
                minutesToEndPeriode = nextPeriode._endDatetime - datetime.now()
            else:
                minutesToEndPeriode = currentPeriode._endDatetime - datetime.now()
            minutesToEndPeriode = (minutesToEndPeriode.seconds) / 60
        
        """ Limite de marche en fin de période atteinte """
        endPeriodPowerOnLimit = minutesToEndPeriode != None and minutesToEndPeriode < float(self._databaseService.getEmitterStartLimitBeforeEndPeriod())
        
        """ Si la consigne de la péiode suivante est supérieure à la consigne de la periode courante """
        if endPeriodPowerOnLimit == True and nextPeriode != None and nextPeriode._mode._cons >= currentPeriode._mode._cons:
            endPeriodPowerOnLimit = False
                
        if currentPeriodDefined:
            """ Un mode est défini """
            if (not stoveIsOn and  endPeriodPowerOnLimit):
                """ Le poêle est arrété et la période se termine dans moins de XX minutes """
                """ => On n'allume pas le poêle """
                None
            elif (stoveIsOn and tempZone2 and  endPeriodPowerOnLimit):
                """ Le poêle est en marche et la période se termine dans moins de XX minutes et en zone de température 2 """
                """ => On ne maintient pas l'allumage """
                None       
            elif ((not onForced and not offForced and tempZone1) or \
                    (not onForced and not offForced and tempZone2 and stoveIsOn) or \
                    (not stoveIsOn and onForced and tempZone2)):
                """ Pas d'indicateurs de forçage de définis et en zone de température 1 """
                """ OU Pas d'indicateurs de forçade de définis et en zone de température 2 et poêle déjà en marche """
                """ OU Indicateur de marche forcée défini et en zone de température 2 et poêle en arrêt """
                """ => On allume ou on maintient allumé """
                niveauPuissance = self._mczProtocolService.getNiveauPuissance(currentTemp, currentPeriode._mode._cons, boostActive);
                startStove = True
        elif onForced and (tempForcedZone1 or tempForcedZone2) :
            """ Pas de mode de défini """
            """ ET indicateur de marche forcée défini et en zones de température 1 ou 2 """
            if tempForcedZone1 :
                niveauPuissance = self._mczProtocolService.getNiveauPuissance(currentTemp, forcedMode._cons, boostActive);
            """ => On allume ou on maintient allumé """
            startStove = True
                
        if not startStove:
            """ On ne demande pas d'allumage ou de maintient allumé du poêle """  
            if stoveIsOn :
                """ Poêle allumé """
                if (not currentPeriodDefined and not onForced and not offForced) or \
                        (not currentPeriodDefined and onForced and not offForced and tempForcedZone3) or \
                        (currentPeriodDefined and not onForced and not offForced and tempZone3) or \
                        (currentPeriodDefined and not onForced and offForced) or \
                        (currentPeriodDefined and tempZone2 and  endPeriodPowerOnLimit) :
                    """ Pas de mode défini et pas d'indicateur de forçage """
                    """ OU Pas de mode défini et indicateur de marche forcée et zone de température 3 """
                    """ OU Mode défini et pas d'indicateur de forçage et zone de température 3 """
                    """ OU Mode défini et indicateur d'arrêt forcé défini """
                    """ OU La période se termine dans moins de XX minutes et en zone de température 2 """
                    """ => On éteint """
                    shutdownStove = True
            else :
                """ Poêle éteint """
                """ => On maintient l'extinction """
                shutdownStove = True 
        
        """ Mise à jour des paramètres de la trame """
        if startStove:
            trameEtat = enumeration.Etat.on
#             if onForced and not stoveIsOn :
#                 trameActionneur = enumeration.Actionneur.utilisateur    
        elif shutdownStove :
            trameEtat = enumeration.Etat.off
            lastTrame = self._mczProtocolService.getLastTrame()
            if lastTrame != None :
                niveauPuissance = lastTrame._puissance
                niveauVentilation = lastTrame._ventilation
#             if offForced and stoveIsOn:
#                 trameActionneur = enumeration.Actionneur.utilisateur

    
        self._logger.debug("  Allumage        : " + str(startStove))
        self._logger.debug("  Extinction      : " + str(shutdownStove))

        """ On construit la trame et on l'envoi """       
        if startStove or shutdownStove :
            if (trameActionneur != enumeration.Actionneur.utilisateur or \
                trameActionneur == enumeration.Actionneur.utilisateur and self._databaseService.isCheckDelays()):
                checkDelays = True
            else:
                checkDelays = False           
            self.constructAndSendTrame(startStove, shutdownStove, trameEtat, trameMode, trameActionneur, niveauPuissance, niveauVentilation, checkDelays)
        
    def launchManu(self):
        self._logger.debug("---------- Launching Manu Mode ----------")
        
        """ Ordre manuel """
        manualOrder = self._databaseService.getOrdreManu()
        
        """ Etat de fonctionnement du poêle """
        stoveIsOn = self._databaseService.isStoveActive()
        
        " Température courante """    
        currentTemp = self._tempService.readTemp()
        
        """ Mode manuel """
        manualMode = self._databaseService.findManualMode()
        
        """ Zones de températures """
        tempManualZone1 = currentTemp < manualMode._cons
        tempManualZone3 = currentTemp >= manualMode._max
        tempManualZone2 = not tempManualZone1 and not tempManualZone3
        
        """ ------- DEBUG ------ """
        self._logger.debug("  Consigne        : " + str(manualMode._cons) + "°C")
        self._logger.debug("  Max             : " + str(manualMode._max) + "°C")
        self._logger.debug("  Poêle actif     : " + str(stoveIsOn))
        self._logger.debug("  Ordre manuel    : " + str(manualOrder.value))
        self._logger.debug("  Température     : " + str(currentTemp) + "°C")
        """ ------- DEBUG ------ """

        """ Initialisation des paramètres de la trame """
        """ Niveau de chauffe """    
        niveauPuissance = enumeration.NiveauPuissance.niveau1
        """ Niveau de ventilation """
        niveauVentilation = enumeration.NiveauVentilation.auto
        """ Mode de fonctionnement """
        trameMode = enumeration.Mode.automatique
        """ Etat  """
        trameEtat = enumeration.Etat.off
        """ Actionneur """
        trameActionneur = enumeration.Actionneur.systeme
        
        """ Allumage / Arrêt du poêle """
        """ Allumage du poêle ou maintient allumé """ 
        startStove = False
        """ Arrêt du poêle ou maintient éteint """
        shutdownStove = False
        """if manualOrder == enumeration.OrdreManuel.marche and (tempManualZone1 or (stoveIsOn and tempManualZone2)):"""
        if manualOrder == enumeration.OrdreManuel.marche and (tempManualZone1 or tempManualZone2):
            """ Ordre d'allumage et zones de température 1 ou 2 """
            startStove = True
            niveauPuissance = self._mczProtocolService.getNiveauPuissance(currentTemp, manualMode._cons, True);            
            trameEtat = enumeration.Etat.on
            if not stoveIsOn :
                trameActionneur = enumeration.Actionneur.utilisateur
        
        """Stop cases"""
        if manualOrder == enumeration.OrdreManuel.arret or (not startStove):
            """ Ordre d'extinction du poêle OU pas d'ordre d'allumage"""
            shutdownStove = True
            trameEtat = enumeration.Etat.off
            lastTrame = self._mczProtocolService.getLastTrame()
            if lastTrame != None :
                niveauPuissance = lastTrame._puissance
                niveauVentilation = lastTrame._ventilation
            if stoveIsOn and not tempManualZone3:
                trameActionneur = enumeration.Actionneur.utilisateur
            
        self._logger.debug("  Allumage        : " + str(startStove))
        self._logger.debug("  Extinction      : " + str(shutdownStove))
        
        """ On construit la trame et on l'envoi """              
        if startStove or shutdownStove :
            if (trameActionneur != enumeration.Actionneur.utilisateur or \
                trameActionneur == enumeration.Actionneur.utilisateur and self._databaseService.isCheckDelays()):
                check = True
            else:
                check = False
            self.constructAndSendTrame(startStove, shutdownStove, trameEtat, trameMode, trameActionneur, niveauPuissance, niveauVentilation, check)
                    
        self._databaseService.saveOrdreManu(self._databaseService.isStoveActive())

        
    def launchStop(self):
        self._logger.debug("---------- Launching Stop Mode ----------")

        niveauPuissance = enumeration.NiveauPuissance.niveau1
        niveauVentilation = enumeration.NiveauVentilation.auto
        trameMode = enumeration.Mode.automatique
        trameEtat = enumeration.Etat.off
        trameActionneur = enumeration.Actionneur.systeme
        
        
        """Is stove On """
        stoveIsOn = self._databaseService.isStoveActive()
        if stoveIsOn :
            trameActionneur = enumeration.Actionneur.utilisateur
            
        lastTrame = self._mczProtocolService.getLastTrame()
        if lastTrame != None :
            niveauPuissance = lastTrame._puissance
            niveauVentilation = lastTrame._ventilation
        
        """ On construit la trame et on l'envoi """        
        self.constructAndSendTrame(False, True, trameEtat, trameMode, trameActionneur, niveauPuissance, niveauVentilation, True)

        
    def constructAndSendTrame(self, startStove, shutdownStove, trameEtat, trameMode, trameActionneur, niveauPuissance, niveauVentilation, checkDelays):
        self._logger.debug("  ** Construction de la trame **")
        self._logger.debug("  Etat            : " + trameEtat.name)
        self._logger.debug("  Mode            : " + trameMode.name)
        self._logger.debug("  Actionneur      : " + trameActionneur.name)
        self._logger.debug("  Puissance       : " + niveauPuissance.name)
        self._logger.debug("  Ventilation     : " + niveauVentilation.name)        
        self._logger.debug("  Contrôles       : " + str(checkDelays))        
        
        if (checkDelays) :        
            """ Durée écoulée depuis dernière extinction """
            lastPowerOffElapsedTime = self._mczProtocolService.getLastPowerOffElapsedTime()
    
            """ Contrôle sur la durée maxi des envois d'ordre d'extinction """
            emitterStopTrameSendDuration = self._databaseService.getEmitterStopTrameSendDuration()
            
            if (shutdownStove and lastPowerOffElapsedTime != None and lastPowerOffElapsedTime > float(emitterStopTrameSendDuration)):            
                self._logger.debug("  Durée depuis dernière extinction : " + str(lastPowerOffElapsedTime) + " minutes")
                self._logger.debug("  Durée des envois d'ordre d'extinction : " + str(emitterStopTrameSendDuration) + " minutes")
                self._logger.debug("  On n'envoie pas")
                return
            
            """ Contrôle sur le délai minimal entre 2 cycles extinction/allumage """
            emitterOffMinDuration = self._databaseService.getEmitterOffMinDuration()       
            if (startStove and lastPowerOffElapsedTime != None and lastPowerOffElapsedTime < float(emitterOffMinDuration)): 
                self._logger.debug("  Durée depuis dernière extinction : " + str(lastPowerOffElapsedTime) + " minutes")
                self._logger.debug("  Délai d'allumage après extinction : " + str(emitterOffMinDuration) + " minutes")
                self._logger.debug("  On n'envoie pas")
                return
           
            """ Contrôle sur l'envoi de trame identiques """     
            lastTrameIsSame = self._mczProtocolService.isTrameSameAsLastTrame(trameMode, trameEtat, niveauPuissance, niveauVentilation)
            lastTrameElapsesTime = self._mczProtocolService.getLastTrameElapsedTime()
            emitterSameStartTrameDelay = self._databaseService.getEmitterSameStartTrameDelay()
            emitterSameStopTrameDelay = self._databaseService.getEmitterSameStopTrameDelay()
            
            if(lastTrameIsSame and ((startStove and lastTrameElapsesTime < float(emitterSameStartTrameDelay)) \
                                     or (shutdownStove and lastTrameElapsesTime < float(emitterSameStopTrameDelay)))):
                self._logger.debug("  Dernière trame identique ")
                self._logger.debug("  Durée depuis dernier envoi : " + str(lastTrameElapsesTime) + " minutes")
                if (startStove):
                    self._logger.debug("  Délai entre 2 trames On    : " + str(emitterSameStartTrameDelay) + " minutes")
                if (shutdownStove):
                    self._logger.debug("  Délai entre 2 trames Off   : " + str(emitterSameStopTrameDelay) + " minutes")
                self._logger.debug("  On n'envoie pas")
                return
       
        self._logger.debug("  On envoie")                
        try:
            """Construction de la trame """
            trame = self._mczProtocolService.getTrame(trameMode, trameEtat, trameActionneur, niveauPuissance, niveauVentilation)

            """Envoi de la trame"""
            os.system(self._config.get('EMITTER', 'emitter.command') + " " + trame._message)
                
            """ Sauvegarde de l'état du poêle """    
            self._databaseService.setStoveActive(startStove)
            
            """ Sauvegarde de la trame """
            self._mczProtocolService.saveTrame(trame)        
        except Exception as e:
            self._logger.error("  Trame non envoyée", e)
            raise
        finally:
            self._logger.debug("  Trame envoyée")
     

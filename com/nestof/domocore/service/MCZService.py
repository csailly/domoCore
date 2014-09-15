# -*- coding: utf-8 -*-
'''
Created on 22 mai 2014

@author: nestof
'''

import logging
from os.path import os
import subprocess

from com.nestof.domocore import enumeration

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
        
        """ Current Mode"""    
        currentMode = self._databaseService.findCurrentMode()
    
        onPeriode = currentMode != None
    
        """ Last mode id """
        lastModeId = self._databaseService.getLastModeId()   
    
        """ Stove state"""
        stoveIsOn = self._databaseService.getStoveActive()    
        
        """ Forced flags""" 
        onForced = self._databaseService.getForcedOn()
        offForced = self._databaseService.getForcedOff()
        
        """ Forced mode """
        forcedMode = self._databaseService.findForcedMode()
        
        """ The current temp """    
        currentTemp = self._tempService.readTemp();
        
        """ current mode temp zones"""
        if onPeriode :        
            tempZone1 = currentTemp < currentMode._cons
            tempZone3 = currentTemp >= currentMode._max
            tempZone2 = not tempZone1 and not tempZone3
        
        """ forced mode temp zones"""
        tempForcedZone1 = currentTemp < forcedMode._cons
        tempForcedZone3 = currentTemp >= forcedMode._max
        tempForcedZone2 = not tempForcedZone1 and not tempForcedZone3
        
        """ initialization """ 
        startStove = False
        shutdownStove = False
            
        niveauPuissance = enumeration.NiveauPuissance.niveau1
        niveauVentilation = enumeration.NiveauVentilation.auto
        trameMode = enumeration.Mode.automatique
        trameEtat = enumeration.Etat.off
        trameActionneur = enumeration.Actionneur.systeme
        
        
        """ ------- DEBUG ------ """
        if onPeriode :
            self._logger.debug("  Mode en cours   : " + currentMode._libelle)
            self._logger.debug("  Consigne        : " + str(currentMode._cons) + "°C")
            self._logger.debug("  Max             : " + str(currentMode._max) + "°C")
        self._logger.debug("  Dernier mode    : " + str(lastModeId))
        self._logger.debug("  Poêle actif     : " + str(stoveIsOn))
        self._logger.debug("  Marche forcée   : " + str(onForced))
        self._logger.debug("  Arrêt forcé     : " + str(offForced))
        self._logger.debug("  Température     : " + str(currentTemp) + "°C")
        """ ------- DEBUG ------ """
        
        """RAZ forced flags"""
        if (onForced and offForced) :
            self._databaseService.setForcedOff(False)
            self._databaseService.setForcedOn(False)
            onForced = False
            offForced = False
        elif lastModeId != None and currentMode != None and str(currentMode._id) != str(lastModeId) :
            """ On change de mode => RAZ des flags """
            self._databaseService.setForcedOff(False)
            self._databaseService.setForcedOn(False)
            onForced = False
            offForced = False
        elif (offForced and not onPeriode):
            """ On est en arrêt forcé et en période d'arrêt => RAZ flag arrêt forcé """
            self._databaseService.setForcedOff(False)
            offForced = False
            None
        elif (onForced and onPeriode):
            """ On est en marche forcée et en période de fonctionnement """
            if stoveIsOn :
                """ Le poêle est allumé => RAZ flag marche forcée """
                self._databaseService.setForcedOn(False)
                onForced = False
            elif tempZone1 or tempZone3 :
                """ Le poêle est éteint est on est dans les zones de température 1 ou 3 => RAZ flag marche forcée """
                self._databaseService.setForcedOn(False)
                onForced = False
        """Mise à jour dernier mode"""
        self._databaseService.setLastModeId(currentMode._id)
        
                      
        """ Start / Continue cases"""
        if onPeriode:
            if (not onForced and not offForced and tempZone1) or \
                    (not onForced and not offForced and tempZone2 and stoveIsOn) or \
                    (not stoveIsOn and onForced and tempZone2):
                niveauPuissance = self._mczProtocolService.getNiveauPuissance(currentTemp, currentMode._cons);
                startStove = True
        elif onForced and (tempForcedZone1 or tempForcedZone2) :
            if tempForcedZone1 :
                niveauPuissance = self._mczProtocolService.getNiveauPuissance(currentTemp, forcedMode._cons);
                startStove = True
        
        if startStove:
            trameEtat = enumeration.Etat.on
            if onForced and not stoveIsOn :
                trameActionneur = enumeration.Actionneur.utilisateur
        else : 
            """ Stop cases """    
            if stoveIsOn :
                if (not onPeriode and not onForced and not offForced) or \
                        (onPeriode and not onForced and offForced) or \
                        (onPeriode and not onForced and not offForced and tempZone3) or \
                        (not onPeriode and onForced and not offForced and tempForcedZone3) :
                    shutdownStove = True
            else :
                shutdownStove = True 
            
        if shutdownStove :
            trameEtat = enumeration.Etat.off
            lastTrame = self._mczProtocolService.getLastTrame()
            if lastTrame != None :
                niveauPuissance = lastTrame._puissance
                niveauVentilation = lastTrame._ventilation
            if offForced and stoveIsOn:
                trameActionneur = enumeration.Actionneur.utilisateur

    
        self._logger.debug("  startStove      : " + str(startStove))
        self._logger.debug("  shutdownStove   : " + str(shutdownStove))
        
       
       
        if startStove or shutdownStove :
            self.constructAndSendTrame(startStove, shutdownStove, trameEtat, trameMode, trameActionneur, niveauPuissance, niveauVentilation)
        
    def launchManu(self):
        self._logger.debug("---------- Launching Manu Mode ----------")
        
        """ initialization """ 
        startStove = False
        shutdownStove = False
            
        niveauPuissance = enumeration.NiveauPuissance.niveau1
        niveauVentilation = enumeration.NiveauVentilation.auto
        trameMode = enumeration.Mode.automatique
        trameEtat = enumeration.Etat.off
        trameActionneur = enumeration.Actionneur.systeme
        
        """Manual Order"""
        manualOrder = self._databaseService.getOrdreManu()
        
        """Is stove On """
        stoveIsOn = self._databaseService.getStoveActive()
        
        """ The current temperature """    
        currentTemp = self._tempService.readTemp()
        
        """ Parametered temperatures """
        manualMode = self._databaseService.findManualMode()
        
        """ Manual mode temperature zones"""
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
        
        
        """Start/ Continue cases """
        if manualOrder == enumeration.OrdreManuel.marche and tempManualZone1 or (stoveIsOn and tempManualZone2):
            niveauPuissance = self._mczProtocolService.getNiveauPuissance(currentTemp, manualMode._cons);
            startStove = True
            trameEtat = enumeration.Etat.on
            if not stoveIsOn :
                trameActionneur = enumeration.Actionneur.utilisateur


        
        """Stop cases"""
        if manualOrder == enumeration.OrdreManuel.arret or (not startStove):
            shutdownStove = True
            trameEtat = enumeration.Etat.off
            lastTrame = self._mczProtocolService.getLastTrame()
            if lastTrame != None :
                niveauPuissance = lastTrame._puissance
                niveauVentilation = lastTrame._ventilation
            if stoveIsOn and not tempManualZone3:
                trameActionneur = enumeration.Actionneur.utilisateur
            
        self._logger.debug("  startStove      : " + str(startStove))
        self._logger.debug("  shutdownStove   : " + str(shutdownStove))
                      
        if startStove or shutdownStove :
            self.constructAndSendTrame(startStove, shutdownStove, trameEtat, trameMode, trameActionneur, niveauPuissance, niveauVentilation)

            
        
    def launchStop(self):
        self._logger.debug("---------- Launching Stop Mode ----------")
        """Envoyer odre Off"""
        None
        
    def constructAndSendTrame(self, startStove, shutdownStove, trameEtat, trameMode, trameActionneur, niveauPuissance, niveauVentilation):
        self._logger.debug("  **Construction trame**")
        self._logger.debug("  Etat            : " + trameEtat.name)
        self._logger.debug("  Mode            : " + trameMode.name)
        self._logger.debug("  Actionneur      : " + trameActionneur.name)
        self._logger.debug("  Puissance       : " + niveauPuissance.name)
        self._logger.debug("  Ventilation     : " + niveauVentilation.name)
            
        trame = self._mczProtocolService.getTrame(trameMode, trameEtat, trameActionneur, niveauPuissance, niveauVentilation)
            
        lastTrameIsSame = self._mczProtocolService.isTrameSameAsLastTrame(trame)
        lastTrameElapsesTime = self._mczProtocolService.getLastTrameElapsedTime()
            
        self._logger.debug("  Dernière trame identique : " + str(lastTrameIsSame))
        self._logger.debug("  Durée depuis dernier envoi : " + str(lastTrameElapsesTime))
    
        lastPowerOffElapsedTime = self._mczProtocolService.getLastPowerOffElapsedTime()
            
        if (shutdownStove and lastPowerOffElapsedTime != None and lastPowerOffElapsedTime > float(self._config.get('EMITTER', 'emitter.stopOrder.max.duration'))):            
            self._logger.debug("  Durée depuis dernière extinction : " + str(lastPowerOffElapsedTime))
            self._logger.debug("  Durée des envois d'ordre d'extinction : " + self._config.get('EMITTER', 'emitter.stopOrder.max.duration'))
            self._logger.debug("  On n'envoie pas")
            return
        
        if (startStove and lastPowerOffElapsedTime != None and lastPowerOffElapsedTime < float(self._config.get('EMITTER', 'emitter.powerOff.min.duration'))): 
            self._logger.debug("  Durée depuis dernière extinction : " + str(lastPowerOffElapsedTime))
            self._logger.debug("  Délai d'allumage après extinction : " + self._config.get('EMITTER', 'emitter.powerOff.min.duration'))
            self._logger.debug("  On n'envoie pas")
            return
            
        if (not lastTrameIsSame or (lastTrameIsSame and ((startStove and lastTrameElapsesTime >= float(self._config.get('EMITTER', 'emitter.same.trame.start.delay'))) or (shutdownStove and lastTrameElapsesTime >= float(self._config.get('EMITTER', 'emitter.same.trame.stop.delay')))))) :
            """ Ici trame différente de la précédente ou Trame de mise en marche avec un délai >= 15 min ou Trame de mise en arrêt avec un délai >= 5 min  """
            self._logger.debug("  On envoie")                
            try:
                """Envoi de la trame"""
                os.system(self._config.get('EMITTER', 'emitter.command') + " " + trame._message)
                
                # proc = subprocess.Popen([self._config['EMITTER']['emitter.command'], trame._message], stdout=subprocess.PIPE, shell=True)
                # (out, err) = proc.communicate()
                # print("program output:" + str(err))
                
                
                if startStove : 
                    self._databaseService.setStoveActive(True)
                else :
                    self._databaseService.setStoveActive(False)
                self._mczProtocolService.saveTrame(trame)        
            except Exception as e:
                raise
            finally:
                None
        else :
            self._logger.debug("  Même trame, délai insuffisant :" + str(lastTrameElapsesTime))      

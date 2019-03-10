# -*- coding: utf-8 -*-
'''
Created on 10 avr. 2014

@author: S0087931
'''



from com.nestof.domocore import utils

class Enum(object):
    def __init__(self, name, value):
        '''
        Constructor
        '''
        self.name = name
        self.value = value
        
    def getBinValue(self):
        return utils.intToBin3(self.value)

"""Mode de régulation du poêle, Automatique ou Manuel"""
class Mode(object):
    automatique = Enum("automatique", 0)
    manuel = Enum("manuel", 1)
    
    def __init__(self):
        '''
        Constructor
        '''
        
    def getEnum(self, value):
        if value == 0 :
            return self.automatique
        if value == 1 :
            return self.manuel
        return None

"""Etat"""
class Etat(object):
    on = Enum("on", 1)
    off = Enum("off", 0)
    
    def __init__(self):
        '''
        Constructor
        '''

    def getEnum(self, value):
        if value == 0 :
            return self.off
        if value == 1 :
            return self.on
        return None

"""Ordre à envoyer au poêle, On en mode automatique, On en mode manuel, Off"""
class Ordre(object):
    onAuto = Enum("onAuto", 0b100)
    onManuel = Enum("onManuel", 0b010)
    off = Enum("off", 0b000)
    
    def __init__(self):
        '''
        Constructor
        '''
        
    def getEnum(self, value):
        if value == 0b100 :
            return self.onAuto
        if value == 0b010 :
            return self.onManuel
        if value == 0b000 :
            return self.off
        return None
    

    
"""Niveau de puissance de chauffe"""
class NiveauPuissance(object):
    niveau1 = Enum("niveau1", 1)
    niveau2 = Enum("niveau2", 2)
    niveau3 = Enum("niveau3", 3)
    niveau4 = Enum("niveau4", 4)
    niveau5 = Enum("niveau5", 5)
    
    def __init__(self):
        '''
        Constructor
        '''
        
    def getEnum(self, value):
        if value == 1 :
            return self.niveau1
        if value == 2 :
            return self.niveau2
        if value == 3 :
            return self.niveau3
        if value == 4 :
            return self.niveau3
        if value == 5 :
            return self.niveau5
        return None

    
"""Niveau de ventilation"""
class NiveauVentilation(object):
    niveau1 = Enum("niveau1", 1)
    niveau2 = Enum("niveau2", 2)
    niveau3 = Enum("niveau3", 3)
    niveau4 = Enum("niveau4", 4)
    niveau5 = Enum("niveau5", 5)
    auto = Enum("auto", 6)
    
    def __init__(self):
        '''
        Constructor
        '''
    def getEnum(self, value):
        if value == 1 :
            return self.niveau1
        if value == 2 :
            return self.niveau2
        if value == 3 :
            return self.niveau3
        if value == 4 :
            return self.niveau3
        if value == 5 :
            return self.niveau5
        if value == 6 :
            return self.auto
        return None

    
"""Actionneur qui envoie l'ordre"""
class Actionneur(object):
    systeme = Enum("systeme", 1)
    utilisateur = Enum("utilisateur", 2)
    
    def __init__(self):
        '''
        Constructor
        '''
    
    def getEnum(self, value):
        if value == 1 :
            return self.systeme
        if value == 2 :
            return self.utilisateur
        return None

"""Configuration du poêle, Automatique, Manuel, Arrêt"""
class ConfigurationPeole(object):
    automatique = Enum("Automatique", "AUTO")
    manuel = Enum("Manuel", "MANU")
    arret = Enum("Arrêt", "STOP")
    
    def getEnum(self, value):
        if value == "AUTO" :
            return self.automatique
        if value == "MANU" :
            return self.manuel
        if value == "STOP" :
            return self.arret
        return None
    

def getOrdre(mode, etat):
    """Return an Ordre from Mode and Etat"""
    if not isinstance(mode, Enum) :
        raise Exception('mode is not an instance of Mode')
    
    if not isinstance(etat, Enum) :
        raise Exception('etat is not an instance of Etat')
    
    if etat == Etat.off :
        return Ordre.off
        
    if mode == Mode.automatique :
        return Ordre.onAuto
    
    return Ordre.onManuel

class OrdreManuel(object):
    marche = Enum("Marche", "ON")
    arret = Enum("Arrêt", "OFF")
    
    def getEnum(self, value):
        if value == "ON" :
            return self.marche
        if value == "OFF" :
            return self.arret
        return None

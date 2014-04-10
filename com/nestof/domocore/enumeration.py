'''
Created on 10 avr. 2014

@author: S0087931
'''

from enum import Enum, unique
from com.nestof.domocore import utils


@unique
class Mode(Enum):
    automatique = 0
    manuel = 1

@unique
class Etat(Enum):
    on = 1
    off = 0


@unique
class Ordre(Enum):
    onAuto = 0b100
    onManuel = 0b010
    off = 0b000
    
    def getBinValue(self):
        return utils.intToBin3(self.value)
    
@unique
class NiveauPuissance(Enum):
    niveau1 = 1
    niveau2 = 2
    niveau3 = 3
    niveau4 = 4
    niveau5 = 5
    
    def getBinValue(self):
        return utils.intToBin3(self.value)
    
@unique
class NiveauVentilation(Enum):
    niveau1 = 1
    niveau2 = 2
    niveau3 = 3
    niveau4 = 4
    niveau5 = 5
    auto = 6
    
    def getBinValue(self):
        return utils.intToBin3(self.value)
    
@unique
class Actionneur(Enum):
    systeme = 1
    utilisateur = 2

def getOrdre(mode, etat):
    if not isinstance(mode, Mode) :
        raise Exception('mode is not an instance of Mode')
    
    if not isinstance(etat, Etat) :
        raise Exception('etat is not an instance of Etat')
    
    if etat == Etat.off :
        return Ordre.off
        
    if mode == Mode.automatique :
        return Ordre.onAuto
    
    return Ordre.onManuel
     
        
        
    
    
    None
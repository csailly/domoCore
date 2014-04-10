'''
Created on 21 mars 2014

@author: S0087931
'''



from com.nestof.domocore import enumeration
from com.nestof.domocore import utils
from com.nestof.domocore.service.MCZProtocolService import MCZProtocolService


if __name__ == '__main__':
    print(utils.getFlag(enumeration.Ordre.off, enumeration.NiveauPuissance.niveau1 ,enumeration.NiveauVentilation.auto,  enumeration.Actionneur.systeme))
    
    mczProtocolService = MCZProtocolService(None)
    trame = mczProtocolService.getTrame(enumeration.NiveauPuissance.niveau3, enumeration.NiveauVentilation.niveau3, enumeration.Mode.automatique, enumeration.Etat.on, enumeration.Actionneur.utilisateur)
    print(trame)
    print(utils.binaryStringToHex(trame))
    

        
    
    
    
    
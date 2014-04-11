'''
Created on 21 mars 2014

@author: S0087931
'''



from com.nestof.domocore import enumeration
from com.nestof.domocore import utils
from com.nestof.domocore.service.MCZProtocolService import MCZProtocolService
from com.nestof.domocore.domain.HistoTrameMCZ import HistoTrameMCZ
from com.nestof.domocore.dao.HistoTrameMczDao import HistoTrameMczDao


if __name__ == '__main__':
    
    
    mczProtocolService = MCZProtocolService("D:\+sandbox\work\domocore\domotique.sqlite")
    
       
    trame = mczProtocolService.getTrame(enumeration.NiveauPuissance.niveau3, enumeration.NiveauVentilation.niveau3, enumeration.Mode.automatique, enumeration.Etat.on, enumeration.Actionneur.utilisateur)
    print(utils.binaryStringToHex(trame))
   
    histoTrameMcz = HistoTrameMCZ()
    histoTrameMcz._sendDate = utils.getCurrentDateTime()
    histoTrameMcz._actionneur = enumeration.Actionneur.utilisateur    
    histoTrameMcz._puissance = enumeration.NiveauPuissance.niveau3
    histoTrameMcz._ventilation = enumeration.NiveauVentilation.niveau3
    histoTrameMcz._order = enumeration.getOrdre(enumeration.Mode.automatique, enumeration.Etat.on)
    histoTrameMcz._flag = mczProtocolService.getFlag(histoTrameMcz._order, histoTrameMcz._puissance, histoTrameMcz._ventilation, histoTrameMcz._actionneur)
    
    histoTrameMczDao = HistoTrameMczDao("D:\+sandbox\work\domocore\domotique.sqlite")
    histoTrameMczDao.save(histoTrameMcz)

    
    
    
    

        
    
    
    
    
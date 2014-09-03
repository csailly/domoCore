# -*- coding: utf-8 -*-
'''
Created on 21 mars 2014

@author: S0087931
'''


import configparser
import logging
from os.path import os, sys

pathname = os.path.dirname(sys.argv[0])
sys.path.append(os.path.abspath(pathname) + "/../../../")

from com.nestof.domocore import enumeration
from com.nestof.domocore import utils
from com.nestof.domocore.service.DatabaseService import DatabaseService
from com.nestof.domocore.service.MCZService import MCZService





if __name__ == '__main__':

    
    if sys.platform.startswith('linux') :
        _configFilename = 'domocore.cfg'
        from com.nestof.domocore.service.TempService import TempService
        tempService = TempService()
    elif sys.platform.startswith('win') :
        _configFilename = 'domocoreDev.cfg'
        from com.nestof.domocore.service.TempServiceDev import TempServiceDev
        tempService = TempServiceDev()
    else :
        print("Unknown Operating System : " + sys.platform)
        exit(1)
    
    """ Loading config file """
    print("Loading config file...")    
    _configFile = "../../../" + _configFilename
    
    if os.path.isfile(_configFile):    
        try:
            with open(_configFile) as file:
                pass
        except IOError as e:
            print ("Unable to open config file " + _configFile)  # Does not exist OR no read permissions
            exit(1)
    else:
        print("Config file " + _configFile + " not found")
        exit(1)    
        
    config = configparser.ConfigParser()
    config.read(_configFile, 'utf-8')
    
    """Logger configuration """
    print("Configuring logger...")
    loggingFilePath = config['LOGGER']['logger.path']
    loggingFileName = config['LOGGER']['logger.filename']    
    logging.basicConfig(filename=loggingFilePath + loggingFileName, format='[%(asctime)s][%(levelname)s][%(name)s] - %(message)s', level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    """ Database configuration """
    print("Loading database...")
    databasePath = config['DATABASE']['database.path']
    databaseFilename = config['DATABASE']['database.filename']

    try:
        with open(databasePath + databaseFilename) as file:
            pass
    except IOError as e:
        print("Unable to open database " + databasePath + databaseFilename)  # Does not exist OR no read permissions
        exit(1)

    """ Services """    
    databaseService = DatabaseService(databasePath + databaseFilename)
    mczService = MCZService(databasePath + databaseFilename)

    """ Stove configuration """
    configurationPoele = databaseService.getConfig()

    if (configurationPoele == enumeration.ConfigurationPeole().automatique) :
        print("Launch automatique mode...")
        mczService.launchAuto()
    elif (configurationPoele == enumeration.ConfigurationPeole().manuel) :
        print("Launch manuel mode...")
        mczService.launchManu()
    else:
        print("Launch stop mode...")
        mczService.launchStop()
        
        


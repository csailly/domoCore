# -*- coding: utf-8 -*-
'''
Created on 21 mars 2014

@author: S0087931
'''


from os.path import os, sys

pathname = os.path.dirname(sys.argv[0])
sys.path.append(os.path.abspath(pathname) + "/../../../")

import configparser
import logging
from com.nestof.domocore import utils
from com.nestof.domocore.service.DatabaseService import DatabaseService
from com.nestof.domocore.service.MCZService import MCZService

if __name__ == '__main__':

    """ Loading config file """
    print("Loading config file...")
    if sys.platform.startswith('linux') :
        _configFilename = 'domocore.cfg'
    elif sys.platform.startswith('win') :
        _configFilename = 'domocoreDev.cfg'
    else :
        print("Unknown Operating System : " + sys.platform)
        exit(1)
        
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

    """ Stove configuration """
    currentConfig = databaseService.getConfig()

    mczService = MCZService(databasePath + databaseFilename)
    
    print("Launch...")
    mczService.launchAuto()
        


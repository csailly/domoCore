# -*- coding: utf-8 -*-
'''
Created on 21 mars 2014

@author: S0087931
'''


import configparser
import logging
import logging.config
from os.path import os, sys, normpath, normcase

from com.nestof.domocore import enumeration
from com.nestof.domocore.service.DatabaseService import DatabaseService
from com.nestof.domocore.service.MCZProtocolService import MCZProtocolService
from com.nestof.domocore.service.MCZService import MCZService
from com.nestof.domocore import utils


if __name__ == '__main__':

    
    if sys.platform.startswith('linux') :
        configFilename = 'domocore.cfg'
        from com.nestof.domocore.service.TempService import TempService
        tempService = TempService()
    elif sys.platform.startswith('win') :
        configFilename = 'domocoreDev.cfg'
        from com.nestof.domocore.service.TempServiceDev import TempServiceDev
        tempService = TempServiceDev()
    else :
        print("Unknown Operating System : " + sys.platform)
        exit(1)
    
    """ Loading config file """
    print("Loading config file...")    
    _configFile = normcase(normpath("conf")) + os.sep + configFilename
    
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
    loggingFilePath = normcase(normpath(config['LOGGER']['logger.path'])) + os.sep
    loggingFileName = config['LOGGER']['logger.filename']    
    logging.basicConfig(filename=loggingFilePath + loggingFileName, format='[%(asctime)s][%(levelname)s][%(name)s] - %(message)s', level=logging.DEBUG)
    
    
    
    # logging.config.fileConfig(normcase(normpath("conf")) + os.sep + "logging.conf")
    logger = logging.getLogger(__name__)

    
    """ Database configuration """
    print("Loading database...")
    databasePath = normcase(normpath(config['DATABASE']['database.path'])) + os.sep
    databaseFilename = config['DATABASE']['database.filename']

    try:
        with open(databasePath + databaseFilename) as file:
            pass
    except IOError as e:
        print("Unable to open database " + databasePath + databaseFilename)  # Does not exist OR no read permissions
        exit(1)

    """ Services """    
    databaseService = DatabaseService(databasePath + databaseFilename)

    """Read current temp"""
    temp = currentTemp = tempService.readTemp()
    time = utils.getCurrentTime();
    date = utils.getCurrentDate();
    
    """Save current temp"""
    databaseService.saveTemp(date, time, temp)

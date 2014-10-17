# -*- coding: utf-8 -*-
'''
Created on 21 mars 2014

@author: S0087931
'''



import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler
from os.path import os, sys, normpath, normcase

from com.nestof.domocore import utils
from com.nestof.domocore.service.DatabaseService import DatabaseService


if __name__ == '__main__':

    print("****************************************************************************")
    print("**                       " + str(utils.getCurrentDateTime()) + "                       **")
    print("****************************************************************************")
    
    if sys.platform.startswith('linux') :
        configFilename = 'domocore.cfg'
        from com.nestof.domocore.service.TempService import Tmp102
        from com.nestof.domocore.service.TempService import DS18B20
        tempServiceTmp102 = Tmp102()
        tempServiceDs18b20 = DS18B20()
        from ConfigParser import ConfigParser
    elif sys.platform.startswith('win') :
        configFilename = 'domocoreDev.cfg'
        from com.nestof.domocore.service.TempServiceDev import TempServiceDev
        tempServiceTmp102 = TempServiceDev()
        tempServiceDs18b20 = TempServiceDev()
        from configparser import ConfigParser
    else :
        print("Unknown Operating System : " + sys.platform)
        exit(1)
    
    """ Loading config file """
    print("Loading config file...")    
    _configFile = normcase(normpath(os.path.dirname(os.path.abspath(__file__)))) + os.sep + normcase(normpath("conf")) + os.sep + configFilename
    
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
        
    config = ConfigParser()
    config.read(_configFile)
    
    """Logger configuration """
    print("Configuring logger...")
    loggingFilePath = normcase(normpath(config.get('LOGGER', 'logger.path'))) + os.sep
    loggingFileName = config.get('LOGGER', 'logger.releve.filename')    
    timedRotatingFileHandler = TimedRotatingFileHandler(loggingFilePath + loggingFileName, 'midnight', interval=1, backupCount=0, encoding='UTF-8', delay=True)       
    logging.basicConfig(filename=loggingFilePath + loggingFileName, format='[%(asctime)s][%(levelname)s][%(name)s] - %(message)s', level=logging.DEBUG)
    #logging.basicConfig(handlers=[timedRotatingFileHandler], format='[%(asctime)s][%(levelname)s][%(name)s] - %(message)s', level=logging.DEBUG)
    # logging.config.fileConfig(normcase(normpath("conf")) + os.sep + "logging.conf")
    logger = logging.getLogger(__name__)

    
    """ Database configuration """
    print("Loading database...")
    databasePath = normcase(normpath(config.get('DATABASE', 'database.path'))) + os.sep
    databaseFilename = config.get('DATABASE', 'database.filename')

    try:
        with open(databasePath + databaseFilename) as file:
            pass
    except IOError as e:
        print("Unable to open database " + databasePath + databaseFilename)  # Does not exist OR no read permissions
        exit(1)

    """ Services """    
    databaseService = DatabaseService(databasePath + databaseFilename)

    """Read current temp"""
    time = utils.getCurrentTime();
    date = utils.getCurrentDate();
    tempSonde1 = tempServiceTmp102.readTemp()
    tempSonde2 = tempServiceDs18b20.readTemp()
    
    
    """Save current temp"""
    databaseService.saveTemp(date, time, tempSonde1, 1)
    databaseService.saveTemp(date, time, tempSonde2, 2)
    
    logger.debug(tempSonde1)

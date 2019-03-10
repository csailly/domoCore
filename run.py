# -*- coding: utf-8 -*-
'''
Created on 21 mars 2014

@author: S0087931
'''



import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler

from os.path import os, sys, normpath, normcase

from com.nestof.domocore import enumeration
from com.nestof.domocore import utils
from com.nestof.domocore.service.DatabaseService import DatabaseService
from com.nestof.domocore.service.MCZProtocolService import MCZProtocolService
from com.nestof.domocore.service.MCZService import MCZService


if __name__ == '__main__':
    
    print("****************************************************************************")
    print("**                       " + str(utils.getCurrentDateTime()) + "                       **")
    print("****************************************************************************")
    
    if sys.platform.startswith('linux') :
        configFilename = 'domocore.cfg'
        from com.nestof.domocore.service.TempService import Tmp102
        from com.nestof.domocore.service.TempService import Degrade
        try:
            tempService = Tmp102()
        except Exception as e:
            tempService = Degrade()
        from ConfigParser import ConfigParser
    elif sys.platform.startswith('win') :
        configFilename = 'domocoreDev.cfg'
        from com.nestof.domocore.service.TempServiceDev import TempServiceDev
        tempService = TempServiceDev()
        from configparser import ConfigParser
    else :
        print("Unknown Operating System : " + sys.platform)
        exit(1)
    
    """ Loading config file """  
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
    loggingFilePath = normcase(normpath(config.get('LOGGER', 'logger.path'))) + os.sep
    loggingFileName = config.get('LOGGER', 'logger.filename')
    logging.basicConfig(filename=loggingFilePath + loggingFileName,\
                         format='[%(asctime)s][%(levelname)s][%(name)s-%(funcName)s-%(lineno)s] - %(message)s', level=logging.ERROR)
    #timedRotatingFileHandler = TimedRotatingFileHandler(loggingFilePath + loggingFileName, 'midnight', interval=1, backupCount=0, encoding='UTF-8', delay=True)       
    #logging.basicConfig(handlers=[timedRotatingFileHandler], format='[%(asctime)s][%(levelname)s][%(name)s] - %(message)s', level=logging.DEBUG)
    # logging.config.fileConfig(normcase(normpath("conf")) + os.sep + "logging.conf")
    logger = logging.getLogger(__name__)

    logger.info("**             Démarrage                            **")
    
    """ Database configuration """
    databasePath = normcase(normpath(config.get('DATABASE', 'database.path'))) + os.sep
    databaseFilename = config.get('DATABASE', 'database.filename')

    try:
        with open(databasePath + databaseFilename) as file:
            pass
    except IOError as e:
        logger.error("Unable to open database " + databasePath + databaseFilename)  # Does not exist OR no read permissions
        exit(1)

    """ Services """    
    databaseService = DatabaseService(databasePath + databaseFilename)
    mczProtocolService = MCZProtocolService(databasePath + databaseFilename)
    mczService = MCZService(databaseService, tempService, mczProtocolService, config)

    """ Stove configuration """
    configurationPoele = databaseService.getConfig()

    if (configurationPoele == enumeration.ConfigurationPeole().automatique) :
        logger.debug("Launch Automatique Mode...")
        mczService.launchAuto()
    elif (configurationPoele == enumeration.ConfigurationPeole().manuel) :
        logger.debug("Launch Manual Mode...")
        mczService.launchManu()
    else:
        logger.debug("Launch Stop Mode...")
        mczService.launchStop()
    
    logger.info("**              Terminé                             **")   
    exit(0)   


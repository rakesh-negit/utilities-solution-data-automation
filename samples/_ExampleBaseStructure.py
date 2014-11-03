"""
    @author:
    @contact:
    @company: Esri
    @version: 1.0.0
    @description:
    @requirements: Python 2.7.x, ArcGIS 10.2.1
    @copyright: Esri, 2014
"""

import agol
from agol import common

import arcpy
from arcpy import env

import sys, os, datetime
import gettext,locale


import ConfigParser

import arcpyhelper
from arcpyhelper import helper



logFileName ='.\\logs\\log.log'
configFilePath =  '.\\configs\\_ExampleConfig.ini'
dateTimeFormat = '%Y-%m-%d %H:%M'


def main(log,config):
    try:

        exampleConfigValue = config.get('SAMPLE', 'SETTING')
        print exampleConfigValue

    except helper.HelperError,e:
        line, filename, synerror = helper.trace()
        print _("error on line: %s") % line
        print _("error in file name: %s") % filename
        print _("with error message: %s") % synerror
        print _("Add. Error Message: %s") % e
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


    except arcpy.ExecuteError:

        line, filename, synerror = helper.trace()
        print _("error on line: %s") % line
        print _("error in file name: %s") % filename
        print _("with error message: %s") % synerror
        print _("ArcPy Error Message: %s") % arcpy.GetMessages(2)
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


    except:
        line, filename, synerror = helper.trace()
        print _("error on line: %s") % line
        print _("error in file name: %s") % filename
        print _("with error message: %s") % synerror
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def init_localization():
  '''prepare l10n'''
  locale.setlocale(locale.LC_ALL, '') # use user's preferred locale
  # take first two characters of country code
  loc = locale.getlocale()
  filename = "res/messages_%s.mo" % locale.getlocale()[0][0:2]

  try:
    print( "Opening message file %s for locale %s", filename, loc[0] )
    trans = gettext.GNUTranslations(open( filename, "rb" ) )
  except IOError:
    print( "Locale not found. Using default messages" )
    trans = gettext.NullTranslations()

  trans.install()

if __name__ == "__main__":
    init_localization()
    env.overwriteOutput = True
    #Create the log file
    try:
        log = open(logFileName, 'a')

    except:
        print _("Log file could not be created")

    #Change the output to both the windows and log file
    original = sys.stdout
    sys.stdout = helper.Tee(sys.stdout, log)

    print _("***************Script Started******************")
    print datetime.datetime.now().strftime(dateTimeFormat)

    #Load the config file
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            config = ConfigParser.ConfigParser()
            config.read(sys.argv[1])
        else:
            print _("INI file not found.")
            sys.exit()

    else:
        if os.path.isfile(configFilePath):
            config = ConfigParser.ConfigParser()
            config.read(configFilePath)
        else:
            print _("INI file not found.")
            sys.exit()

    #Run the script

    main(log,config)
    print datetime.datetime.now().strftime(dateTimeFormat)
    print _("###############Script Completed#################")
    print ""
    log.close()

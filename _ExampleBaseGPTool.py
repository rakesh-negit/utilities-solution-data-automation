"""
    @author:
    @contact:
    @company: Esri
    @version: 1.0.0
    @description:
    @requirements: Python 2.7.x, ArcGIS 10.2.1
    @copyright: Esri, 2014
"""
import sys, os, datetime
import gettext, locale

import arcpy
from arcpy import env
from arcpy import mapping
from arcpy import da


import agol
from agol import common

import arcpyhelper
from arcpyhelper import helper


def main(*argv):
    try:

        # Script arguments
        gpParam = argv[0]

        arcpy.SetParameterAsText(1,output)


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
    argv = tuple(arcpy.GetParameterAsText(i)
        for i in xrange(arcpy.GetArgumentCount()))
    main(*argv)



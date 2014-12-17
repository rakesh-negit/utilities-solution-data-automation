"""
    @company: Esri
    @version: 1.0.0
    @description: Appends features to a feature service
    @requirements: Python 2.7.x, ArcGIS 10.1
    @copyright: Esri, 2014
"""
import os
import sys
import arcpy

from arcpyhelper import ArcRestHelper
from arcpyhelper import Common


def trace():
    """
        trace finds the line, the filename and error message and returns it
        to the user
    """
    import inspect
    import traceback
    import sys
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    # script name + line number
    line = tbinfo.split(", ")[1]
    filename = inspect.getfile( inspect.currentframe() )
    # Get Python syntax error
    #
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror
def outputPrinter(message):
    arcpy.AddMessage(message=message)
    print(message)
def main(*argv):
    try:
    
        userName = argv[0]
        password = argv[1]
        org_url = argv[2]
        fsId = argv[3]
        layerNames = argv[4]
        sql = argv[5]
    
        arh = ArcRestHelper.featureservicetools(username = userName, password=password,org_url=org_url,
                                                   token_url=None, 
                                                   proxy_url=None, 
                                                   proxy_port=None)                    
        if not arh is None:
            outputPrinter(message="Security handler created")
                    
            fs = arh.GetFeatureService(itemId=fsId,returnURLOnly=False)
            if arh.valid:
                outputPrinter("Logged in successful")        
                if not fs is None:
                    for layerName in layerNames.split(','):
                        fl = arh.GetLayerFromFeatureService(fs=fs,layerName=layerName,returnURLOnly=False)
                        if not fl is None:
                            results = fl.deleteFeatures(where=sql)        
                            outputPrinter (message=results)
                        else:
                            
                            outputPrinter(message="Layer %s was not found, please check your credentials and layer name" % layerName)        
                else:
                    outputPrinter(message="Feature Service with id %s was not found" % fsId)                    
            else:
                outputPrinter(arh.message)   
                arcpy.SetParameterAsText(6, "false")
                
            
        else:
            outputPrinter(message="Security handler not created, exiting")
            arcpy.SetParameterAsText(6, "false")
            
        arcpy.SetParameterAsText(6, "true")
    except arcpy.ExecuteError:
        line, filename, synerror = trace()
        outputPrinter("error on line: %s" % line)
        outputPrinter("error in file name: %s" % filename)
        outputPrinter("with error message: %s" % synerror)
        outputPrinter("ArcPy Error Message: %s" % arcpy.GetMessages(2))
        arcpy.SetParameterAsText(6, "false")
    except:
        line, filename, synerror = trace()
        outputPrinter("error on line: %s" % line)
        outputPrinter("error in file name: %s" % filename)
        outputPrinter("with error message: %s" % synerror)
        arcpy.SetParameterAsText(6, "false")
    finally:
        pass
if __name__ == "__main__":
    argv = tuple(arcpy.GetParameterAsText(i)
        for i in xrange(arcpy.GetArgumentCount()))
    main(*argv)

























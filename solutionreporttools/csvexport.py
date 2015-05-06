"""
    @author: ArcGIS for Gas Utilities
    @contact: ArcGISTeamUtilities@esri.com
    @company: Esri
    @version: 1.0
    @description: Class is used to export a feature into CSV using field alias
    @requirements: Python 2.7.x, ArcGIS 10.2
    @copyright: Esri, 2015
    @originial source of script is from http://mappatondo.blogspot.com/2012/10/this-is-my-python-way-to-export-feature.html with modifications
"""
import sys, arcpy, csv
from arcpy import env
class ReportToolsError(Exception):
    """ raised when error occurs in utility module functions """
    pass
def trace():
    """
        trace finds the line, the filename
        and error message and returns it
        to the user
    """
    import traceback, inspect
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    filename = inspect.getfile(inspect.currentframe())
    # script name + line number
    line = tbinfo.split(", ")[1]
    # Get Python syntax error
    #
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror
class CSVExport:
    _tempWorkspace = None
    _tempFeature = None
    _CSVLocation = None
       
    def __init__(self, configParams=""):
        # Gets the values of where the temp feature class resides and
        # the output location of the CSV.
        try:
            if configParams and configParams != "":
                
                if "ResultsGDB" in configParams:
                    self._tempWorkspace = configParams["ResultsGDB"]
                
                if "CSVOutputLocation" in configParams:
                    self._CSVLocation = configParams["CSVOutputLocation"]
                
                self._tempFeature = "CSVTemp"
                    

            else:
                print "Error, no config file path specified."
                
        except arcpy.ExecuteError:
            line, filename, synerror = trace()
            raise ReportToolsError({
                "function": "create_report_layers_using_config",
                "line": line,
                "filename":  filename,
                "synerror": synerror,
                "arcpyError": arcpy.GetMessages(2),
            }
            )
        except:
            line, filename, synerror = trace()
            raise ReportToolsError({
                "function": "create_report_layers_using_config",
                "line": line,
                "filename":  filename,
                "synerror": synerror,
            }
            )
          
        
    def WriteCSV(self):
        # This function writes the CSV. It writes the header then the rows. This script omits the SHAPE fields.
        try:
            env.workspace = self._tempWorkspace
           
            fc = arcpy.ListFeatureClasses(self._tempFeature)
            for fcs in fc:      
                    
                outFile = open(self._CSVLocation, 'wb')      
                print "%s create" % self._CSVLocatio
                linewriter = csv.writer(outFile, delimiter = ',')
                
                fcdescribe = arcpy.Describe(fcs)
                flds = fcdescribe.Fields
        
                header = []
                resFields = []
                if hasattr(fcdescribe, 'areaFieldName'):
                    resFields.append(fcdescribe.areaFieldName)
                if hasattr(fcdescribe, 'lengthFieldName'):
                    resFields.append(fcdescribe.lengthFieldName)
                if hasattr(fcdescribe, 'shapeFieldName'):
                    resFields.append(fcdescribe.shapeFieldName)                
                
                fldLst = []
                for fld in flds:
                    value = fld.AliasName
                    #if value.upper() == 'SHAPE':
                    if (fld.name in resFields):
                        pass
                    else:
                        fullHeader = value
                        header.append(fullHeader)
                        fldLst.append(fld.name)
                linewriter.writerow(header)
               
                with arcpy.da.SearchCursor(fcs,fldLst) as rows:
                    for row in rows:
                        line = []
                        for i in range(0,len(fldLst)):
                                           
                            value = row[i]
                            
                            line.append(value)
                    
                        linewriter.writerow([s.encode('utf8') if isinstance(s,unicode) else s for s in line])
                    del line
                   
                    del row
                    del rows
                outFile.close() 
                print "CSV file complete"
            return True
        except arcpy.ExecuteError:
            line, filename, synerror = trace()
            raise ReportToolsError({
                "function": "create_report_layers_using_config",
                "line": line,
                "filename":  filename,
                "synerror": synerror,
                "arcpyError": arcpy.GetMessages(2),
            }
            )
        except:
            line, filename, synerror = trace()
            raise ReportToolsError({
                "function": "create_report_layers_using_config",
                "line": line,
                "filename":  filename,
                "synerror": synerror,
            }
            )
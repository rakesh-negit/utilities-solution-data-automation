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
import sys, os, arcpy, csv, codecs, commands
from arcpy import env

class CSVExport:
    _tempWorkspace = None
    _tempFeature = None
    _CSVLocation = None
       
    def __init__(self,configParams=""):
        # Gets the values of where the temp feature class resides and the output location of the CSV.
        try:
            if configParams and configParams != "":
                
                if "ResultsGDB" in configParams:
                    self._tempWorkspace = configParams["ResultsGDB"]
                
                if "CSVOutputLocation" in configParams:
                    self._CSVLocation = configParams["CSVOutputLocation"]
                
                self._tempFeature = "CSVTemp"
                    
                return None
            else:
                print "Error, no config file path specified."
                return False        
        except:
            print "Unexpected error initializing CSV report:", sys.exc_info()[0]
            return False  
        
    def WriteCSV(self):
        # This function writes the CSV. It writes the header then the rows. This script omits the SHAPE fields.
        try:
            env.workspace = self._tempWorkspace
           
            fc = arcpy.ListFeatureClasses(self._tempFeature)
            for fcs in fc:      
                    
                    outFile = open(self._CSVLocation, 'wb')      
            
                    linewriter = csv.writer(outFile, delimiter = ',')
                    
                    fcdescribe = arcpy.Describe(fcs)
                    flds = fcdescribe.Fields
            
                    header = []
                    for fld in flds:
                        value = fld.AliasName
                        #if value.upper() == 'SHAPE':
                        if (value.upper() == "SHAPE") | (value.upper() == "SHAPE_LENGTH") | (value.upper() == "SHAPE_AREA"):
                            continue
                        else:
                            fullHeader = value
                            header.append(fullHeader)
                    linewriter.writerow(header)
            
                    cursor = arcpy.SearchCursor(fcs)
                    row = cursor.next()
            
                    while row:
                        line = []
                        for fld in flds:
                            value = row.getValue(fld.Name)
                            if (fld.Name.upper() == "SHAPE") | (fld.Name.upper() == "SHAPE_LENGTH") | (fld.Name.upper() == "SHAPE_AREA"):
                            #if str(value).startswith("<geo"):
                                continue
                            else:
                                line.append(value)
                        
                        linewriter.writerow([s.encode('utf8') if type(s) is unicode else s for s in line])
                        del line
                        row = cursor.next()
                    
                    del cursor
                    outFile.close() 
            return True
        except:
            print "Unexpected error creating CSV report:", sys.exc_info()[0]
            return False         

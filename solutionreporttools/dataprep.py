"""
    @author: ArcGIS for Utilities
    @contact: ArcGISTeamUtilities@esri.com
    @company: Esri
    @version: 1.0
    @description: Used to prep data for reporting and other geoprocessing task by copying datasets from enterprise to local geodatabases.
    @requirements: Python 2.7.x, ArcGIS 10.2
    @copyright: Esri, 2015
    @Usage: temp = DataPrep.DataPrep(configFilePath="path to config file")  to intialize(each of the below can be called independently)
            temp.CopyData()
            This can also be called from a different application.  Just need to pass in the config as a DICT object
"""
import arcpy
import os
import sys
import common as Common
import subprocess

class DataPrep:

    overWrite = None
    databases = None
    start_db =  None
    end_db = None
    datasetsToInclude = None       
    standaloneFeatures = None
    calledFromApp = None
    postExtractGP = None

    def __init__(self,configFilePath=""):
    
        # This checks to see whether this Data Prep is ran as a standalone or as a sub process in another application
        if configFilePath and configFilePath != "":
            if type(configFilePath) is dict:
                configParams = configFilePath
                self.calledFromApp = True
            else:
                configParams = Common.init_config_json(config_file=configFilePath)
                self.calledFromApp = False
        
            if "Databases" in configParams:
                self.databases = configParams["Databases"]
                
            return None
        else:
            print "Error, no config file path specified."
            return False
 
    def CopyData(self):
        print "************ BEGIN copying SDE to Local DB ****************"
        # Read the config values and store in local variables then start extraction
        # It all depends on if it can create a GDB, if not, all other processes are bypassed.
        for database in self.databases:
            self.overWrite = None
            self.databases = None
            self.start_db =  None
            self.end_db = None
            self.datasetsToInclude = None       
            self.standaloneFeatures = None
            self.postExtractGP = None
            retVal = True
            if "GDBPath" in database and "SDEPath" in database:
                if (database["GDBPath"].lower()).find(".sde") == -1:
                    self.start_db =  database["SDEPath"]
                    self.end_db =  database["GDBPath"]
                    self.overWrite = database["Overwrite"]
                    if self._CheckCreateGDBProcess():
                        if "DataSets" in database:
                            if database["DataSets"]:
                                self.datasetsToInclude = database["DataSets"]
                                retVal = self._CopyDatasetsProcess()
                        if "FeatureClasses" in database:
                            if database["FeatureClasses"]:
                                self.standaloneFeatures = database["FeatureClasses"]
                                retVal = self._CopyDataTypeProcess(type="FeatureClasses") 
                        if "Tables" in database:
                            if database["Tables"]:
                                self.standaloneFeatures = database["Tables"]
                                retVal = self._CopyDataTypeProcess(type="Tables")  
                        if "PostProcesses" in database:
                            if database["PostProcesses"]:
                                self.postExtractGP = database["PostProcesses"]
                                retVal = self._executePostProcess() 
                else:
                    print "Sorry, can not copy sde to sde at this time" 
                    retVal = False                   
        print "************ END copying SDE to Local DB ****************"
        return retVal
        
    def _CopyDatasetsProcess(self): 
        try: 
            if self.datasetsToInclude: 
                #Set workspaces
                arcpy.env.workspace = self.start_db
                wk2 = self.end_db
                datasetList = arcpy.ListDatasets()
                
                #Check GDB if not created already, create it now
                if self._CheckCreateGDBProcess():
                
                    for dataset in datasetList:
                        name = arcpy.Describe(dataset)
                        new_data=name.name.split('.')[-1]
                        
                        # if user specified *, then user wants all datasets and child objects copied
                        if "*" in self.datasetsToInclude and len(self.datasetsToInclude) == 1:
                            #print "Reading: {0}".format(dataset)
                            if arcpy.Exists(wk2 + os.sep + new_data)==False:      
                                arcpy.Copy_management(dataset, wk2 + os.sep + new_data)
                                print "Created Dataset {0} and all childs in local gdb".format(new_data)
                        else:
                        # If a list of dataset names is stated, check to see if it iterating dataset is in that list
                            for checkDS in self.datasetsToInclude:                               
                                if new_data == checkDS["Name"]:
                                    print "Reading: {0}".format(dataset)
                                    if arcpy.Exists(wk2 + os.sep + new_data)==False:
                                        
                                        if "*" in checkDS["FeatureClasses"] and len(checkDS["FeatureClasses"]) == 1:
                                            arcpy.Copy_management(dataset, wk2 + os.sep + new_data)
                                            print "Created Dataset {0} and all childs in local gdb".format(new_data)                                           
                                        else:
                                            #Create the dataset envelope. Creating and not copying because user might not want all
                                            #features copied into this dataset
                                            arcpy.CreateFeatureDataset_management(self.end_db, new_data, dataset)
                                            print "Created Dataset {0} in local gdb".format(new_data)
                                            
                                            #Handles child features of the datset.  Can either copy all or user defined features
                                            if name.children:
                                                self._CheckChildFeatures(ds=name.name,childList=name.children,checkList=checkDS["FeatureClasses"])
                                    else:                            
                                        #Handles child features of the datset if dataset already exist.  Only copy new ones
                                        if name.children:
                                            self._CheckChildFeatures(ds=name.name,childList=name.children,checkList=checkDS["FeatureClasses"])                            
                                        print "Dataset {0} already exists in the end_db checking for childs".format(new_data)                  
                    #Clear memory
                    del dataset
            return True
        except:
            print "Unexpected error copying feature datasets:", sys.exc_info()[0]
            return False
    
    def _CopyDataTypeProcess(self,type="FeatureClasses",ds="",fc=""):
        try:   
            #Set workspaces
            arcpy.env.workspace = self.start_db
            wk2 = self.end_db
            
            if(self.calledFromApp):
                for featClass in self.standaloneFeatures:
                    if featClass.upper().find(".SDE") != -1:
                        featName = featClass.split('.')[-1]
                    else:
                        featName = featClass.split('/')[-1]
                    arcpy.FeatureClassToFeatureClass_conversion(featClass,wk2,featName)
                    print "Completed copy on {0}".format(featName) 
            else:
            
                # if ds passed value exist then this call came from a copy dataset child object request.
                if ds != "":
                    if arcpy.Exists(wk2 + os.sep + ds.split('.')[-1] + os.sep + fc.split('.')[-1])==False:
                        if type == "FeatureClasses":
                            arcpy.FeatureClassToFeatureClass_conversion(self.start_db + os.sep + ds + os.sep + fc,wk2 + os.sep + ds.split('.')[-1],fc.split('.')[-1])
                            #arcpy.Copy_management(self.start_db + os.sep + ds + os.sep + fc, wk2 + os.sep + ds.split('.')[-1] + os.sep + fc.split('.')[-1])
                            print "Completed copy on {0}".format(fc)
                else:
                # This function was called independently        
                    #Check GDB if not created already, create it now
                    if self._CheckCreateGDBProcess():
                    #Determine the object type and List out
                        if type == "Tables":
                            dataTypeList = arcpy.ListTables()
                        else:
                            dataTypeList = arcpy.ListFeatureClasses()
                            
                        for dtl in dataTypeList:
                            name = arcpy.Describe(dtl)
                            new_data=name.name.split('.')[-1]
                            
                            # Checks to see if user wants to copy all features or just the ones that match the supplied list.
                            if "*" in self.standaloneFeatures and len(self.standaloneFeatures) == 1:
                                #print "Reading: {0}".format(dtl)
                                if arcpy.Exists(wk2 + os.sep + new_data)==False:
                                    if type == "Tables":
                                        arcpy.TableToTable_conversion(dtl,wk2,new_data)
                                    else:
                                        arcpy.FeatureClassToFeatureClass_conversion(dtl,wk2,new_data)                           
                                    print "Completed copy on {0}".format(new_data)
                            else:
                                if new_data in self.standaloneFeatures:
                                    print "Reading here: {0}".format(dtl)
                                    if arcpy.Exists(wk2 + os.sep + new_data)==False:                     
                                        if type == "Tables":
                                            arcpy.TableToTable_conversion(dtl,wk2,new_data)
                                        else:
                                            arcpy.FeatureClassToFeatureClass_conversion(dtl,wk2,new_data)
                                        print "Completed copy on {0}".format(new_data)                   
                                    else:
                                        print "Feature class {0} already exists in the end_db so skipping".format(new_data)
                    #Clear memory
                    del dtl
            return True
        except:
            print "Unexpected error copying feature classes:", sys.exc_info()[0]
            return False
 
    def _CheckChildFeatures(self,ds="",childList="",checkList=""):
         #Handles child features of the datset.  Can either copy all or user defined features
        try:         
            if checkList:
                children = childList
                for child in children:
                    #Determines if all features will be copied.  Sending to copy feature class function
                    #to keep the handling of different data types separate.
                    if "*" in checkList and len(checkList) == 1:
                        self._CopyDataTypeProcess(ds=ds,fc=child.name)
                    else:
                        if child.name.split('.')[-1] in checkList:
                            self._CopyDataTypeProcess(ds=ds,fc=child.name)
        except:
            print "Unexpected error checking for child features:", sys.exc_info()[0]
            return False                            
    
    def _CheckCreateGDBProcess(self):
        try:
            # If user param is to overwrite GDB, then delete it first
            if self.overWrite.upper() == "YES":
                if arcpy.Exists(self.end_db)==True:
                    arcpy.Delete_management(self.end_db)
                    self.overWrite = None
                    print "Deleted previous GDB {0}".format(self.end_db)
             
            # if the local gdb doesn't exist, then create it using the path and name given in the end_db string
            if arcpy.Exists(self.end_db)==False:
                if self.end_db.rfind("\\") != -1:    
                    lastSlash = self.end_db.rfind("\\")
                else:
                    lastSlash = self.end_db.rfind("/")           
                arcpy.CreateFileGDB_management(self.end_db[:lastSlash], self.end_db[lastSlash+1:])
                self.overWrite = None
                print "Created geodatabase {0}".format(self.end_db[lastSlash+1:])
            else:
                self.overWrite = None
                #print "Geodatabase already exists" 
            return True 
        except:
            print "Unexpected error create geodatabase:", sys.exc_info()[0]
            return False
        
    def _executePostProcess(self):
        try:  
            print "Running post process GP (not yet implemented)"
            #for postGP in self.postExtractGP:
                #subprocess.call([sys.executable, os.path.join(get_script_dir(), 'test.py')])
        except:
            print "Unexpected error executing GP tool:", sys.exc_info()[0]
            return False                  
    
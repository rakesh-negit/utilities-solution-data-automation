import os, sys
import traceback

import arcpy
from arcpy import env

import time


import datetime
import inspect
import random
import string
import json

import gettext, locale
import ConfigParser

from copy import deepcopy


import arcrest

from urlparse import urlparse

import base64
import uuid

from dateutil.parser import parse

dateTimeFormat = '%Y-%m-%d %H:%M'


class HelperError(Exception):
    """ raised when error occurs in utility module functions """
    pass
#----------------------------------------------------------------------
class Tee(object):
    """ Combines standard output with a file for logging"""

    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)


# get a UUID - URL safe, Base64
def get_a_Uuid():
    r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    return r_uuid.replace('=', '')
def get_guid():
    return str(uuid.uuid1())

def update_existing_service_from_config(config):
    proc_info = []
    if 'ExistingService' in config['PublishingDetails']:
        
        ext_services = config['PublishingDetails']['ExistingService']
        for ext_service in ext_services:
            fURL = ext_service['URL']
            
            if config['PublishingDetails']['Credentials'].has_key('Portal') == False:
                config['PublishingDetails']['Credentials']['Portal'] = ''
                
            
            fl = layer.FeatureLayer(url = fURL,
                                    username = config['PublishingDetails']['Credentials']['Username'],
                                    password = config['PublishingDetails']['Credentials']['Password'])                        
            if fl == None:
                proc_info.append(
                    {'error':fl})
            else:        
                if 'DeleteInfo' in ext_service:
                    if str(ext_service['DeleteInfo']['Delete']).upper() == "TRUE":
                        res = fl.deleteFeatures(where = ext_service['DeleteInfo']['DeleteSQL'])
                       
                        proc_info.append(res)
                            
                        
                res = fl.addFeatures(fc = ext_service['ReportResult'])
                proc_info.append(res)                
                    
    return proc_info

#----------------------------------------------------------------------
def publish_service_map_from_config(config):

    results = {}
    publish_info = config['PublishingDetails']
 
    resultFS = publish_feature_service_from_config(config=config)
    results["ServiceInfo"] = resultFS
    for res in resultFS:
    
        if 'error' in res:
            print str(resultMap)
        elif 'error' in res['FSInfo']:
            print str(resultMap)
    
        
    resultMap = publish_map_from_config(config=config,fsInfo=resultFS)              
    if (resultMap != None):
        if len(resultMap) > 0:
            results["MapInfo"] = resultMap
            if 'error' in resultMap:
                print str(resultMap)
        else:
            results["MapInfo"] = "error"                    
    else:
        results["MapInfo"] = "error"
    
    return results

#----------------------------------------------------------------------
def publish_map_from_config(config,fsInfo=None):
    publish_info = config['PublishingDetails']

    maps_info = publish_info['MapDetails']
    map_results = []
    for map_info in maps_info:
        if map_info.has_key('ReplaceInfo'):
            replaceInfo = map_info['ReplaceInfo']
        else:
            replaceInfo = None
    
    
        cred_info = publish_info['Credentials']
    
        print _("            Starting Map Publishing Process")
            # AGOL Credentials
        username = cred_info['Username']
        password = cred_info['Password']
        if cred_info.has_key('Portal') == False:
            portal = ''
        else:
            portal = cred_info['Portal']
        
        agol = admin.AGOL(username=username, password=password,org_url=portal)
        if replaceInfo != None:
    
            for replaceItem in replaceInfo:
                if replaceItem['ReplaceType'] == 'Layer':
                    
                    for fs in fsInfo: 
                        if fs is not None and replaceItem['ReplaceString'] == fs['ReplaceTag']:
                            replaceItem['ReplaceString'] = fs['FSInfo']['serviceurl']
                            replaceItem['ItemID'] = fs['FSInfo']['serviceItemId']
                            replaceItem['ItemFolder'] = fs['FSInfo']['folderId']
                        elif replaceItem.has_key('ItemID'):
                            if replaceItem.has_key('ItemFolder') == False:
            
                                itemID = replaceItem['ItemID']
                                itemInfo = agol.item(item_id=itemID)
                                if 'owner' in itemInfo:
                                    if itemInfo['owner'] == username and 'ownerFolder' in itemInfo:
                                        replaceItem['ItemFolder'] = itemInfo['ownerFolder']
                                    else:
                                        replaceItem['ItemFolder'] = None
        
        itemInfo  = publishWebMapFromConfig(agol=agol, config=map_info,
                                           replaceInfo=replaceInfo)
        if not 'error' in itemInfo:
            print _("            %s webmap created" %
                    itemInfo['Name'])
            map_results.append(itemInfo)
    
        else:
            print str(itemInfo)
            map_results.append(itemInfo)
    return map_results

#----------------------------------------------------------------------
def publish_dashboard_from_config(config,mapInfo=None):

    publish_info = config['PublishingDetails']
    app_info = publish_info['AppDetails']
    cred_info = publish_info['Credentials']
  
    if app_info.has_key('ReplaceInfo'):
        replaceInfo = app_info['ReplaceInfo']
    else:
        replaceInfo = None

    print _("            Starting Dashboard Publishing Process")

    # AGOL Credentials
    username = cred_info['Username']
    password = cred_info['Password']
    if cred_info.has_key('Portal') == False:
        portal = ''
    else:
        portal = cred_info['Portal']    
    
    agol = admin.AGOL(username=username, password=password, org_url=portal)

    for replaceItem in replaceInfo:
        if mapInfo is not None and replaceItem['ReplaceString'] == '{WebMap}':
            replaceItem['ReplaceString'] = mapInfo

    delete_existing = False if app_info['UpdateItemContents'].upper() == "TRUE" else True

    name = ''
    tags = ''
    description = ''
    extent = ''

    item_data = ''

    itemJson = app_info['ItemJSON']

    item_data= agol.itemData(item_id = mapInfo)
    layerNamesID = {}
    layerIDs =[]


    if 'operationalLayers' in item_data:
        for opLayer in item_data['operationalLayers']:
            layerNamesID[opLayer['title']] = opLayer['id']
            layerIDs.append(opLayer['id'])

    with open(itemJson) as json_data:
        try:
            item_data = json.load(json_data)
        except:
            raise ValueError("%s is not a valid JSON File" % webmapdef_path)
   
        for replaceItem in replaceInfo:
            if replaceItem['ReplaceType'] == 'Global':
                item_data = find_replace(item_data,replaceItem['SearchString'],replaceItem['ReplaceString'])
            elif replaceItem['ReplaceType'] == 'MapID':  
                widgets = item_data['widgets']
                for widget in widgets:
                
                    if widget.has_key('mapId'):
                        if replaceItem['SearchString'] in widget['mapId']:
                            widget['mapId'] = replaceItem['ReplaceString']
                            if widget.has_key('mapTools'):
                                for mapTool in widget['mapTools']:
                                    if mapTool.has_key('layerIds'):
                                        mapTool['layerIds'] = layerIDs
                            if widget.has_key('dataSources'):
                                for dataSource in widget['dataSources']:
                                    if dataSource.has_key('layerId'):
                                        if layerNamesID.has_key(dataSource['name']):
                                            dataSource['layerId'] = layerNamesID[dataSource['name']]
                                      
                            


    name = app_info['Title']

    if app_info.has_key('DateTimeFormat'):
        loc_df = app_info['DateTimeFormat']
    else:
        loc_df = dateTimeFormat

    datestring = datetime.datetime.now().strftime(loc_df)
    name = name.replace('{DATE}',datestring)
    name = name.replace('{Date}',datestring)

    description = app_info['Description']
    tags = app_info['Tags']
    snippet = app_info['Summary']

    extent = app_info['Extent']

    everyone = app_info['ShareEveryone']
    orgs = app_info['ShareOrg']
    groups = app_info['Groups']  #Groups are by ID. Multiple groups comma separated

    folderName = app_info['Folder']
    thumbnail = app_info['Thumbnail']

    itemType = app_info['Type']
    typeKeywords = app_info['typeKeywords']

    itemID = agol.publishItem(name=name,tags=tags,snippet=snippet,description=description,extent=extent,
                               data=item_data,thumbnail=thumbnail,share_everyone=everyone,share_org=orgs,share_groups=groups,
                               item_type=itemType,typeKeywords=typeKeywords,folder_name=folderName,delete_existing=delete_existing)

    return {"ItemID" : itemID, "Name" : name}

#----------------------------------------------------------------------
def publish_feature_service_from_config(config):
    publish_info = config['PublishingDetails']
    fs_info = publish_info['FeatureService']
    cred_info = publish_info['Credentials']


    print _("            Starting Feature Service Publishing Process")
        # AGOL Credentials
    username = cred_info['Username']
    password = cred_info['Password']
    if cred_info.has_key('Portal') == False:
        portal = ''
        securityHandler = arcrest.AGOLTokenSecurityHandler(username=username, password=password)    
    else:
        if cred_info['Portal'] == '' or cred_info['Portal'] is None:
            portal = ''
            securityHandler = arcrest.AGOLTokenSecurityHandler(username=username, password=password)                
        else:
            portal = cred_info['Portal']    
            securityHandler = arcrest.PortalTokenSecurityHandler(username=username, 
                                                            password=password, 
                                                            baseOrgUrl = portal, 
                                                            proxy_url=None, 
                                                            proxy_port=None)
        
    
    fsInfo = publishFSfromConfig(securityHandler, fs_info)
    for res in fsInfo:
        if not 'error' in res:
    
            if 'serviceurl' in res:
                print _("            %s created" % res['serviceurl'])
            
            else:
                print str(res)
        else:
            print str(res)
    return fsInfo
#----------------------------------------------------------------------
def create_report_layers_using_config(config):

    try:
        
        reports =  config['Reports']

        report_msg = []
        for i in reports:
            if i['Type'].upper()== "JOINCALCANDLOAD":
                create_calcload_report(report_params=i)                                   
            elif i['Type'].upper()== "RECLASS":
                reporting_areas = i ['ReportingAreas']
                if not os.path.isabs(reporting_areas):
                    reporting_areas =os.path.abspath(reporting_areas)
        
        
                reporting_areas_ID_field = i ['ReportingAreasIDField']

                report_msg.append( create_reclass_report(reporting_areas=reporting_areas,
                                     reporting_areas_ID_field=reporting_areas_ID_field,
                                     report_params=i))
            elif i['Type'].upper()== "AVERAGE":
                reporting_areas = i['ReportingAreas']
                if not os.path.isabs(reporting_areas):
                    reporting_areas =os.path.abspath(reporting_areas)
                
                reporting_areas_ID_field = i['ReportingAreasIDField']
                
                report_msg.append(create_average_report(reporting_areas=reporting_areas,
                                     reporting_areas_ID_field=reporting_areas_ID_field,
                                     report_params=i))
            else:
                print "Unsupported report type"
        if 'error' in report_msg:
            return False
        else:
            return True


    except HelperError,e:
        line, filename, synerror = trace()
        print _("error on line: %s") % line
        print _("error in file name: %s") % filename
        print _("with error message: %s") % synerror
        print _("Add. Error Message: %s") % e
        print datetime.datetime.now().strftime(dateTimeFormat)
        return False


    except arcpy.ExecuteError:

        line, filename, synerror = trace()
        print _("error on line: %s") % line
        print _("error in file name: %s") % filename
        print _("with error message: %s") % synerror
        print _("ArcPy Error Message: %s") % arcpy.GetMessages(2)
        print datetime.datetime.now().strftime(dateTimeFormat)
        return False


    except:
        line, filename, synerror = trace()
        print _("error on line: %s") % line
        print _("error in file name: %s") % filename
        print _("with error message: %s") % synerror
        print datetime.datetime.now().strftime(dateTimeFormat)
        return False

#----------------------------------------------------------------------
def create_calcload_report(report_params):

    try:

        
        filt_layer = "filter_layer"

        reporting_layer = report_params['Data']
        reporting_layer_id_field = report_params['DataIDField']
        joinInfo = report_params['JoinInfo']
        
        field_map = report_params['FieldMap']

        sql = report_params['FilterSQL']

        report_date = report_params["ReportDateField"]
        report_schema = report_params['ReportResultSchema']
        report_result = report_params['ReportResult']

        #if not os.path.isabs(report_result):
            #report_result = os.path.abspath( report_result)

        #if not os.path.isabs(report_schema):
            #report_schema = os.path.abspath( report_schema)
            
        _tempWorkspace = env.scratchGDB    
        _tempTableName = random_string_generator()
        _tempTableFull = os.path.join(_tempWorkspace, _tempTableName)
        
        
        if sql == '' or sql is None or sql == '1=1' or sql == '1==1':
            filt_layer = reporting_layer
        else:
            #arcpy.MakeQueryTable_management(in_table=reporting_layer,out_table=filt_layer,in_key_field_option="USE_KEY_FIELDS",in_key_field="#",in_field="#",where_clause=sql)
            try:            
                arcpy.MakeFeatureLayer_management(reporting_layer, filt_layer, sql, "", "")
                
            except:      
                try:                
                    arcpy.TableToTable_conversion(in_rows=reporting_layer,out_path=_tempWorkspace,out_name=_tempTableName)
                                                      
                    arcpy.MakeTableView_management(in_table=_tempTableFull, out_view= filt_layer, where_clause=sql,workspace="#",field_info="#")                
                 
                except:      
                    pass
        inputCnt = int(arcpy.GetCount_management(in_rows=filt_layer)[0])
        arcpy.Copy_management(report_schema,report_result,"FeatureClass")
                      
        if inputCnt == 0:
            
            print _("      %s was created" % report_result)
        else:

            _procData = calculate_load_results(feature_data = joinInfo['FeatureData'], 
                             feature_data_id_field = joinInfo['FeatureDataIDField'],                          
                            join_table = filt_layer, 
                            join_table_id_field = reporting_layer_id_field,
                            report_date_field=report_date,
                            report_result = report_result, 
                            field_map = field_map
                            )
            
            
            
            deleteFC([_procData])
            if arcpy.Exists(_tempTableFull):
                deleteFC([_tempTableFull])

            print _("      %s was created" % report_result)

    except HelperError,e:
        line, filename, synerror = trace()
        print _("error on line: %s") % line
        print _("error in file name: %s") % filename
        print _("with error message: %s") % synerror
        print _("Add. Error Message: %s") % e
        print datetime.datetime.now().strftime(dateTimeFormat)


    except arcpy.ExecuteError:

        line, filename, synerror = trace()
        print _("error on line: %s") % line
        print _("error in file name: %s") % filename
        print _("with error message: %s") % synerror
        print _("ArcPy Error Message: %s") % arcpy.GetMessages(2)
        print datetime.datetime.now().strftime(dateTimeFormat)


    except:
        line, filename, synerror = trace()
        print _("error on line: %s") % line
        print _("error in file name: %s") % filename
        print _("with error message: %s") % synerror
        print datetime.datetime.now().strftime(dateTimeFormat)


#----------------------------------------------------------------------
def create_reclass_report(reporting_areas,reporting_areas_ID_field,report_params):

    try:

        classified_layer_field_name = "reclass"

        filt_layer = "filter_layer"

        reporting_layer = report_params['Data']
        field_map = report_params['FieldMap']
        sql = report_params['FilterSQL']


        count_field = report_params['CountField']
        reclass_map = report_params['ReclassMap']

        report_schema = report_params['ReportResultSchema']
        report_result = report_params['ReportResult']
        if not os.path.isabs(report_result):
            report_result =os.path.abspath( report_result)

        if not os.path.isabs(report_schema):
            report_schema =os.path.abspath( report_schema)

        report_date_field = report_params['ReportDateField']
        report_ID_field = report_params['ReportIDField']
        result_exp = report_params['FinalResultExpression']

        #if type(value_field) is tuple:
        #    average_value = value_field[1]
        #    value_field = value_field[0]

        if sql == '' or sql is None or sql == '1=1' or sql == '1==1':
            filt_layer = reporting_layer
        else:
            #arcpy.MakeQueryTable_management(in_table=reporting_layer,out_table=filt_layer,in_key_field_option="USE_KEY_FIELDS",in_key_field="#",in_field="#",where_clause=sql)
            arcpy.MakeFeatureLayer_management(reporting_layer, filt_layer, sql, "", "")

        inputCnt = int(arcpy.GetCount_management(in_rows=filt_layer)[0])
        if inputCnt == 0:
            copy_empty_report(reporting_areas=reporting_areas, reporting_areas_ID_field=reporting_areas_ID_field,
                              report_schema=report_schema,
                              report_result=report_result,
                              reclass_map=reclass_map,
                              report_date_field=report_date_field,
                              report_ID_field=report_ID_field)
            print _("      %s was created" % report_result)
        else:
            classified_layer = split_reclass(reporting_areas=reporting_areas, reporting_areas_ID_field=reporting_areas_ID_field,reporting_layer=filt_layer,field_map=field_map,
                                             reclass_map=reclass_map,classified_layer_field_name = classified_layer_field_name)

            pivot_layer = classified_pivot(classified_layer =classified_layer, classified_layer_field_name= classified_layer_field_name,
                                           reporting_areas_ID_field=reporting_areas_ID_field,count_field=count_field)

            report_copy = copy_report_data_schema(reporting_areas=reporting_areas,reporting_areas_ID_field=reporting_areas_ID_field,report_schema=report_schema,
                                                  report_result=report_result,join_layer=pivot_layer)


            calculate_report_results(report_result=report_result,  reporting_areas_ID_field=reporting_areas_ID_field,report_copy=report_copy,
                                     reclass_map=reclass_map, report_date_field=report_date_field,report_ID_field=report_ID_field, exp=result_exp)

            deleteFC([classified_layer,pivot_layer,report_copy])

            print _("      %s was created" % report_result)

    except HelperError,e:
        line, filename, synerror = trace()
        print _("error on line: %s") % line
        print _("error in file name: %s") % filename
        print _("with error message: %s") % synerror
        print _("Add. Error Message: %s") % e
        print datetime.datetime.now().strftime(dateTimeFormat)


    except arcpy.ExecuteError:

        line, filename, synerror = trace()
        print _("error on line: %s") % line
        print _("error in file name: %s") % filename
        print _("with error message: %s") % synerror
        print _("ArcPy Error Message: %s") % arcpy.GetMessages(2)
        print datetime.datetime.now().strftime(dateTimeFormat)


    except:
        line, filename, synerror = trace()
        print _("error on line: %s") % line
        print _("error in file name: %s") % filename
        print _("with error message: %s") % synerror
        print datetime.datetime.now().strftime(dateTimeFormat)

#----------------------------------------------------------------------
def create_average_report(reporting_areas,reporting_areas_ID_field,report_params):

    try:

        filt_layer = "filter_layer"
        reporting_layer = report_params['Data']
        field_map = report_params['FieldMap']
        sql = report_params['FilterSQL']

        code_exp = report_params['PreCalcExpression']

        report_schema = report_params['ReportResultSchema']
        report_result = report_params['ReportResult']

        if not os.path.isabs(report_result):
            report_result =os.path.abspath( report_result)

        if not os.path.isabs(report_schema):
            report_schema =os.path.abspath( report_schema)

        report_date_field = report_params['ReportDateField']
        report_ID_field = report_params['ReportIDField']

        avg_field_map = report_params['AverageToResultFieldMap']

        if sql == '' or sql is None or sql == '1=1' or sql == '1==1':
            filt_layer = reporting_layer
        else:
                      #arcpy.MakeQueryTable_management(in_table=reporting_layer,out_table=filt_layer,in_key_field_option="USE_KEY_FIELDS",in_key_field="#",in_field="#",where_clause=sql)
            arcpy.MakeFeatureLayer_management(reporting_layer, filt_layer, sql, "", "")

        inputCnt = int(arcpy.GetCount_management(in_rows=filt_layer).getOutput(0))
        if inputCnt == 0:
            pass
        else:

            result = split_average(reporting_areas=reporting_areas, reporting_areas_ID_field=reporting_areas_ID_field,reporting_layer=filt_layer,
                         reporting_layer_field_map=field_map,code_exp=code_exp)

            if 'layer' in result:

                report_copy = copy_report_data_schema(reporting_areas=reporting_areas,reporting_areas_ID_field=reporting_areas_ID_field,report_schema=report_schema,
                                                      report_result=report_result,join_layer=result['layer'])

                report_result = calculate_average_report_results(report_result=report_result,
                                                reporting_areas_ID_field=reporting_areas_ID_field ,
                                                report_copy=report_copy,
                                                field_map=avg_field_map,
                                                report_date_field=report_date_field,
                                                report_ID_field=report_ID_field,
                                                average_field=result['field'])
                print _("      %s was created" % report_result)



    except HelperError,e:
        line, filename, synerror = trace()
        print _("error on line: %s") % line
        print _("error in file name: %s") % filename
        print _("with error message: %s") % synerror
        print _("Add. Error Message: %s") % e
        print datetime.datetime.now().strftime(dateTimeFormat)


    except arcpy.ExecuteError:

        line, filename, synerror = trace()
        print _("error on line: %s") % line
        print _("error in file name: %s") % filename
        print _("with error message: %s") % synerror
        print _("ArcPy Error Message: %s") % arcpy.GetMessages(2)
        print datetime.datetime.now().strftime(dateTimeFormat)


    except:
        line, filename, synerror = trace()
        print _("error on line: %s") % line
        print _("error in file name: %s") % filename
        print _("with error message: %s") % synerror
        print datetime.datetime.now().strftime(dateTimeFormat)

#----------------------------------------------------------------------
def calculate_load_results(feature_data, 
                           feature_data_id_field,                         
                           join_table, 
                           join_table_id_field,
                           report_date_field,
                           report_result, 
                           field_map
                           ):
    # one_to_many_table,one_to_many_table_id_field, one_to_many_table_feature_id_field, 
    
    #"OneToManyTable": "../Maps and GDBs/CustomerComplaints.gdb/CustomerToMeter",
           #"OneToManyTableDataIDField": "ACCOUNTID",
           #"OneToManyTableFeatureDataIDField": "FACILITYID"    

    _tempWorkspace = env.scratchGDB
    
    _feature_data_layer = random_string_generator()
    _join_table_copy = random_string_generator()
    _joinedDataFull = os.path.join(_tempWorkspace, _join_table_copy)
    
    _pointsJoinedData = random_string_generator()
    _pointsJoinedDataFull = os.path.join(_tempWorkspace, _pointsJoinedData)
    # Process: Make Feature Layer
    if arcpy.Exists(dataset = feature_data) == False:
        return {"Error": feature_data + " Does not exist"}
    
    if arcpy.Exists(dataset = join_table) == False:
        return {"Error": join_table + " Does not exist"}    
    
    arcpy.MakeFeatureLayer_management(in_features=feature_data, out_layer=_feature_data_layer, where_clause=None, workspace=None, field_info=None)
    
    # Process: Table to Table
    arcpy.TableToTable_conversion(join_table, _tempWorkspace, _join_table_copy, "", "#", "")
      
    # Process: Add Join
    arcpy.AddJoin_management(_feature_data_layer, feature_data_id_field, _joinedDataFull, join_table_id_field, "KEEP_COMMON")
    
    arcpy.FeatureClassToFeatureClass_conversion(_feature_data_layer, _tempWorkspace, _pointsJoinedData, "", "", "")

    joinTableDesc = arcpy.Describe(_joinedDataFull)
    joinName = str(joinTableDesc.name)    
            
    featureDataDesc = arcpy.Describe(feature_data)
    featureDataName = str(featureDataDesc.name)    

    try:    
        arcpy.RemoveJoin_management(_feature_data_layer, joinName)
    except:
        pass
    
    
    fields = []
    tFields = []       
    layerFlds = fieldsToFieldArray(featureclass = _pointsJoinedDataFull)
    
    for fld in field_map:
        if fld['FieldName'] in layerFlds:
        
         
            fields.append(fld['FieldName'])            
        elif joinName + "_" + fld['FieldName'] in layerFlds:
            fld['FieldName'] = joinName + "_" + fld['FieldName']
            fields.append( fld['FieldName'])
        elif featureDataName + "_" + fld['FieldName'] in layerFlds:
            fld['FieldName'] = featureDataName + "_" + fld['FieldName']
            fields.append( fld['FieldName'])                
        
    if len(fields) != len(field_map):    
        print "Field Map length does not match fields in layer, exiting"
        return
    
    for fld in field_map:
        tFields.append(fld['TargetField'])        
    
    
    tFields.append("SHAPE@")
    
    fields.append("SHAPE@")
    
    datefld = -1
    if report_date_field in tFields:
        datefld = tFields.index(report_date_field)
    elif report_date_field != '':
        tFields.append(report_date_field)
        
    icursor = arcpy.da.InsertCursor(report_result,tFields)   
    strOnlineTime = common.online_time_to_string(common.local_time_to_online(),dateTimeFormat)
                                                  
    with arcpy.da.SearchCursor(_pointsJoinedDataFull, fields) as scursor:
        for row in scursor:
            new_row=list(row)
            if datefld > -1 :
                dt = parse(new_row[datefld])
                onlTm = local_time_to_online(dt)
                timeStr = online_time_to_string(onlTm,dateTimeFormat)
                new_row[datefld] = timeStr
            elif report_date_field != '':    
                new_row.append(strOnlineTime)  
            icursor.insertRow(new_row)   
        
                    
#----------------------------------------------------------------------
def split_average(reporting_areas, reporting_areas_ID_field,reporting_layer, reporting_layer_field_map,code_exp):
    _tempWorkspace = env.scratchGDB

    _intersect = os.path.join(_tempWorkspace ,random_string_generator())
    sumstats = os.path.join(_tempWorkspace ,random_string_generator())

    # Process: Intersect Reporting Areas with Reporting Data to split them for accurate measurements
    arcpy.Intersect_analysis(in_features="'"+ reporting_areas + "' #;'" + reporting_layer+ "' #",out_feature_class= _intersect,join_attributes="ALL",cluster_tolerance="#",output_type="INPUT")

    age_field="statsfield"
    # Process: Add a field and calculate it with the groupings required for reporting.  If CP is set, _CP will be apped to the end of the material type.
    arcpy.AddField_management(in_table=_intersect, field_name=age_field, field_type="LONG",field_precision= "", field_scale="", field_length="",
                              field_alias="",field_is_nullable= "NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

    calc_field(inputDataset=_intersect,field_map=reporting_layer_field_map,code_exp=code_exp,result_field=age_field)

    arcpy.Statistics_analysis(_intersect,out_table=sumstats,statistics_fields=age_field + " MEAN",case_field=reporting_areas_ID_field)

    deleteFC([_intersect])

    return {"layer":sumstats,"field":"MEAN_"+age_field}

#----------------------------------------------------------------------
def split_reclass(reporting_areas, reporting_areas_ID_field,reporting_layer, field_map,reclass_map,classified_layer_field_name):
    _tempWorkspace = env.scratchGDB

    _intersect = os.path.join(_tempWorkspace ,random_string_generator())

    # Process: Intersect Reporting Areas with Reporting Data to split them for accurate measurements
    arcpy.Intersect_analysis(in_features="'"+ reporting_areas + "' #;'" + reporting_layer+ "' #",out_feature_class= _intersect,join_attributes="ALL",cluster_tolerance="#",output_type="INPUT")

    # Process: Add a field and calculate it with the groupings required for reporting.  If CP is set, _CP will be apped to the end of the material type.
    arcpy.AddField_management(in_table=_intersect, field_name=classified_layer_field_name, field_type="TEXT",field_precision= "", field_scale="", field_length="",
                              field_alias="",field_is_nullable= "NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

    flds = []
    for fld in field_map:
        flds.append(fld['FieldName'])
    flds.append(reporting_areas_ID_field)
    flds.append( "SHAPE@")
    flds.append(classified_layer_field_name)

    newRows = []

    with arcpy.da.UpdateCursor(_intersect, flds) as urows:
        for row in urows:
            val_fnd = False
            for field in reclass_map:
                sql_state = field['Expression']
                try:


                    for i in range (len( field_map)):
                        sql_state = sql_state.replace(field_map[i]['Expression'],str(row[i]))

                    if eval(sql_state) == True:
                        if val_fnd == True:
                            newRow = deepcopy(row)
                            newRow[len(flds) - 1] = field['FieldName']
                            newRows.append(newRow)

                        else:
                            row[len(flds) - 1] = field['FieldName']
                            val_fnd = True
                except Exception, e:
                    print _("       WARNING: %s is not valid" % str(sql_state))

            if val_fnd == False:

                row[len(flds) - 1] = 'NORECLASS'
            urows.updateRow(row)

        del urows
        if len(newRows) > 0 :
            with arcpy.da.InsertCursor(_intersect, flds) as irows:

                for newRow in newRows:
                    irows.insertRow(newRow)


            del irows
    return _intersect
#----------------------------------------------------------------------
def classified_pivot(classified_layer, classified_layer_field_name, reporting_areas_ID_field, count_field,summary_fields=''):
    _tempWorkspace = env.scratchGDB

    _freq = os.path.join(_tempWorkspace ,random_string_generator())
    _pivot = os.path.join(_tempWorkspace ,random_string_generator())

    if not count_field in summary_fields and count_field != 'FREQUENCY':
        summary_fields = count_field if summary_fields =='' else summary_fields + ";" + count_field

    arcpy.Frequency_analysis(in_table=classified_layer, out_table=_freq,frequency_fields= reporting_areas_ID_field + ';' + classified_layer_field_name , summary_fields=summary_fields)


    #if average_value.upper() == 'TRUE':
        #with arcpy.da.UpdateCursor(_freq,('FREQUENCY',count_field)) as urows:
            #for row in urows:
                #if  row[1]  is None or  row[0] is None:
                    #pass
                #else:
                    #row[1] =  float(float(row[1]) / float(row[0]))
                #urows.updateRow(row)
            #del urows

    arcpy.PivotTable_management(_freq, reporting_areas_ID_field,classified_layer_field_name , count_field, _pivot)
    deleteFC([_freq])
    return _pivot
#----------------------------------------------------------------------
def copy_report_data_schema(reporting_areas, reporting_areas_ID_field,report_schema ,report_result, join_layer):
    _tempWorkspace = env.scratchGDB


    _reportCopy = random_string_generator()

    final_report = os.path.join(_tempWorkspace ,_reportCopy)

    # Process: Create a copy of the Reporting Areas for the summary info join
    arcpy.FeatureClassToFeatureClass_conversion(reporting_areas, _tempWorkspace, _reportCopy, "", reporting_areas_ID_field + ' "' + reporting_areas_ID_field + '" true true false 50 Text 0 0 ,First,#,' + reporting_areas +',' + reporting_areas_ID_field + ',-1,-1', "")

    # Process: Join the Areas to the pivot table to get a count by area
    arcpy.JoinField_management(final_report, reporting_areas_ID_field, join_layer, reporting_areas_ID_field, "#")

    # Process: Create a copy of the report layer
    if not os.path.isabs(report_result):
        report_result =os.path.abspath( report_result)

    if not os.path.isabs(report_schema):
        report_schema =os.path.abspath( report_schema)


    arcpy.Copy_management(report_schema,report_result,"FeatureClass")
    return final_report
#----------------------------------------------------------------------
def calculate_average_report_results(report_result, reporting_areas_ID_field,report_copy, field_map  ,report_date_field,report_ID_field,average_field  ):

    fields = []
    for fld in field_map:
        fields.append(fld['FieldName'])

    fields.append(report_ID_field)
    fields.append(report_date_field)
    fields.append("SHAPE@")

    strOnlineTime = common.online_time_to_string(common.local_time_to_online(),dateTimeFormat)
    #strLocalTime = datetime.datetime.now().strftime(dateTimeFormat)


    search_fields = [average_field,reporting_areas_ID_field,"SHAPE@"]

    with arcpy.da.InsertCursor(report_result,fields) as irows:
        with arcpy.da.SearchCursor(report_copy,search_fields) as srows:
            for row in srows:
                newrow = []

                for fld in field_map:
                    try:

                        newrow.append(eval(fld["Expression"].replace("{Value}", str(noneToValue( row[0],0.0)))))
                    except Exception, e:
                        newrow.append(None)
                newrow.append(row[1])
                newrow.append(strOnlineTime)
                newrow.append(row[2])

                irows.insertRow(tuple(newrow)  )

        del srows
    del irows
    return report_result
#----------------------------------------------------------------------

def calculate_report_results(report_result, reporting_areas_ID_field,report_copy, reclass_map  ,report_date_field,report_ID_field ,exp ):

    appendString=""
    fields = []
    for fld in reclass_map:
        appendString +=   fld['FieldName'] + " \"\" true true false 8 Double 0 0 ,First,#," + report_copy + "," + fld['FieldName'] + ",-1,-1;"
        fields.append(fld['FieldName'])

    appendString +=  report_ID_field + " \"\" true true false 80 string 0 0 ,First,#," + report_copy + "," + reporting_areas_ID_field + ",-1,-1;"


    arcpy.Append_management(report_copy,report_result, "NO_TEST",appendString, "")

    strOnlineTime = common.online_time_to_string(common.local_time_to_online(),dateTimeFormat)
    #strLocalTime = datetime.datetime.now().strftime(dateTimeFormat)
    fields.append(report_date_field)

    with arcpy.da.UpdateCursor(report_result,fields) as urows:
        for row in urows:
            for u in range(len(fields) - 1):
                row[u]= eval(exp.replace('{Value}', str(noneToValue( row[u],0.0))))# {'__builtins__':{}}

            row[len(fields)-1] = strOnlineTime
            urows.updateRow(row)
        del urows

#----------------------------------------------------------------------
def copy_empty_report(reporting_areas, reporting_areas_ID_field,report_schema ,report_result,reclass_map  ,report_date_field,report_ID_field):

    _tempWorkspace = env.scratchGDB

    _reportCopy = random_string_generator()

    _final_report = os.path.join(_tempWorkspace ,_reportCopy)

    # Process: Create a copy of the Reporting Areas for the summary info join
    arcpy.FeatureClassToFeatureClass_conversion(reporting_areas, _tempWorkspace, _reportCopy, "", reporting_areas_ID_field + ' "' + reporting_areas_ID_field + '" true true false 50 Text 0 0 ,First,#,' + reporting_areas +',' + reporting_areas_ID_field + ',-1,-1', "")

    # Process: Create a copy of the report layer
    arcpy.Copy_management(report_schema,report_result,"FeatureClass")

    appendString = report_ID_field + " \"\" true true false 80 string 0 0 ,First,#," + _final_report + "," + reporting_areas_ID_field + ",-1,-1;"

    arcpy.Append_management(_final_report,report_result, "NO_TEST",appendString, "")

    strOnlineTime = common.online_time_to_string(common.local_time_to_online(),dateTimeFormat)
    #strLocalTime = datetime.datetime.now().strftime(dateTimeFormat)

    fields = []
    for fld in reclass_map:
        fields.append(fld['FieldName'])


    fields.append(report_date_field)

    with arcpy.da.UpdateCursor(report_result,fields) as urows:
        for row in urows:
            for u in range(len(fields) - 1):
                row[u]= str(noneToValue( row[u],0.0))


            row[len(fields)-1] = strOnlineTime
            urows.updateRow(row)
        del urows

    deleteFC([_final_report])

#----------------------------------------------------------------------
def init_config_ini(config_file):

    config = None
    #Load the config file
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            config = ConfigParser.ConfigParser()
            config.read(sys.argv[1])
        else:
            pass

    else:
        if os.path.isfile(config_file):
            config = ConfigParser.ConfigParser()
            config.read(config_file)
        else:
            pass
    return config
#----------------------------------------------------------------------
def init_config_json(config_file):

    #Load the config file
    with open(config_file) as json_file:
        json_data = json.load(json_file)
        return unicode_convert( json_data)
    
def write_config_json(config_file, data):
    with open(config_file, 'w') as outfile:
        json.dump(data, outfile)  
      
#----------------------------------------------------------------------
def unicode_convert(obj):
    """ converts unicode to anscii """
    if isinstance(obj, dict):
        return {unicode_convert(key): unicode_convert(value) for key, value in obj.iteritems()}
    elif isinstance(obj, list):
        return [unicode_convert(element) for element in obj]
    elif isinstance(obj, unicode):
        return obj.encode('utf-8')
    else:
        return obj
def find_replace(obj,find,replace):
    """ searchs an object and does a find and replace """
    if isinstance(obj, dict):
        return {find_replace(key,find,replace): find_replace(value,find,replace) for key, value in obj.iteritems()}
    elif isinstance(obj, list):
        return [find_replace(element,find,replace) for element in obj]
    elif obj == find:
        return replace
    else:
        return obj 
#----------------------------------------------------------------------
def init_log(log_file,):

    #Create the log file
    log = None
    try:
        log = open(log_file, 'a')

        #Change the output to both the windows and log file
        #original = sys.stdout
        sys.stdout = Tee(sys.stdout, log)
    except Exception:
        pass
    return log


#----------------------------------------------------------------------
def init_localization():
    '''prepare l10n'''
    locale.setlocale(locale.LC_ALL, '') # use user's preferred locale
    # take first two characters of country code
    filename = "res/messages_%s.mo" % locale.getlocale()[0][0:2]

    try:
        #print( "Opening message file %s for locale %s") % (filename, loc[0])
        trans = gettext.GNUTranslations(open( filename, "rb" ) )
    except IOError:
        #print( "Locale not found. Using default messages" )
        trans = gettext.NullTranslations()

    trans.install()

#----------------------------------------------------------------------
def trace():
    """
        trace finds the line, the filename
        and error message and returns it
        to the user
    """
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    filename = inspect.getfile( inspect.currentframe() )
    # script name + line number
    line = tbinfo.split(", ")[1]
    # Get Python syntax error
    #
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror



def deleteFC(in_datasets):

    for in_data in in_datasets:
        try:
            if in_data is not None:
                if arcpy.Exists(dataset=in_data):
                    arcpy.Delete_management(in_data=in_data)
        except Exception:
            print "Unable to delete %s" % in_data

#----------------------------------------------------------------------
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

def shapeBasedSpatialJoin(TargetLayer, JoinLayer,JoinResult):
    if not arcpy.Exists( TargetLayer):
        raise ValueError(TargetLayer + " does not exist")
    if not arcpy.Exists( JoinLayer):
        raise ValueError(JoinLayer + " does not exist")
    # Local variables:
    _tempWorkspace = env.scratchGDB

    _targetCopyName = random_string_generator()
    _targetCopy = os.path.join(_tempWorkspace ,_targetCopyName)
    #JoinResult = os.path.join(_tempWorkspace ,random_string_generator())
    _areaFieldName = random_string_generator(size=12)
    _idenResultLayer ="polyIdenLayer"

    _lenAreaFld = "SHAPE_Area"

    layDetails = arcpy.Describe(TargetLayer)
    if layDetails.shapeType == "Polygon":
        _lenAreaFld = "Shape_Area"
    elif layDetails.shapeType == "Polyline":
        _lenAreaFld = "Shape_Length"
    else:
        return ""
    arcpy.FeatureClassToFeatureClass_conversion(TargetLayer,_tempWorkspace,_targetCopyName,"#","","#")
    # Process: Copy
    # Process: Add Field
    arcpy.AddField_management(_targetCopy, _areaFieldName, "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

    # Process: Calculate Field
    arcpy.CalculateField_management(_targetCopy, _areaFieldName, "!" + _lenAreaFld +"!", "PYTHON_9.3", "")

    # Process: Identity
    arcpy.Identity_analysis(_targetCopy, JoinLayer, JoinResult, "ALL", "", "NO_RELATIONSHIPS")

    # Process: Make Feature Layer
    arcpy.MakeFeatureLayer_management(JoinResult, _idenResultLayer, "", "", "")

    # Process: Select Layer By Attribute
    arcpy.SelectLayerByAttribute_management(_idenResultLayer, "NEW_SELECTION", _lenAreaFld + " < .5 *  " + _areaFieldName)

    # Process: Delete Features
    arcpy.DeleteFeatures_management(_idenResultLayer)

    deleteFC([_targetCopy])

    return JoinResult

def JoinAndCalc(inputDataset, inputJoinField, joinTable, joinTableJoinField,copyFields, joinType="KEEP_ALL"):
    try:
        """

            copyFields = [('Field to copy','Field to store it in'),('Field to copy','Field to store it in'),('Field to copy','Field to store it in')]"""
        inputLayer = "inputLayer"
        arcpy.MakeFeatureLayer_management (inputDataset, inputLayer)

        joinTableDesc = arcpy.Describe(joinTable)
        joinName = str(joinTableDesc.name)
        arcpy.AddJoin_management(inputLayer, inputJoinField, joinTable, joinTableJoinField,joinType)
        removeJoin = True

        tz = time.timezone # num of seconds to add to GMT based on current TimeZone
##        fields = arcpy.ListFields(inputLayer)
##        for field in fields:
##            print("{0} is a type of {1} with a length of {2}"
##                .format(field.name, field.type, field.length))
        for copyField in copyFields:
            if len(copyField) == 3:
                dateExp = "import time\\nimport datetime\\nfrom time import mktime\\nfrom datetime import datetime\\ndef calc(dt):\\n  return datetime.fromtimestamp(mktime(time.strptime(str(dt), '" + str(copyField[2]) + "')) +  time.timezone)"
                exp =  'calc(!' + joinName +'.' + copyField[0] + '!)'
                arcpy.CalculateField_management(inputLayer,copyField[1], exp, 'PYTHON_9.3', dateExp)

            else:
                arcpy.CalculateField_management(inputLayer,copyField[1], '!' + joinName +'.' + copyField[0] + '!', "PYTHON_9.3", "")

            print copyField[1] + " Calculated from " + copyField[0]

        arcpy.RemoveJoin_management(inputLayer,joinName)
    except arcpy.ExecuteError:
        line, filename, synerror = trace()
        raise HelperError({
                    "function": "JoinAndCalc",
                    "line": line,
                    "filename":  filename,
                    "synerror": synerror,
                    "arcpyError": arcpy.GetMessages(2),
                                    }
                                    )
    except:
        line, filename, synerror = trace()
        raise HelperError({
                    "function": "JoinAndCalc",
                    "line": line,
                    "filename":  filename,
                    "synerror": synerror,
                                    }
                                    )
def FieldExist(featureclass, fieldNames):
    """FieldExist(dataset, [fieldNames])

       Determines if the array of fields exist in the dataset

         dataset(String):
       The specified feature class or table whose indexes will be returned.

         fieldNames{Array}:
       The the array of field name to verify existance."""
    try:
        fieldList = arcpy.ListFields(featureclass)
        fndCnt = 0
        for field in fieldList:
            if field.name in fieldNames:
                fndCnt = fndCnt + 1

            if fndCnt >0 :
                return True
        if fndCnt != len(fieldNames):
            return False

    except:
        line, filename, synerror = trace()
        raise HelperError({
            "function": "FieldExist",
            "line": line,
            "filename":  filename,
            "synerror": synerror,
        }
                          )

def FieldExistReturnFieldName(featureclass, fieldNames):
    """FieldExist(dataset, [fieldNames])

       Determines if the array of fields exist in the dataset

         dataset(String):
       The specified feature class or table whose indexes will be returned.

         fieldNames{Array}:
       The the array of field name to verify existance."""
    try:
        fieldList = arcpy.ListFields(featureclass)
        fndCnt = 0
        for field in fieldList:
            if field.name in fieldNames:
                for fldname in fieldNames:
                    if field.name == fldname:
                        return fldname
                    
        return None
    except:
        line, filename, synerror = trace()
        raise HelperError({
            "function": "FieldExist",
            "line": line,
            "filename":  filename,
            "synerror": synerror,
        }
                          )
def fieldsToFieldArray(featureclass):
    """FieldExist(dataset)

       Determines if the array of fields exist in the dataset

         dataset(String):
       The specified feature class or table whose fields will be returned.

    """
    try:
        fieldList = arcpy.ListFields(featureclass)
        returnFields = []
        for field in fieldList:
            returnFields.append(field.name)
                    
        return returnFields
    except:
        line, filename, synerror = trace()
        raise HelperError({
            "function": "fieldsToFieldArray",
            "line": line,
            "filename":  filename,
            "synerror": synerror,
        }
                          )

def random_string_generator(size=6, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

def random_int_generator(maxrange):
    return random.randint(0,maxrange)

def local_time_to_online(dt=None):
    """
       converts datetime object to a UTC timestamp for AGOL
       Inputs:
          dt - datetime object
       Output:
          Long value
    """
    if dt is None:
        dt = datetime.datetime.now()

    is_dst = time.daylight > 0 and time.localtime().tm_isdst > 0
    utc_offset =  (time.altzone if is_dst else time.timezone)

    return (time.mktime(dt.timetuple()) * 1000) + (utc_offset * 1000)

def online_time_to_string(value,timeFormat):
    """
       Converts a timestamp to date/time string
       Inputs:
          value - timestamp as long
          timeFormat - output date/time format
       Output:
          string
    """
    return datetime.datetime.fromtimestamp(value /1000).strftime(timeFormat)
#----------------------------------------------------------------------
def calcFieldToOnlineTime(layer,field,timeFormat):
    if FieldExist(layer,field):
        with arcpy.da.UpdateCursor(layer, field) as cursor:
            for row in cursor:
                row[0] = online_time_to_string(local_time_to_online(row[0]),timeFormat)
                cursor.updateRow(row)



def currentToPrevious(inputDataset,fieldsPairs):



    """currentToPrevious(dataset, [{ToField,FromField},])

    Copies values from one field to another field

     dataset(String):
    The specified feature class or table

     fieldPairs{Array of Field Tuples}:
    The the array of field name to verify existance."""

    try:
        for fieldsPair in fieldsPairs:

            print fieldsPair[0] + " Calculated from " + fieldsPair[1]
            arcpy.CalculateField_management(inputDataset,fieldsPair[0], '!' + fieldsPair[1] + '!', "PYTHON_9.3", "")

    except:
        line, filename, synerror = trace()
        raise HelperError({
            "function": "currentToPrevious",
            "line": line,
            "filename":  filename,
            "synerror": synerror,
        })


def calc_field(inputDataset,field_map,code_exp,result_field):
    try:

        replaceValList = []
        newList =[]
        for fld in field_map:
            newList.append(fld['FieldName'])
            replaceValList.append (fld['ReplaceValue'])
        newList.append(result_field)
        with arcpy.da.UpdateCursor(inputDataset, newList) as cursor:

            for row in cursor:
                sqlState = code_exp
                try:
                    for i in range(0,len(replaceValList)):
                        sqlState = sqlState.replace(replaceValList[i],str(row[i]))

                    res = eval(sqlState)
                    row[len(newList) -1] = res
                    cursor.updateRow(row)

                except Exception:
                    cursor.deleteRow()


    except:
        line, filename, synerror = trace()
        raise HelperError({
            "function": "calculate_age_field",
            "line": line,
            "filename":  filename,
            "synerror": synerror,
        })
def calculate_age_field(inputDataset,field,result_field):
    try:


        newList =[field,result_field]
        with arcpy.da.UpdateCursor(inputDataset, newList) as cursor:


            for row in cursor:
                if row[0] == None:
                    cursor.deleteRow()
                else:
                    row[1] = datetime.datetime.now().year - row[0].year
                    cursor.updateRow(row)


    except:
        line, filename, synerror = trace()
        raise HelperError({
            "function": "calculate_age_field",
            "line": line,
            "filename":  filename,
            "synerror": synerror,
        })

def calculate_inline_stats(inputDataset,fields,result_field,stats_method):
    """calculate_inline_stats(inputDataset,(field1, field2,..),resultField,<Min, Max, Sum, Mean>)

    Calculates stats on the input table

     dataset(String):
    The specified feature class or table

     fields(field1,field2,..):
    List of fields to perform stats on

     result_field:
    Field to store the results on

     stats_method:
    Type of stats to perform
    """

    try:

        lstLen = len(fields)
        newList =deepcopy(fields)
        newList.append(result_field)
        with arcpy.da.UpdateCursor(inputDataset, tuple(newList)) as cursor:


            for row in cursor:
                row.pop(lstLen)
                if  stats_method.upper() == "AVERAGE" or  stats_method.upper() == "AVG" or  stats_method.upper() == "MEAN":
                    cnt = 0
                    val = 0
                    for i in row:
                        if i is not None:
                            cnt += 1
                            val += i
                    row.append(val/cnt)
                elif  stats_method.upper() == "MIN" or  stats_method.upper() == "MINIMUM":
                    minVal = min(i for i in row if i is not None)
                    row.append(minVal)
                elif  stats_method.upper() == "MAX" or  stats_method.upper() == "MAXIMUM":
                    maxVal = max(i for i in row if i is not None)
                    row.append(maxVal)
                cursor.updateRow(row)


    except:
        line, filename, synerror = trace()
        raise HelperError({
            "function": "currentToPrevious",
            "line": line,
            "filename":  filename,
            "synerror": synerror,
        })



def noneToValue(value,newValue):
    if value is None:
        return newValue
    else:
        return value


def fieldPrinter(layer):
    fieldList = arcpy.ListFields(layer)
    for field in fieldList:
        print("{0} is a type of {1} with a length of {2}".format(field.name, field.type, field.length))

def publishFSfromConfig(agol,config):
    res = []    
    if isinstance(config, list):
        for fs in config:
            if fs.has_key('ReplaceTag'):
                
                resItm = {"ReplaceTag":fs['ReplaceTag'] }
            else:
                resItm = {"ReplaceTag":"{FeatureService}" }
                
            resItm['FSInfo'] =_publishFSfromConfig(agol, fs)
            res.append( resItm)
            
    else:
        if config.has_key('ReplaceTag'):
                
            resItm = {"ReplaceTag":config['ReplaceTag'] }
        else:
            resItm = {"ReplaceTag":"{FeatureService}" }
            
        resItm['FSInfo'] =_publishFSfromConfig(agol, config)
        res.append(resItm)
    return res

        
def _publishFSfromConfig(agol,config):
    
    # Report settings
    mxd = config['Mxd']

    # Service settings
    service_name = config['Title']

    everyone = config['ShareEveryone']
    orgs = config['ShareOrg']
    groups = config['Groups']  #Groups are by ID. Multiple groups comma separated

    folderName = config['Folder']
    thumbnail = config['Thumbnail']
    
    capabilities = config['Capabilities']
    if config.has_key("maxRecordCount"):
        maxRecordCount =  config["maxRecordCount"]
    else:
        maxRecordCount =1000
   
    if config.has_key('DateTimeFormat'):
        loc_df = config['DateTimeFormat']
    else:
        loc_df = dateTimeFormat


    datestring = datetime.datetime.now().strftime(loc_df)
    service_name = service_name.replace('{DATE}',datestring)
    service_name = service_name.replace('{Date}',datestring)

  
    sd = arcrest.common.servicedef.MXDtoFeatureServiceDef(mxd_path=mxd, 
                                                         service_name=service_name, 
                                                         tags="None", 
                                                         description="None", 
                                                         folder_name=folderName, 
                                                         capabilities=capabilities, 
                                                         maxRecordCount=maxRecordCount, 
                                                         server_type='MY_HOSTED_SERVICES')  
    
    
    admin = arcrest.manageorg.Administration(url="http://www.arcgis.com", securityHandler=securityHandler, 
                                             proxy_url=None, 
                                             proxy_port=None, 
                                             initialize=False)
    
    
    portal = admin.portals()
    content = admin.content
    itemParams = arcrest.manageorg.ItemParameter()
    itemParams.title = service_name
    itemParams.thumbnail = "http://its.ucsc.edu/software/images/arcgis.jpg"
    itemParams.type = "Web Map"
    itemParams.tags = "Map, Earthquake"
    itemParams.extent = "-180,-80.1787,180, 80.1787"
    #   Enter in the username you wish to load the item to
     #
     usercontent = content.usercontent(username=username)
     #   Add the Web Map
     #
     print usercontent.addItem(itemParameters=itemParams,    
    itemInfo = agol.createFeatureService(mxd=mxd,title=reportTitle,share_everyone=everyone,share_org=orgs,
                                         share_groups=groups,thumbnail=thumbnail,folder_name=folderName,capabilities=capabilities,maxRecordCount=maxRecordCount)
    if 'error' in itemInfo:
        raise ValueError(str(itemInfo))
    if 'services' in itemInfo:
        return itemInfo['services'][0]
    else:
        raise ValueError(str(itemInfo))



def create_dashboard(webmap_id,config):
    publish_info = config['PublishingDetails']
    cred_info = publish_info['Credentials']
    app_info = publish_info['AppDetails']

   # AGOL Credentials
    username= cred_info['Username']
    password = cred_info['Password']
    
    if cred_info.has_key('Portal') == False:
        portal = ''
    else:
        portal = cred_info['Portal']
    
    agol = admin.AGOL(username=username,password=password, org_url=portal)

    #webmapdef_path = app_info['ItemJSON']
    delete_existing = False if app_info['UpdateItemContents'].upper() == "TRUE" else True

    name = ''
    tags = ''
    description = ''
    extent = ''


    name = app_info['Title']

    if app_info.has_key('DateTimeFormat'):
        loc_df = app_info['DateTimeFormat']
    else:
        loc_df = dateTimeFormat

    datestring = datetime.datetime.now().strftime(loc_df)
    name = name.replace('{DATE}',datestring)
    name = name.replace('{Date}',datestring)

    description = app_info['Description']
    tags = app_info['Tags']
    snippet = app_info['Summary']

    extent = app_info['Extent']

    everyone = app_info['ShareEveryone']
    orgs = app_info['ShareOrg']
    groups = app_info['Groups']  #Groups are by ID. Multiple groups comma separated

    folderName = app_info['Folder']
    thumbnail = app_info['Thumbnail']

    itemType = app_info['Type']
    typeKeywords = app_info['typeKeywords']

    item_info = agol.item(item_id =webmap_id)
    item_data= agol.itemData(item_id =webmap_id)
    mapGUID = get_guid()

    dashboard_data = {
        "addInIds": [],
        "interval": 30,
        "intervalType": "perLayer",
        "standaloneDataSources": [],
        "version": "1.2",
        "tabletLayout": {
            "mapWidget": mapGUID,
            "panels":  []
            } ,
         "widgets": []
        }

    dashboard_map_widget = {
        "caption": item_info['title'],
        "coordinateNotation": "esriLatLong",
        "featureActions": [],
        "id": mapGUID,
        "mapId": webmap_id,
        "dataSources":[],
        "showCoordinates": False,
        "showFeaturePopups": True,
        "type": "mapWidget"
     }

    if 'operationalLayers' in item_data:
        for opLayer in item_data['operationalLayers']:
            layerGUID = get_guid()
            widgetGUID = get_guid()

            dashboard_map_datasource = {
                "autoUpdate": False,
                "id": layerGUID,
                "layerId": opLayer['id'],
                "mapId": mapGUID,
                "name": opLayer['title'],
                "type": "featureLayerDataSource"
            }

            dashboard_feature_widget = {
                "caption": opLayer['title'],
                "coordinateNotation": "esriLatLong",
                "dataSourceId": layerGUID,
                "featureActions": [],
                "id": widgetGUID,
                "showCoordinates": False,
                "type": "featureDetailsWidget"
            }
            panel = {
                "layoutType": "panelTypeFullPage",
                "widgets": [
                     widgetGUID
                ]
            }
            dashboard_map_widget['dataSources'].append(dashboard_map_datasource)

            dashboard_data['widgets'].append(dashboard_feature_widget)
            dashboard_data['tabletLayout']['panels'].insert(0,panel)



    dashboard_data['widgets'].append(dashboard_map_widget)


    itemID = agol.publishItem(name=name,tags=tags,snippet=snippet,description=description,extent=extent,
                               data=dashboard_data,thumbnail=thumbnail,share_everyone=everyone,share_org=orgs,share_groups=groups,
                               item_type=itemType,typeKeywords=typeKeywords,folder_name=folderName,delete_existing=delete_existing)

    itemInfo =  {"ItemID" : itemID, "Name" : name}

    if not 'error' in itemInfo:
        print _("            %s webmap created" % itemInfo['Name'])
        return {"MapInfo":itemInfo}

    else:
        print str(itemInfo)


def combineWebMaps(webmaps,config):
    publish_info = config['PublishingDetails']
    cred_info = publish_info['Credentials']
    if publish_info.has_key('CombinedMapDetails'):
        maps = publish_info['CombinedMapDetails']
    elif publish_info.has_key('MapDetails'):
        maps = publish_info['MapDetails']
        
   # AGOL Credentials
    username= cred_info['Username']
    password = cred_info['Password']
    if cred_info.has_key('Portal') == False:
        portal = ''
    else:
        portal = cred_info['Portal']    

    agol = admin.AGOL(username=username,password=password, org_url=portal)

    for map_info in maps:
        webmapdef_path = map_info['ItemJSON']
        delete_existing = False if map_info['UpdateItemContents'].upper() == "TRUE" else True
    
        with open(webmapdef_path) as json_data:
            try:
                webmap_data = json.load(json_data)
            except:
                raise ValueError("%s is not a valid JSON File"%webmapdef_path)
        combinedLayers = []
        for webmap in webmaps:
            data = agol.itemData(webmap)
            if 'operationalLayers' in data:
                opLays = []
                for opLayer in data['operationalLayers']:
                    opLays.append(opLayer)
                opLays.extend(combinedLayers)
                combinedLayers = opLays
        webmap_data['operationalLayers'] = combinedLayers
    
        name = ''
        tags = ''
        description = ''
        extent = ''
    
    
        name = map_info['Title']
    
        if map_info.has_key('DateTimeFormat'):
            loc_df = map_info['DateTimeFormat']
        else:
            loc_df = dateTimeFormat
    
    
        datestring = datetime.datetime.now().strftime(loc_df)
        name = name.replace('{DATE}', datestring)
        name = name.replace('{Date}', datestring)
    
        description = map_info['Description']
        tags = map_info['Tags']
        snippet = map_info['Summary']
    
        extent = map_info['Extent']
    
        everyone = map_info['ShareEveryone']
        orgs = map_info['ShareOrg']
        groups = map_info['Groups']  #Groups are by ID. Multiple groups comma separated
    
        folderName = map_info['Folder']
        thumbnail = map_info['Thumbnail']
    
        itemType = map_info['Type']
        typeKeywords = map_info['typeKeywords']
    
    
        itemID = agol.publishItem(name=name,tags=tags,snippet=snippet,description=description,extent=extent,
                                   data=webmap_data,thumbnail=thumbnail,share_everyone=everyone,share_org=orgs,share_groups=groups,
                                   item_type=itemType,typeKeywords=typeKeywords,folder_name=folderName,delete_existing=delete_existing)
    
        itemInfo =  {"ItemID" : itemID, "Name" : name}
    
        if not 'error' in itemInfo:
            print _("            %s webmap created" % itemInfo['Name'])
            return {"MapInfo":itemInfo}
    
        else:
            print str(itemInfo)
def getLayerIndex(url):
    urlInfo = urlparse(url)
    urlSplit = str(urlInfo.path).split('/')
    inx = urlSplit[len(urlSplit)-1]

    if is_number(inx):
        return int(inx);
def getLayerName(url):
    urlInfo = urlparse(url)
    urlSplit = str(urlInfo.path).split('/')
    name = urlSplit[len(urlSplit)-3]
    return name
def publishWebMapFromConfig(agol,config,replaceInfo=None):

    name = ''
    tags = ''
    description = ''
    extent = ''

    webmap_data = ''

    webmapdef_path = config['ItemJSON']
    update_service = config['UpdateService']
    delete_existing = False if config['UpdateItemContents'].upper() == "TRUE" else True

    with open(webmapdef_path) as json_data:
        try:
            webmap_data = json.load(json_data)
        except:
            raise ValueError("%s is not a valid JSON File" % webmapdef_path)
        
        for replaceItem in replaceInfo:
            if replaceItem['ReplaceType'] == 'Global':
                webmap_data = find_replace(webmap_data,replaceItem['SearchString'],replaceItem['ReplaceString'])
            elif replaceItem['ReplaceType'] == 'Layer':
                if webmap_data.has_key('tables'):
                    opLayers = webmap_data['tables']    
                    for opLayer in opLayers:
                        if replaceItem['SearchString'] in opLayer['url']:
        
                            opLayer['url'] = opLayer['url'].replace(replaceItem['SearchString'],replaceItem['ReplaceString'])
                            if replaceItem.has_key('ItemID'):
                                opLayer['itemId'] = replaceItem['ItemID']
                            else:
                                opLayer['itemId'] = None
                                #opLayer['itemId'] = get_guid()
        
                            if str(update_service).upper() == "TRUE" and opLayer['itemId'] != None:
                                layers = []
                                response = agol.itemData(replaceItem['ItemID'])
                                if 'layers' in response:
                                    layers = response['layers']
        
                                str(opLayer['url'] ).split("/")
                                layerIdx = getLayerIndex(opLayer['url'])
                                if opLayer.has_key("popupInfo"):
                                    updatedLayer = {"id" : layerIdx ,
                                                    "popupInfo" : opLayer["popupInfo"]
                                                    }
                                else:
                                    updatedLayer = {"id" : layerIdx}
                                   
                                updated = False
                                for layer in layers:
                                    if str(layer['id']) == str(layerIdx):
                                        layer = updatedLayer
                                        updated = True
                                if updated == False:
                                    layers.append(updatedLayer)
                                if len(layers):                                
                                    text = {
                                        "layers" :layers
                                    }
                    
                                    agol.updateItem(agol_id = replaceItem['ItemID'] , data = text,folder = replaceItem['ItemFolder'])                                
                                              
                opLayers = webmap_data['operationalLayers']    
                for opLayer in opLayers:
                    if replaceItem['SearchString'] in opLayer['url']:
    
                        opLayer['url'] = opLayer['url'].replace(replaceItem['SearchString'],replaceItem['ReplaceString'])
                        if replaceItem.has_key('ItemID'):
                            opLayer['itemId'] = replaceItem['ItemID']
                        else:
                            opLayer['itemId'] = None
                            #opLayer['itemId'] = get_guid()
    
                        if str(update_service).upper() == "TRUE" and opLayer['itemId'] != None:
                            layers = []
                            response = agol.itemData(replaceItem['ItemID'])
                            if 'layers' in response:
                                layers = response['layers']
    
                            str(opLayer['url'] ).split("/")
                            layerIdx = getLayerIndex(opLayer['url'])
                            if opLayer.has_key("popupInfo"):
                                updatedLayer = {"id" : layerIdx,
                                                "popupInfo" : opLayer["popupInfo"]
                                                }
                            else:
                                updatedLayer = {"id" : layerIdx}
                               
                            updated = False
                            for layer in layers:
                                if str(layer['id']) == str(layerIdx):
                                    layer = updatedLayer
                                    updated = True
                            if updated == False:
                                layers.append(updatedLayer)
                            if len(layers):                                
                                text = {
                                    "layers" :layers
                                }
                
                                agol.updateItem(agol_id = replaceItem['ItemID'] , data = text,folder = replaceItem['ItemFolder'])                                
               
        
        opLayers = webmap_data['operationalLayers']    
        for opLayer in opLayers:
            opLayer['id'] = getLayerName(url= opLayer['url']) + "_" + str(random_int_generator(maxrange = 9999))
        
        if webmap_data.has_key('tables'):
        
            opLayers = webmap_data['tables']    
            for opLayer in opLayers:
                opLayer['id'] = getLayerName(url= opLayer['url']) + "_" + str(random_int_generator(maxrange = 9999))
                
            
    name = config['Title']

    if config.has_key('DateTimeFormat'):
        loc_df = config['DateTimeFormat']
    else:
        loc_df = dateTimeFormat

    datestring = datetime.datetime.now().strftime(loc_df)
    name = name.replace('{DATE}',datestring)
    name = name.replace('{Date}',datestring)

    description = config['Description']
    tags = config['Tags']
    snippet = config['Summary']

    extent = config['Extent']

    everyone = config['ShareEveryone']
    orgs = config['ShareOrg']
    groups = config['Groups']  #Groups are by ID. Multiple groups comma separated

    folderName = config['Folder']
    thumbnail = config['Thumbnail']

    itemType = config['Type']
    typeKeywords = config['typeKeywords']


    itemID = agol.publishItem(name=name,tags=tags,snippet=snippet,description=description,extent=extent,
                               data=webmap_data,thumbnail=thumbnail,share_everyone=everyone,share_org=orgs,share_groups=groups,
                               item_type=itemType,typeKeywords=typeKeywords,folder_name=folderName,delete_existing=delete_existing)

    return {"ItemID" : itemID, "Name" : name}




def credHelper(config):
    savecred = False
    if config.has_key('Credentials'):
        if config['Credentials']['Username'] == "":
            username = raw_input(_("Please enter your Organization Username: "))
            config['Credentials']['Username'] = username.encode('base64')
            savecred = True
        else:
            username = config['Credentials']['Username']
            try:
                username = username.decode('base64')
            except:
                pass
        if config['Credentials']['Password'] == "":
            password = raw_input(_("please enter your Organization Password: "))
            config['Credentials']['Password'] = password.encode('base64')  
            savecred = True
        else:
            password = config['Credentials']['Password']
            try:
                password = password.decode('base64')
            except:
                pass    
        return config, username, password,savecred
        
import datetime
import json
import os
import Common
import arcpy
from arcpy import env
from copy import deepcopy

from dateutil.parser import parse

dateTimeFormat = '%Y-%m-%d %H:%M'

class ReportToolsError(Exception):
    """ raised when error occurs in utility module functions """
    pass
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

                report_msg.append(create_reclass_report(reporting_areas=reporting_areas,
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


    except ReportToolsError,e:
        line, filename, synerror = Common.trace()
        print "error on line: %s" % line
        print "error in file name: %s" % filename
        print "with error message: %s" % synerror
        print "Add. Error Message: %s" % e
        print datetime.datetime.now().strftime(dateTimeFormat)
        return False


    except arcpy.ExecuteError:

        line, filename, synerror = Common.trace()
        print "error on line: %s" % line
        print "error in file name: %s" % filename
        print "with error message: %s" % synerror
        print "ArcPy Error Message: %s" % arcpy.GetMessages(2)
        print datetime.datetime.now().strftime(dateTimeFormat)
        return False


    except:
        line, filename, synerror = Common.trace()
        print "error on line: %s" % line
        print "error in file name: %s" % filename
        print "with error message: %s" % synerror
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
        _tempTableName = Common.random_string_generator()
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
            
            print "      %s was created" % report_result
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

            print "      %s was created" % report_result

    except ReportToolsError,e:
        line, filename, synerror = Common.trace()
        print "error on line: %s" % line
        print "error in file name: %s" % filename
        print "with error message: %s" % synerror
        print "Add. Error Message: %s" % e
        print datetime.datetime.now().strftime(dateTimeFormat)


    except arcpy.ExecuteError:

        line, filename, synerror = Common.trace()
        print "error on line: %s" % line
        print "error in file name: %s" % filename
        print "with error message: %s" % synerror
        print "ArcPy Error Message: %s" % arcpy.GetMessages(2)
        print datetime.datetime.now().strftime(dateTimeFormat)


    except:
        line, filename, synerror = Common.trace()
        print "error on line: %s" % line
        print "error in file name: %s" % filename
        print "with error message: %s" % synerror
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
            print "      %s was created" % report_result
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

            print "      %s was created" % report_result

    except ReportToolsError,e:
        line, filename, synerror = Common.trace()
        print "error on line: %s" % line
        print "error in file name: %s" % filename
        print "with error message: %s" % synerror
        print "Add. Error Message: %s" % e
        print datetime.datetime.now().strftime(dateTimeFormat)


    except arcpy.ExecuteError:

        line, filename, synerror = Common.trace()
        print "error on line: %s" % line
        print "error in file name: %s" % filename
        print "with error message: %s" % synerror
        print "ArcPy Error Message: %s" % arcpy.GetMessages(2)
        print datetime.datetime.now().strftime(dateTimeFormat)


    except:
        line, filename, synerror = Common.trace()
        print "error on line: %s" % line
        print "error in file name: %s" % filename
        print "with error message: %s" % synerror
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
                print "      %s was created" % report_result



    except ReportToolsError,e:
        line, filename, synerror = Common.trace()
        print "error on line: %s" % line
        print "error in file name: %s" % filename
        print "with error message: %s" % synerror
        print "Add. Error Message: %s" % e
        print datetime.datetime.now().strftime(dateTimeFormat)


    except arcpy.ExecuteError:

        line, filename, synerror = Common.trace()
        print "error on line: %s" % line
        print "error in file name: %s" % filename
        print "with error message: %s" % synerror
        print "ArcPy Error Message: %s" % arcpy.GetMessages(2)
        print datetime.datetime.now().strftime(dateTimeFormat)


    except:
        line, filename, synerror = Common.trace()
        print "error on line: %s" % line
        print "error in file name: %s" % filename
        print "with error message: %s" % synerror
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
    
    _feature_data_layer = Common.random_string_generator()
    _join_table_copy = Common.random_string_generator()
    _joinedDataFull = os.path.join(_tempWorkspace, _join_table_copy)
    
    _pointsJoinedData = Common.random_string_generator()
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
    strOnlineTime = Common.online_time_to_string(Common.local_time_to_online(),dateTimeFormat)
                                                  
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

    _intersect = os.path.join(_tempWorkspace ,Common.random_string_generator())
    sumstats = os.path.join(_tempWorkspace ,Common.random_string_generator())

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

    _intersect = os.path.join(_tempWorkspace ,Common.random_string_generator())

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
                        try:
                            if val_fnd == True:
                                newRow = deepcopy(row)
                                newRow[len(flds) - 1] = field['FieldName']
                                newRows.append(newRow)
    
                            else:
                                row[len(flds) - 1] = field['FieldName']
                                val_fnd = True
                        except Exception, e:
                            print "       %s" % e                            
                except Exception, e:
                    print "       WARNING: %s is not valid" % str(sql_state)

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

    _freq = os.path.join(_tempWorkspace ,Common.random_string_generator())
    _pivot = os.path.join(_tempWorkspace ,Common.random_string_generator())

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


    _reportCopy = Common.random_string_generator()

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

    strOnlineTime = Common.online_time_to_string(Common.local_time_to_online(),dateTimeFormat)
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

    strOnlineTime = Common.online_time_to_string(Common.local_time_to_online(),dateTimeFormat)
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

    _reportCopy = Common.random_string_generator()

    _final_report = os.path.join(_tempWorkspace ,_reportCopy)

    # Process: Create a copy of the Reporting Areas for the summary info join
    arcpy.FeatureClassToFeatureClass_conversion(reporting_areas, _tempWorkspace, _reportCopy, "", reporting_areas_ID_field + ' "' + reporting_areas_ID_field + '" true true false 50 Text 0 0 ,First,#,' + reporting_areas +',' + reporting_areas_ID_field + ',-1,-1', "")

    # Process: Create a copy of the report layer
    arcpy.Copy_management(report_schema,report_result,"FeatureClass")

    appendString = report_ID_field + " \"\" true true false 80 string 0 0 ,First,#," + _final_report + "," + reporting_areas_ID_field + ",-1,-1;"

    arcpy.Append_management(_final_report,report_result, "NO_TEST",appendString, "")

    strOnlineTime = Common.online_time_to_string(Common.local_time_to_online(),dateTimeFormat)
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
        line, filename, synerror = Common.trace()
        raise ReportToolsError({
                    "function": "JoinAndCalc",
                    "line": line,
                    "filename":  filename,
                    "synerror": synerror,
                    "arcpyError": arcpy.GetMessages(2),
                                    }
                                    )
    except:
        line, filename, synerror = Common.trace()
        raise ReportToolsError({
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
        line, filename, synerror = Common.trace()
        raise ReportToolsError({
            "function": "FieldExist",
            "line": line,
            "filename":  filename,
            "synerror": synerror,
        }
                          )

def deleteFC(in_datasets):

    for in_data in in_datasets:
        try:
            if in_data is not None:
                if arcpy.Exists(dataset=in_data):
                    arcpy.Delete_management(in_data=in_data)
        except Exception:
            print "Unable to delete %s" % in_data



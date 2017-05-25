from __future__ import print_function
import os
import time
import datetime
import arcpy
import copy
from . import common as Common
from collections import defaultdict


def speedyIntersect(fcToSplit, splitFC, fieldsToAssign, countField,onlyKeepLargest, outputFC):
    #arcpy.AddMessage(time.ctime())
    startProcessing = time.time()
    arcpy.env.overwriteOutput = True
    tempWorkspace = arcpy.env.scratchGDB
    tempFCName = Common.random_string_generator()
    tempFC= os.path.join(tempWorkspace, tempFCName)


    #arcpy.AddMessage(time.ctime())
    #startProcessing = time.time()

    fc = splitByLayer(fcToSplit=fcToSplit,
                      splitFC=splitFC,
                      countField=countField,
                      onlyKeepLargest=onlyKeepLargest,
                      outputFC=tempFC)

    assignFieldsByIntersect(sourceFC=fc,
                            assignFC=splitFC,
                            fieldsToAssign=fieldsToAssign,
                            outputFC=outputFC)

    #stopProcessing = time.time()
    #arcpy.AddMessage("Time to process data = {} seconds; in minutes = {}".format(str(int(stopProcessing-startProcessing)), str(int((stopProcessing-startProcessing)/60))))

    #Common.deleteFC(in_datasets=[tempFC])
def assignFieldsByIntersect(sourceFC, assignFC, fieldsToAssign, outputFC):
    tempWorkspace = arcpy.env.scratchGDB

    assignFields = arcpy.ListFields(dataset=assignFC)
    assignFieldsNames = [f.name for f in assignFields]

    sourceFields = arcpy.ListFields(dataset=sourceFC)
    sourceFieldNames = [f.name for f in sourceFields]
    newFields = []

    fms = arcpy.FieldMappings()
    for fieldToAssign in fieldsToAssign:
        if fieldToAssign not in assignFieldsNames:
            raise ValueError("{0} does not exist in {1}".format(fieldToAssign,assignFC))
        outputField = fieldToAssign
        if fieldToAssign in sourceFieldNames + newFields:
            outputField = Common.uniqueFieldName(fieldToAssign, sourceFieldNames + newFields)

        newFields.append(outputField)

        fm = arcpy.FieldMap()
        fm.addInputField(assignFC, fieldToAssign)
        type_name = fm.outputField
        type_name.name = outputField
        fm.outputField = type_name
        fms.addFieldMap(fm)



    fieldmappings = arcpy.FieldMappings()
    #fieldmappings.addTable(assignFC)
    #fieldmappings.removeAll()
    fieldmappings.addTable(sourceFC)
    for fm in fms.fieldMappings:
        fieldmappings.addFieldMap(fm)

    outputLayer = arcpy.SpatialJoin_analysis(target_features=sourceFC,
                               join_features=assignFC,
                              out_feature_class=outputFC,
                              join_operation="JOIN_ONE_TO_ONE",
                              join_type="KEEP_COMMON",
                              field_mapping=fieldmappings,
                              match_option="HAVE_THEIR_CENTER_IN",
                              search_radius=None,
                              distance_field_name=None)[0]


    return outputLayer
def splitByLayer(fcToSplit, splitFC, countField, onlyKeepLargest, outputFC):
    desc = arcpy.Describe(fcToSplit)
    path, fileName = os.path.split(outputFC)

    shapeLengthFieldName =""
    if desc.shapeType == "Polygon":
        shapeLengthFieldName = desc.areaFieldName
        dimension = 4
        measure = "area"
    elif desc.shapeType == "Polyline":
        shapeLengthFieldName = desc.lengthFieldName
        dimension = 2
        measure = "length"
    else:
        arcpy.FeatureClassToFeatureClass_conversion(in_features=fcToSplit,
                                                      out_path=path,
                                                      out_name=fileName,
                                                      where_clause=None,
                                                      field_mapping=None,
                                                      config_keyword=None)
        return outputFC

    arcpy.CreateFeatureclass_management(out_path=path,
                                        out_name=fileName,
                                        geometry_type=desc.shapeType,
                                        template=fcToSplit,
                                        has_m=None,
                                        has_z=None,
                                        spatial_reference=desc.spatialReference,
                                        config_keyword=None,
                                        spatial_grid_1=None,
                                        spatial_grid_2=None,
                                        spatial_grid_3=None)
    fldsInput1 = [f.name for f in arcpy.ListFields(fcToSplit) if f.name not in (desc.shapeFieldName,desc.oidFieldName,shapeLengthFieldName)] + \
                 ["OID@","shape@"]

    iOID = -2
    iShape = -1
    iCountField = None
    fndField = None
    if countField is not None and countField in fldsInput1:
        for f in arcpy.ListFields(outputFC):
            if f.name == countField:
                fndField = f
                break
        if fndField is None:
            raise ValueError("Count field not found")
        if fndField.type != "Double" and fndField.type != "Single" and fndField.type != "Integer" and fndField.type != "SmallInteger":
            raise ValueError("Count is not numeric")
        iCountField = fldsInput1.index(countField)

    with arcpy.da.SearchCursor(splitFC, ["Shape@","OID@"],spatial_reference=desc.spatialReference) as scursor:
        reportingGeometries = {row[1]:row[0] for row in scursor}

    tempWorkspace = arcpy.env.scratchGDB
    tempFCName = Common.random_string_generator()
    tempFC= os.path.join(tempWorkspace, tempFCName)


    #Hide all fields to eliminate and Target_id, Join_FID conflicts
    target_fi = arcpy.FieldInfo()
    for field in desc.fields:
        target_fi.addField(field.name,field.name,'HIDDEN','NONE')

    source_fi = arcpy.FieldInfo()
    for field in arcpy.Describe(splitFC).fields:
        source_fi.addField(field.name,field.name,'HIDDEN','NONE')

    target_sj_no_fields = arcpy.MakeFeatureLayer_management(fcToSplit,"target_sj_no_fields",field_info=target_fi)
    join_sj_no_fields = arcpy.MakeFeatureLayer_management(splitFC,"join_sj_no_fields",field_info=source_fi)

    geoToLayerMap = arcpy.SpatialJoin_analysis(target_features=target_sj_no_fields,
                                       join_features=join_sj_no_fields,
                                      out_feature_class=tempFC,
                                      join_operation="JOIN_ONE_TO_MANY",
                                      join_type="KEEP_COMMON",
                                      field_mapping=None,
                                      match_option="INTERSECT",
                                      search_radius=None,
                                      distance_field_name=None)[0]

    ddict = defaultdict(list)

    with arcpy.da.SearchCursor(geoToLayerMap, ("TARGET_FID", "JOIN_FID")) as sCursor:
        for row in sCursor:
            ddict[row[0]].append(reportingGeometries[row[1]])

    layerToSplit = arcpy.MakeFeatureLayer_management(fcToSplit,"layerToSplit")
    result = arcpy.SelectLayerByLocation_management(layerToSplit, "CROSSED_BY_THE_OUTLINE_OF", splitFC)

    rowCount = int(arcpy.GetCount_management(layerToSplit)[0])
    j = 0
    rowsInserted = 0
    totalDif = 0
    with arcpy.da.SearchCursor(layerToSplit, fldsInput1) as scursor:
        with arcpy.da.InsertCursor(outputFC, fldsInput1) as icursor:

            for j,row in enumerate(scursor,1):
                newRows = []
                lens = []
                row = list(row)
                rowGeo = row[iShape]
                origLength =  getattr(rowGeo, measure)
                row[iShape] = None
                for geo in ddict[row[iOID]]:
                    newRow = copy.copy(row)
                    #if not row[iShape].disjoint(geo):
                    splitGeo = rowGeo.intersect(geo, dimension)

                    newRow[iShape] = splitGeo
                    splitLength = getattr(splitGeo, measure)
                    if iCountField is not None:
                        if row[iCountField] is not None and splitLength is not None and origLength is not None and origLength !=0:
                            newRow[iCountField] = float(row[iCountField]) * (float(splitLength) / float(origLength))
                        else:
                            pass
                    lens.append(float(splitLength))
                    #newRows.append(copy.copy(newRow))
                    newRows.append(newRow)
                if onlyKeepLargest == True:
                    result = icursor.insertRow(newRows[lens.index(max(lens))])
                    rowsInserted = rowsInserted + 1
                else:
                    newOIDS = []
                    for newRow in newRows:
                        result = icursor.insertRow(newRow)
                        newOIDS.append(str(result))
                        rowsInserted = rowsInserted + 1
                    #if rowsInserted % 250 == 0:
                        #print (rowsInserted)
                    dif = sum(lens) / origLength
                    if dif > 1.0001 or dif < .9999:
                        totalDif = totalDif + (origLength - sum(lens))
                        print ("Original Row ID: {3} and new features with OIDs of {0} combined count field did not add up to the original: new combined {1}, original {2}. \n This can be caused by self overlapping lines or data falling outside the split areas.  \n\tLayer: {4}".format(",".join(newOIDS),str(sum(lens)),str(origLength),row[iOID],desc.catalogPath))

    if totalDif > 0:
        print ("Total difference from source to results: {0}".format(totalDif))
    result = arcpy.SelectLayerByLocation_management(in_layer=layerToSplit,
                                                    selection_type="SWITCH_SELECTION")
    rowCount = int(arcpy.GetCount_management(layerToSplit)[0])
    if rowCount > 0:
        result = arcpy.Append_management(inputs=layerToSplit,
                                target=outputFC,
                                schema_type = "TEST",
                               field_mapping=None,
                               subtype=None)

    return outputFC


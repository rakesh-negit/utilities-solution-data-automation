from __future__ import print_function
import os
import time
import datetime
import arcpy
import copy
from . import common
from collections import defaultdict


def speedyIntersect(fcToSplit, splitFC, fieldsToAssign, countField, adjustCountOnSplit, onlyKeepLargest, outputFC):
    startProcessing = time.time()
    print("Starting speedy intersect")
    arcpy.env.overwriteOutput = True
    tempWorkspace = arcpy.env.scratchGDB
    tempFCName = common.random_string_generator()
    tempFC = os.path.join(tempWorkspace, tempFCName)

    fc = splitByLayer(fcToSplit=fcToSplit,
                      splitFC=splitFC,
                      countField=countField,
                      adjustCountOnSplit=adjustCountOnSplit,
                      onlyKeepLargest=onlyKeepLargest,
                      outputFC=tempFC)

    assignFieldsByIntersect(sourceFC=fc,
                            assignFC=splitFC,
                            fieldsToAssign=fieldsToAssign,
                            outputFC=outputFC)

    print(datetime.timedelta(seconds=time.time() - startProcessing))


def assignFieldsByIntersect(sourceFC, assignFC, fieldsToAssign, outputFC):
    assignFields = arcpy.ListFields(dataset=assignFC)
    assignFieldsNames = [f.name for f in assignFields]

    sourceFields = arcpy.ListFields(dataset=sourceFC)
    sourceFieldNames = [f.name for f in sourceFields]
    newFields = []

    fms = arcpy.FieldMappings()
    for fieldToAssign in fieldsToAssign:
        if fieldToAssign not in assignFieldsNames:
            raise ValueError("{0} does not exist in {1}".format(fieldToAssign, assignFC))
        outputField = fieldToAssign
        if fieldToAssign in sourceFieldNames + newFields:
            outputField = common.uniqueFieldName(fieldToAssign, sourceFieldNames + newFields)

        newFields.append(outputField)

        fm = arcpy.FieldMap()
        fm.addInputField(assignFC, fieldToAssign)
        type_name = fm.outputField
        type_name.name = outputField
        fm.outputField = type_name
        fms.addFieldMap(fm)

    fieldmappings = arcpy.FieldMappings()
    # fieldmappings.addTable(assignFC)
    # fieldmappings.removeAll()
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


def splitByLayer(fcToSplit, splitFC, countField, adjustCountOnSplit, onlyKeepLargest, outputFC):
    path, fileName = os.path.split(outputFC)
    arcpy.FeatureClassToFeatureClass_conversion(in_features=fcToSplit,
                                                out_path=path,
                                                out_name=fileName,
                                                where_clause=None,
                                                field_mapping=None,
                                                config_keyword=None)
    desc = arcpy.Describe(outputFC)

    if desc.shapeType == "Polygon":
        shapeLengthFieldName = desc.areaFieldName
        dimension = 4
        measure = "area"
    elif desc.shapeType == "Polyline":
        shapeLengthFieldName = desc.lengthFieldName
        dimension = 2
        measure = "length"
    else:
        return outputFC

    fldsInput1 = [f.name for f in arcpy.ListFields(outputFC) if
                  f.name not in (desc.shapeFieldName, desc.oidFieldName, shapeLengthFieldName)] + \
                 ["OID@", "shape@"]

    iOID = -2
    iShape = -1
    iCountField = None
    if countField in fldsInput1:
        iCountField = fldsInput1.index(countField)

    with arcpy.da.SearchCursor(splitFC, ["Shape@", "OID@"], spatial_reference=desc.spatialReference) as scursor:
        reportingGeometries = {row[1]: row[0] for row in scursor}

    tempWorkspace = arcpy.env.scratchGDB
    tempFCName = common.random_string_generator()
    tempFC = os.path.join(tempWorkspace, tempFCName)
    geoToLayerMap = arcpy.SpatialJoin_analysis(target_features=fcToSplit,
                                               join_features=splitFC,
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

    layerToSplit = arcpy.MakeFeatureLayer_management(outputFC, "layerToSplit")
    arcpy.SelectLayerByLocation_management(layerToSplit, "CROSSED_BY_THE_OUTLINE_OF", splitFC)

    rowCount = int(arcpy.GetCount_management(layerToSplit)[0])
    j = 0
    rowsInserted = 0
    with arcpy.da.SearchCursor(layerToSplit, fldsInput1) as scursor:
        with arcpy.da.InsertCursor(layerToSplit, fldsInput1) as icursor:

            for j, row in enumerate(scursor, 1):
                newRows = []
                lens = []
                row = list(row)
                rowGeo = row[iShape]
                origLength = getattr(rowGeo, measure)
                row[iShape] = None
                for geo in ddict[row[iOID]]:
                    newRow = copy.copy(row)
                    # if not row[iShape].disjoint(geo):
                    splitGeo = rowGeo.intersect(geo, dimension)

                    newRow[iShape] = splitGeo
                    splitLength = getattr(splitGeo, measure)
                    if iCountField is not None and adjustCountOnSplit:
                        if row[iCountField] is not None and splitLength is not None and origLength not in [None, 0]:
                            newRow[iCountField] = float(row[iCountField]) * (float(splitLength) / float(origLength))
                        else:
                            pass
                    lens.append(float(splitLength))
                    # newRows.append(copy.copy(newRow))
                    newRows.append(newRow)
                if onlyKeepLargest:
                    icursor.insertRow(newRows[lens.index(max(lens))])
                    rowsInserted += 1
                else:
                    newOIDS = []
                    for newRow in newRows:
                        result = icursor.insertRow(newRow)
                        newOIDS.append(str(result))
                        rowsInserted += 1

                    dif = sum(lens) / origLength
                    if dif > 1.001 or dif < .999:
                        print("Original Row ID: {3} and new features with OIDs of {0} combined count field did not "
                              "add up to the original: new combined {1}, original {2}. \n "
                              "This can be caused by self overlapping lines.".format(",".join(newOIDS), sum(lens),
                                                                                     origLength), row[iOID])
    # print (rowsInserted)
    descLayer = arcpy.Describe(layerToSplit)
    sel_count = len(descLayer.fidSet.split(";"))
    if sel_count > 0 and rowCount > 0 and rowsInserted > 0:
        arcpy.DeleteFeatures_management(in_features=layerToSplit)
    # Common.deleteFC(in_datasets=[tempFC])
    return outputFC

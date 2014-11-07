

dateTimeFormat = '%Y-%m-%d %H:%M'

import arcrest
from arcrest.agol import FeatureLayer
from arcrest.agol import FeatureService
import datetime
import json
import os
import Common

########################################################################
class resetTools():
    _username = None
    _password = None
    _org_url = None
    _proxy_url = None
    _proxy_port = None
    _token_url = None
    _securityHandler = None
    
    def __init__(self, 
                 username, 
                 password, 
                 org_url=None,
                 token_url = None,
                 proxy_url=None, 
                 proxy_port=None):
        
        """Constructor"""
        _org_url = org_url
        _username = username
        _password = password
        _proxy_url = proxy_url
        _proxy_port = proxy_port 
        _token_url = token_url
      
        if self._org_url is None or 'www.arcgis.com' in  self._org_url:    
            self._securityHandler = arcrest.AGOLTokenSecurityHandler(username=self._username, 
                                                              password=self._password, 
                                                              token_url=self._token_url, 
                                                              proxy_url=self._proxy_url, 
                                                              proxy_port=self._proxy_port)         
        else:
           
            self._securityHandler = arcrest.PortalTokenSecurityHandler(username=self._username, 
                                                              password=self._password, 
                                                              baseOrgUrl=self._org_url, 
                                                              proxy_url=self._proxy_url, 
                                                              proxy_port=self._proxy_port)            
        
   

    def removeUserData(self,users=None, allUsers=True):
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        portal = admin.portals(portalId='self')
        users = portal.users(start=1, num=100)
      
        for user in users['users']:
            print user['username']
            adminusercontent = admin.content.usercontent(username=user['username'])    
            
            userContent = admin.content.getUserContent(username=user['username'])
            for userItem in userContent['items']:

                print adminusercontent.deleteItems(items=userItem['id'])              
            if 'folders' in userContent:
                for userItem in userContent['folders']:
                    folderContent = admin.content.getUserContent(username=user['username'],folderId=userItem['id'])
                    for userItem in folderContent['items']:
                        print adminusercontent.deleteItems(items=userItem['id'])  
                        
                    print adminusercontent.deleteFolder(folderId=userItem['id'])
                                    
                    
    def removeUserGroups(self,users=None, allUsers=True):
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        userCommunity = admin.community
        
        
        portal = admin.portals(portalId='self')
        users = portal.users(start=1, num=100)
        groupAdmin = userCommunity.groups
        
        for user in users['users']:
            print "Loading groups for user: %s" % user['username']
            userCommData = userCommunity.getUserCommunity(username=user['username'])
            
            if 'groups' in userCommData:
                if len(userCommData['groups']) == 0:
                    print "No Groups Found"  
                else:
                    for group in userCommData['groups']:
                        if group['owner'] == user['username']:    
                            print groupAdmin.deleteGroup(groupID=group['id'])
            else:
                print "No Groups Found"    
            
    
        
########################################################################
class publishingtools():
    _username = None
    _password = None
    _org_url = None
    _proxy_url = None
    _proxy_port = None
    _token_url = None
    _securityHandler = None
    _valid = True
    _message = ""        
    #----------------------------------------------------------------------           
    def __init__(self, 
                 username, 
                 password, 
                 org_url=None,
                 token_url = None,
                 proxy_url=None, 
                 proxy_port=None):
        
        """Constructor"""
        self._org_url = org_url
        self._username = username
        self._password = password
        self._proxy_url = proxy_url
        self._proxy_port = proxy_port 
        self._token_url = token_url
      
        if self._org_url is None or 'www.arcgis.com' in  self._org_url:    
            self._securityHandler = arcrest.AGOLTokenSecurityHandler(username=self._username, 
                                                              password=self._password, 
                                                              token_url=self._token_url, 
                                                              proxy_url=self._proxy_url, 
                                                              proxy_port=self._proxy_port)         
        else:
           
            self._securityHandler = arcrest.PortalTokenSecurityHandler(username=self._username, 
                                                              password=self._password, 
                                                              baseOrgUrl=self._org_url, 
                                                              proxy_url=self._proxy_url, 
                                                              proxy_port=self._proxy_port)            
        

    #----------------------------------------------------------------------  
    @property
    def message(self):
        """ returns any messages """
        return self._message   
    #----------------------------------------------------------------------
    @property
    def valid(self):
        """ returns boolean wether handler is valid """
        return self._valid
    #----------------------------------------------------------------------        
    def publishMap(self,maps_info,fsInfo=None):
      
        map_results = []
        for map_info in maps_info:
            itemInfo = {}
            
            if map_info.has_key('ReplaceInfo'):
                replaceInfo = map_info['ReplaceInfo']
            else:
                replaceInfo = None
        
       
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
            
    
            if map_info.has_key('ReplaceTag'):
                               
                itemInfo = {"ReplaceTag":map_info['ReplaceTag'] }
            else:
                itemInfo = {"ReplaceTag":"{WebMap}" }
                
            itemInfo['MapInfo']  = self._publishMap( config=map_info,
                                               replaceInfo=replaceInfo)
            map_results.append(itemInfo)
            if not 'error' in itemInfo:
                print "            %s webmap created" % itemInfo['MapInfo']['Name']
            else:
                print "            " + str(resFS)
            
        return map_results
    
    #----------------------------------------------------------------------               
    def _publishMap(self,config,replaceInfo=None):
    
        name = ''
        tags = ''
        description = ''
        extent = ''
    
        webmap_data = ''
    
        webmapdef_path = config['ItemJSON']
        update_service = config['UpdateService']
        delete_existing = False if config['UpdateItemContents'].upper() == "TRUE" else True
    
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        #adminusercontent = admin.content.usercontent()     
        #userCommunity = admin.community       
        #userContent = admin.content.getUserContent()
        adminusercontent = admin.content.usercontent()   
    
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
                                    item = admin.content.item(itemId = replaceItem['ItemID'])
                                    response = item.itemData()
                                    if 'layers' in response:
                                        layers = response['layers']
            
                                    str(opLayer['url'] ).split("/")
                                  
                                    layerIdx = Common.getLayerIndex(url=opLayer['url'])
                                    if opLayer.has_key("popupInfo"):
                                        updatedLayer = {"id" : layerIdx ,
                                                        "popupInfo" : opLayer["popupInfo"]
                                                        }
                                    else:
                                        updatedLayer = None
                                       
                                    updated = False
                                    for layer in layers:
                                        if str(layer['id']) == str(layerIdx):
                                            layer = updatedLayer
                                            updated = True
                                    if updated == False and not updatedLayer is None:
                                        layers.append(updatedLayer)
                                    if len(layers):                                
                                        text = {
                                            "layers" :layers
                                        }
                                        
                                        itemParams = arcrest.manageorg.ItemParameter()
                                        itemParams.type = "Feature Service"
                                       
                                    
                                        updateResults = adminusercontent.updateItem(itemId = replaceItem['ItemID'],
                                                                    updateItemParameters=itemParams,
                                                                    folderId=replaceItem['ItemFolder'],
                                                                    text=json.dumps(text))       
                                        if 'error' in updateResults:
                                            print updateResults
                                                  
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
                                item = admin.content.item(itemId = replaceItem['ItemID'])
                                response = item.itemData()
                                if 'layers' in response:
                                    layers = response['layers']
        
                                str(opLayer['url'] ).split("/")
                                layerIdx = Common.getLayerIndex(url=opLayer['url'])
                                if opLayer.has_key("popupInfo"):
                                    updatedLayer = {"id" : layerIdx,
                                                    "popupInfo" : opLayer["popupInfo"]
                                                    }
                                else:
                                    updatedLayer = None
                                   
                                updated = False
                                for layer in layers:
                                    if str(layer['id']) == str(layerIdx):
                                        layer = updatedLayer
                                        updated = True
                                if updated == False and not updatedLayer is None:
                                    layers.append(updatedLayer)
                                if len(layers):                                
                                    text = {
                                        "layers" :layers
                                    }
                    
                                    itemParams = arcrest.manageorg.ItemParameter()
                                    itemParams.type = "Feature Service"
                                   
                                
                                    updateResults = adminusercontent.updateItem(itemId = replaceItem['ItemID'],
                                                                updateItemParameters=itemParams,
                                                                folderId=replaceItem['ItemFolder'],
                                                                text=json.dumps(text))                                           
                                    if 'error' in updateResults:
                                        print updateResults                                    
            
            opLayers = webmap_data['operationalLayers']    
            for opLayer in opLayers:
                opLayer['id'] = Common.getLayerName(url=opLayer['url']) + "_" + str(Common.random_int_generator(maxrange = 9999))
            
            if webmap_data.has_key('tables'):
            
                opLayers = webmap_data['tables']    
                for opLayer in opLayers:
                    opLayer['id'] = Common.getLayerName(url=opLayer['url']) + "_" + str(Common.random_int_generator(maxrange = 9999))
                    
                
                
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
        org = config['ShareOrg']
        groupNames = config['Groups']  #Groups are by ID. Multiple groups comma separated
    
        folderName = config['Folder']
        thumbnail = config['Thumbnail']
    
        itemType = config['Type']
        typeKeywords = config['typeKeywords']
    
        
        #itemID = agol.publishItem(name=name,tags=tags,snippet=snippet,description=description,extent=extent,
                                   #data=webmap_data,thumbnail=thumbnail,share_everyone=everyone,share_org=orgs,share_groups=groups,
                                   #item_type=itemType,typeKeywords=typeKeywords,folder_name=folderName,delete_existing=delete_existing)
    
        #return {"ItemID" : itemID, "Name" : name}

        if webmap_data is None:
            return None
        
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        
        
        itemParams = arcrest.manageorg.ItemParameter()
        itemParams.title = name
        itemParams.thumbnail = thumbnail
        itemParams.type = "Web Map"
        itemParams.overwrite = True
        itemParams.description = description
        itemParams.extent = extent
        itemParams.typeKeywords = typeKeywords
        
        adminusercontent = admin.content.usercontent()
        userCommunity = admin.community 
        userContent = admin.content.getUserContent()
        
        folderId = admin.content.getFolderID(name=folderName,userContent=userContent)
        if folderId is None:
            res = adminusercontent.createFolder(name=folderName)
            if 'success' in res:
                folderId = res['folder']['id']                 
            else:
                pass
       
        folderContent = admin.content.getUserContent(folderId=folderId)
            
        itemID = admin.content.getItemID(title=name,itemType='Web Map',userContent=folderContent)
        if not itemID is None:
            resultMap = adminusercontent.updateItem(itemId=itemID,
                                        updateItemParameters=itemParams,
                                        folderId=folderId,
                                        text=json.dumps(webmap_data))
         
        else:
            
            resultMap = adminusercontent.addItem( itemParameters=itemParams,
                    overwrite=True,
                    folder=folderId,
                    url=None,                    
                    relationshipType=None,
                    originItemId=None,
                    destinationItemId=None,
                    serviceProxyParams=None,
                    metadata=None,
                    text=json.dumps(webmap_data))
        
                            
        if not 'error' in resultMap:
                            
            group_ids = userCommunity.getGroupIDs(groupNames=groupNames)
            shareResults = adminusercontent.shareItems(items=resultMap['id'],
                                   groups=','.join(group_ids),
                                   everyone=everyone,
                                   org=org)
            updateParams = arcrest.manageorg.ItemParameter()             
            updateParams.title = name
            updateResults = adminusercontent.updateItem(itemId=resultMap['id'],
                                                        updateItemParameters=updateParams,
                                                        folderId=folderId)
            resultMap['folderId'] = folderId
            resultMap['Name'] = name
        return resultMap
            
           

    
    #----------------------------------------------------------------------           
    def publishFsFromMXD(self,fs_config):
        """
            publishs a feature service from a mxd
            Inputs:
                feature_service_config: Json file with list of feature service publishing details
            Output:
                feature service item information
                
        """            
     
        res = []    
        if isinstance(fs_config, list):
            for fs in fs_config:
                if fs.has_key('ReplaceTag'):
                    
                    resItm = {"ReplaceTag":fs['ReplaceTag'] }
                else:
                    resItm = {"ReplaceTag":"{FeatureService}" }
                    
                resItm['FSInfo'] =self._publishFSfromConfig(config=fs)
                res.append( resItm)
                
        else:
            if fs_config.has_key('ReplaceTag'):
                    
                resItm = {"ReplaceTag":fs_config['ReplaceTag'] }
            else:
                resItm = {"ReplaceTag":"{FeatureService}" }
                
            resItm['FSInfo'] =self._publishFSfromConfig(config=fs_config)
            res.append(resItm)
            
        for resFS in res:
            if not 'error' in resFS:
                if 'FSInfo' in resFS:
                    if 'serviceurl' in resFS['FSInfo']:
                        print "            %s created" % resFS['FSInfo']['serviceurl']
                    else:
                        print "            " + str(resFS)                    
                else:
                    print "            " + str(resFS)
            else:
                print "            " + str(resFS)
        return res
    
    #----------------------------------------------------------------------           
    def _publishFSfromConfig(self,config):
        
        # Report settings
        mxd = config['Mxd']
    
        # Service settings
        service_name = config['Title']
    
        everyone = config['ShareEveryone']
        org = config['ShareOrg']
        groupNames = config['Groups']  #Groups are by ID. Multiple groups comma separated
    
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
        
        service_name_safe = service_name.replace(' ','_')
        service_name_safe = service_name_safe.replace(':','-')
    
        if os.path.exists(path=mxd) == False:
            raise ValueError("MXD does not exit")
            
        sd_Info = arcrest.common.servicedef.MXDtoFeatureServiceDef(mxd_path=mxd, 
                                                             service_name=service_name_safe, 
                                                             tags=None, 
                                                             description=None, 
                                                             folder_name=None, 
                                                             capabilities=capabilities, 
                                                             maxRecordCount=maxRecordCount, 
                                                             server_type='MY_HOSTED_SERVICES')  
        
        if sd_Info is None:
            return
        
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        
        
        itemParams = arcrest.manageorg.ItemParameter()
        itemParams.title = service_name
        itemParams.thumbnail = thumbnail
        itemParams.type = "Service Definition"
        itemParams.overwrite = True
         
        adminusercontent = admin.content.usercontent()
        
        
        userCommunity = admin.community
         
        userContent = admin.content.getUserContent()
        
        folderId = admin.content.getFolderID(name=folderName,userContent=userContent)
        if folderId is None:
            res = adminusercontent.createFolder(name=folderName)
            if 'success' in res:
                folderId = res['folder']['id']                 
            else:
                pass
       
        #q = "title:\""+ service_name + "\"AND owner:\"" + self._securityHandler.username + "\" AND type:\"" + "Service Definition" + "\""
   
        #items = admin.query(q=q, bbox=None, start=1, num=10, sortField=None, 
                   #sortOrder="asc")
    
        #if items['total'] >= 1:   
            #pass
        folderContent = admin.content.getUserContent(folderId=folderId)
            
        itemID = admin.content.getItemID(title=service_name,itemType='Service Definition',userContent=folderContent)
        if not itemID is None:
            resultSD = adminusercontent.updateItem(itemId=itemID,
                                        updateItemParameters=itemParams,
                                        folderId=folderId,
                                        filePath=sd_Info['servicedef'])
         
        else:
            
            resultSD = adminusercontent.addItem( itemParameters=itemParams,
                    filePath=sd_Info['servicedef'],
                    overwrite=True,
                    folder=folderId,
                    url=None,
                    text=None,
                    relationshipType=None,
                    originItemId=None,
                    destinationItemId=None,
                    serviceProxyParams=None,
                    metadata=None)
        
                            
        if not 'error' in resultSD:
            publishParameters = arcrest.manageorg.PublishSDParmaeters(tags=sd_Info['tags'],overwrite='true')
            #itemID = admin.content.getItemID(title=service_name,itemType='Feature Service',userContent=folderContent)   
            #if not itemID is None:
                #delres=adminusercontent.deleteItems(items=itemID)  
            
            resultFS = adminusercontent.publishItem(
                fileType="serviceDefinition",
                itemId=resultSD['id'],
                publishParameters=publishParameters)                        
    
            if 'services' in resultFS:
                if len(resultFS['services']) > 0:
                    
                    status = adminusercontent.status(itemId=resultFS['services'][0]['serviceItemId'],
                                                     jobId=resultFS['services'][0]['jobId'],
                                                     jobType='publish')
                    while status['status'] == 'processing':
                        status = adminusercontent.status(itemId=resultFS['services'][0]['serviceItemId'],
                                                                             jobId=resultFS['services'][0]['jobId'],
                                                                             jobType='publish')                        
                    if status['status'] == 'completed':
                       
                        group_ids = userCommunity.getGroupIDs(groupNames=groupNames)
                        shareResults = adminusercontent.shareItems(items=resultFS['services'][0]['serviceItemId'],
                                               groups=','.join(group_ids),
                                               everyone=everyone,
                                               org=org)
                        updateParams = arcrest.manageorg.ItemParameter()             
                        updateParams.title = service_name
                        updateResults = adminusercontent.updateItem(itemId=resultFS['services'][0]['serviceItemId'],
                                                                    updateItemParameters=updateParams,
                                                                    folderId=folderId)
                        resultFS['services'][0]['folderId'] = folderId
                        return resultFS['services'][0]
                        
                    else:
                        return status
                else:
                    return resultFS                    
            else:
                return resultFS                
        else:
            return resultSD
    #----------------------------------------------------------------------        
    def publishApp(self,app_info,map_info=None):
      
        app_results = []
        for appDet in app_info:
            itemInfo = {}
            
            if appDet.has_key('ReplaceInfo'):
                replaceInfo = appDet['ReplaceInfo']
            else:
                replaceInfo = None
        
       
            if replaceInfo != None:
        
                for replaceItem in replaceInfo:
                    if replaceItem['ReplaceType'] == 'Map':
                        
                        for mapDet in map_info: 
                            if mapDet is not None and replaceItem['ReplaceString'] == mapDet['ReplaceTag']:
                                #replaceItem['ReplaceString'] = mapDet['MapInfo']['id']
                                replaceItem['ItemID'] = mapDet['MapInfo']['id']
                                replaceItem['ItemFolder'] = mapDet['MapInfo']['folderId']
                            elif replaceItem.has_key('ItemID'):
                                if replaceItem.has_key('ItemFolder') == False:
                
                                    itemId = replaceItem['ItemID']
                                    itemInfo =   item = admin.content.item(itemId=itemId)
                                    if 'owner' in itemInfo:
                                        if itemInfo['owner'] == username and 'ownerFolder' in itemInfo:
                                            replaceItem['ItemFolder'] = itemInfo['ownerFolder']
                                        else:
                                            replaceItem['ItemFolder'] = None
            
    
            if appDet.has_key('ReplaceTag'):
                               
                itemInfo = {"ReplaceTag":appDet['ReplaceTag'] }
            else:
                itemInfo = {"ReplaceTag":"{App}" }
                
            if appDet['Type'] == 'Web Mapping Application':
                itemInfo['AppInfo']  = self._publishApp(config=appDet,
                                                               replaceInfo=replaceInfo)                
            elif appDet['Type'] == 'Operations Dashboard':
                pass
            else:
                itemInfo['AppInfo']  = self._publishApp(config=appDet,
                                               replaceInfo=replaceInfo)            
            app_results.append(itemInfo)
            if not 'error' in itemInfo:
                print "            %s app created" % itemInfo['AppInfo']['Name']
            else:
                print "            " + str(resFS)
            
        return app_results
    
    #----------------------------------------------------------------------   
    def _publishApp(self, config, replaceInfo):
        name = ''
        tags = ''
        description = ''
        extent = ''
    
    
        itemJson = config['ItemJSON']
    
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        
        adminusercontent = admin.content.usercontent()   
        if os.path.exists(itemJson):
            with open(itemJson) as json_data:
                try:
                    itemData = json.load(json_data)
                except:
                    raise ValueError("%s is not a valid JSON File" % itemJson)
                
                for replaceItem in replaceInfo:
                    if replaceItem['ReplaceType'] == 'Map' and 'ItemID' in replaceItem:
                        if 'values' in itemData:
                            if 'webmap' in itemData['values']:
                                if itemData['values']['webmap'] == replaceItem['SearchString']:
                                    itemData['values']['webmap'] = replaceItem['ItemID']
                                    if 'folderId' in itemData:
                                        itemData['folderId'] = replaceItem['ItemFolder']
                    elif replaceItem['ReplaceType'] == 'Global':
                        itemData = Common.find_replace(itemData,replaceItem['SearchString'],replaceItem['ItemID'])
                        
        else:
            itemData = None
                        
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
    
        
        everyone = config['ShareEveryone']
        org = config['ShareOrg']
        groupNames = config['Groups']  #Groups are by ID. Multiple groups comma separated
    
        folderName = config['Folder']
        url = config['Url']
        thumbnail = config['Thumbnail']
    
        itemType = config['Type']
        typeKeywords = config['typeKeywords']
        
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        
        
        itemParams = arcrest.manageorg.ItemParameter()
        itemParams.title = name
        itemParams.thumbnail = thumbnail
        itemParams.type = itemType
        
        itemParams.overwrite = True
        itemParams.description = description
        
        itemParams.typeKeywords = typeKeywords
        
        adminusercontent = admin.content.usercontent()
        userCommunity = admin.community 
        userContent = admin.content.getUserContent()
        
        folderId = admin.content.getFolderID(name=folderName,userContent=userContent)
        if folderId is None:
            res = adminusercontent.createFolder(name=folderName)
            if 'success' in res:
                folderId = res['folder']['id']                 
            else:
                pass
       
        folderContent = admin.content.getUserContent(folderId=folderId)
            
        itemID = admin.content.getItemID(title=name,itemType=itemType,userContent=folderContent)
        if not itemID is None:
            resultApp = adminusercontent.updateItem(itemId=itemID,
                                        updateItemParameters=itemParams,
                                        folderId=folderId,
                                        text=json.dumps(itemData))
         
        else:
            
            resultApp = adminusercontent.addItem( itemParameters=itemParams,
                    folder=folderId,           
                    relationshipType=None,
                    originItemId=None,
                    destinationItemId=None,
                    serviceProxyParams=None,
                    metadata=None,
                    text=json.dumps(itemData))
        
                            
        if not 'error' in resultApp:
                            
            group_ids = userCommunity.getGroupIDs(groupNames=groupNames)
            shareResults = adminusercontent.shareItems(items=resultApp['id'],
                                   groups=','.join(group_ids),
                                   everyone=everyone,
                                   org=org)
            updateParams = arcrest.manageorg.ItemParameter()             
            updateParams.title = name
            url = url.replace("{AppID}",resultApp['id'])
            updateResults = adminusercontent.updateItem(itemId=resultApp['id'],
                                                        url=url,        
                                                        updateItemParameters=updateParams,
                                                        folderId=folderId)
            resultApp['folderId'] = folderId
            resultApp['Name'] = name
        return resultApp
            
           
    #----------------------------------------------------------------------
    def _publishDashboard(self,config, replaceInfo):
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
    
        layerIDSwitch = []
    
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
                                                layerIDSwitch.append({"OrigID":dataSource['layerId'],"NewID":layerNamesID[dataSource['name']] })                                          
                                                dataSource['layerId'] = layerNamesID[dataSource['name']]
                                          
                                
    
        configFileAsString = json.dumps(item_data)
        for repl in layerIDSwitch:
            configFileAsString.replace(repl['OrigID'],repl['NewID'])
    
        item_data = json.loads(configFileAsString)
    
    
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
########################################################################
class featureservicetools():
    def __init__(self, 
                 username=None, 
                 password=None, 
                 org_url=None,
                 token_url = None,
                 proxy_url=None, 
                 proxy_port=None):
        
        """Constructor"""
        self._org_url = org_url
        self._username = username
        self._password = password
        self._proxy_url = proxy_url
        self._proxy_port = proxy_port 
        self._token_url = token_url
        self._valid = True
        self._message = ""                
        if not username is None:
            if self._org_url is None or 'www.arcgis.com' in  self._org_url:    
                self._securityHandler = arcrest.AGOLTokenSecurityHandler(username=self._username, 
                                                                  password=self._password, 
                                                                  token_url=self._token_url, 
                                                                  proxy_url=self._proxy_url, 
                                                                  proxy_port=self._proxy_port)         
            else:
               
                self._securityHandler = arcrest.PortalTokenSecurityHandler(username=self._username, 
                                                                  password=self._password, 
                                                                  baseOrgUrl=self._org_url, 
                                                                  proxy_url=self._proxy_url, 
                                                                  proxy_port=self._proxy_port)            
        

        
    #----------------------------------------------------------------------  
    @property
    def message(self):
        """ returns any messages """
        return self._message   
    #----------------------------------------------------------------------
    @property
    def valid(self):
        """ returns boolean wether handler is valid """
        return self._valid
    #----------------------------------------------------------------------    
    def GetFeatureService(self,itemId,returnURLOnly=False):
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        if self._securityHandler.valid == False:
            self._valid = self._securityHandler.valid  
            self._message = self._securityHandler.message
            return None
        
            
        item = admin.content.item(itemId=itemId)
        if item.itemType == "Feature Service":
            if returnURLOnly:
                return item.url
            else:
                return FeatureService(
                   url=item.url,
                   securityHandler=self._securityHandler)          
        return None
    #----------------------------------------------------------------------    
    def GetLayerFromFeatureServiceByURL(self,url,layerName="",returnURLOnly=False):
        fs = FeatureService(
                url=url,
                securityHandler=self._securityHandler) 
         
        return self.GetLayerFromFeatureService(fs=fs,layerName=layerName,returnURLOnly=returnURLOnly)
         
    #----------------------------------------------------------------------  
    def GetLayerFromFeatureService(self,fs,layerName="",returnURLOnly=False):
    
        layers = fs.layers
        for layer in layers:
            if layer.name == layerName:
                if returnURLOnly:
                    return fs.url + '/' + str(layer.id)
                else:
                    return layer
            
            elif not layer.subLayers is None:
                for sublayer in layer.subLayers:
                    if sublayer == layerName:
                        return sublayer
        for table in fs.tables:
            if table.name == layerName:
                if returnURLOnly:
                    return fs.url + '/' + str(layer.id)
                else:
                    return table            
        return None
            
    #---------------------------------------------------------------------- 
    def AddFeaturesToFeatureLayer(self,url,pathToFeatureClass):
        
        fl = FeatureLayer(
               url=url,
               securityHandler=self._securityHandler) 
        return fl.addFeatures(fc=pathToFeatureClass)
        
    #---------------------------------------------------------------------- 
    def DeleteFeaturesFromFeatureLayer(self,url,sql):
            
        fl = FeatureLayer(
               url=url,
               securityHandler=self._securityHandler) 
        return fl.deleteFeatures(where=sql)
            
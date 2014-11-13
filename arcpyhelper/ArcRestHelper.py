

dateTimeFormat = '%Y-%m-%d %H:%M'

import arcrest
from arcrest.agol import FeatureLayer
from arcrest.agol import FeatureService
from arcrest.hostedservice import AdminFeatureService
import datetime
import json
import os
import Common

########################################################################
class orgTools():
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
                                                                  orgUrl=self._org_url, 
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
    def shareItemsToGroup(self,shareToGroupName,items=None,groups=None):
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
    
        userCommunity = admin.community 
        group_ids = userCommunity.getGroupIDs(groupNames=shareToGroupName)
        results = []
        if not items is None:
            for item in items:        
                item = admin.content.item(itemId = item)
                res = item.shareItem(",".join(group_ids),everyone=False,org=False)
                if 'error' in res:
                    print res
                else:
                    print "%s shared with %s" % (item.title,shareToGroupName)
                results.append(res)
        if not groups is None:
            for group in groups:
                groupContent = admin.content.groupContent(groupId=group)
                for result in groupContent['items']:
                    item = admin.content.item(itemId = result['id'])
                    res = item.shareItem(",".join(group_ids),everyone=False,org=False)
                    if 'error' in res:
                        print res
                    else:
                        print "%s shared with %s" % (result['title'],shareToGroupName)
                    results.append(res)  
     
    #----------------------------------------------------------------------    
    def createGroup(self,
                    title,
                    tags,
                    description="",
                    snippet="",
                    phone="",
                    access="org", sortField="title",
                    sortOrder="asc", isViewOnly=False,
                    isInvitationOnly=False, thumbnail=None):
        
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        userCommunity = admin.community
        return userCommunity.createGroup(title=title,
                    tags=tags,
                    description=description,
                    snippet=snippet,
                    phone=phone,
                    access=access,
                    sortField=sortField,
                    sortOrder=sortOrder, 
                    isViewOnly=isViewOnly,
                    isInvitationOnly=isInvitationOnly, 
                    thumbnail=thumbnail)
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
            self._securityHandler = arcrest.AGOLTokenSecurityHandler(username=username, 
                                                              password=password, 
                                                              token_url=token_url, 
                                                              proxy_url=proxy_url, 
                                                              proxy_port=proxy_port)  
           
        else:
           
            self._securityHandler = arcrest.PortalTokenSecurityHandler(username=username, 
                                                              password=password, 
                                                              baseOrgUrl=org_url, 
                                                              proxy_url=proxy_url, 
                                                              proxy_port=proxy_port)            
        
   

    def removeUserData(self,users=None):
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        portal = admin.portals(portalId='self')
        users = portal.users(start=1, num=100)
        if users is None:
            users = portal.users(start=1, num=100)
              
              
        if users:              
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
                                        
                    
    def removeUserGroups(self,users=None):
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        userCommunity = admin.community
        
        
        portal = admin.portals(portalId='self')
        if users is None:
            users = portal.users(start=1, num=100)
        
        groupAdmin = userCommunity.groups
        if users:        
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
                
            itemInfo['MapInfo']  = self._publishMap(config=map_info,
                                               replaceInfo=replaceInfo)
            map_results.append(itemInfo)
            if not 'error' in itemInfo['MapInfo']['Results']:
                print "            %s webmap created" % itemInfo['MapInfo']['Name']
            else:
                print "            " + str(resFS)
            
        return map_results
    
    #----------------------------------------------------------------------               
    def _publishMap(self,config,replaceInfo=None,operationalLayers=None,tableLayers=None):
    
        name = ''
        tags = ''
        description = ''
        extent = ''
    
        webmap_data = ''
    
        webmapdef_path = config['ItemJSON']
        update_service = config['UpdateService']
     
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        #adminusercontent = admin.content.usercontent()     
        #userCommunity = admin.community       
        #userContent = admin.content.getUserContent()
        adminusercontent = admin.content.usercontent()   
        resultMap = {'Layers':[],'Tables':[],'Results':None}
        with open(webmapdef_path) as json_data:
            try:
                webmap_data = json.load(json_data)
            except:
                raise ValueError("%s is not a valid JSON File" % webmapdef_path)
            if operationalLayers:
                webmap_data['operationalLayers'] = operationalLayers
            if tableLayers:
                webmap_data['tables'] = tableLayers                
            if replaceInfo:          
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
                resultMap['Layers'].append({"Name":opLayer['title'],"ID":opLayer['id']})
                
                
            if webmap_data.has_key('tables'):
            
                opLayers = webmap_data['tables']    
                for opLayer in opLayers:
                    opLayer['id'] = Common.getLayerName(url=opLayer['url']) + "_" + str(Common.random_int_generator(maxrange = 9999))
                    resultMap['Tables'].append({"Name":opLayer['title'],"ID":opLayer['id']})
                
                
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
            resultMap['Results'] = adminusercontent.updateItem(itemId=itemID,
                                        updateItemParameters=itemParams,
                                        folderId=folderId,
                                        text=json.dumps(webmap_data))
         
        else:
            
            resultMap['Results'] = adminusercontent.addItem( itemParameters=itemParams,
                    overwrite=True,
                    folder=folderId,
                    url=None,                    
                    relationshipType=None,
                    originItemId=None,
                    destinationItemId=None,
                    serviceProxyParams=None,
                    metadata=None,
                    text=json.dumps(webmap_data))
        
                            
        if not 'error' in resultMap['Results']:
                            
            group_ids = userCommunity.getGroupIDs(groupNames=groupNames)
            shareResults = adminusercontent.shareItems(items=resultMap['Results']['id'],
                                   groups=','.join(group_ids),
                                   everyone=everyone,
                                   org=org)
            updateParams = arcrest.manageorg.ItemParameter()             
            updateParams.title = name
            updateResults = adminusercontent.updateItem(itemId=resultMap['Results']['id'],
                                                        updateItemParameters=updateParams,
                                                        folderId=folderId)
            resultMap['folderId'] = folderId
            resultMap['Name'] = name
        return resultMap
            
           

    
    #----------------------------------------------------------------------     
    def publishCombinedWebMap(self,maps_info,webmaps):
        
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        
        map_results = []
        for map_info in maps_info:
           
            operationalLayers = []
            tableLayers = []
            for webmap in webmaps:
                item = admin.content.item(itemId=webmap)
                response = item.itemData()    
                if 'operationalLayers' in response:
                                             
                    opLays = []
                    for opLayer in response['operationalLayers']:
                        opLays.append(opLayer)
                    opLays.extend(operationalLayers)
                    operationalLayers = opLays
                if 'tables' in response:
                                            
                    tblLays = []
                    for tblLayer in response['tables']:
                        tblLays.append(tblLayer)
                    tblLays.extend(tableLayers)
                    tableLayers = tblLays            

            if map_info.has_key('ReplaceTag'):
                            
                itemInfo = {"ReplaceTag":map_info['ReplaceTag'] }
            else:
                itemInfo = {"ReplaceTag":"{WebMap}" }
            
            itemInfo['MapInfo'] = self._publishMap(config=map_info,
                                                                   replaceInfo=None,
                                                                   operationalLayers=operationalLayers,
                                                                   tableLayers=tableLayers)
                         
            map_results.append(itemInfo)        
            
            if not 'error' in itemInfo['MapInfo']['Results']:
                print "            %s webmap created" % itemInfo['MapInfo']['Name']
            else:
                print "            " + str(resFS)
        return map_results
        
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
        enableEditTracking = config['EnableEditTracking']
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
                        if enableEditTracking == True:
                            adminFS = AdminFeatureService(url=resultFS['services'][0]['serviceurl'], securityHandler=self._securityHandler)
                           
                            json_dict = {'editorTrackingInfo':{}}
                            json_dict['editorTrackingInfo']['allowOthersToDelete'] = True
                            json_dict['editorTrackingInfo']['allowOthersToUpdate'] = True
                            json_dict['editorTrackingInfo']['enableEditorTracking'] = True
                            json_dict['editorTrackingInfo']['enableOwnershipAccessControl'] = False
                            
                            enableResults = adminFS.updateDefinition(json_dict=json.dumps(json_dict))
                            if 'error' in enableResults:
                                resultFS['services'][0]['messages'] = enableResults
                                 
                            del adminFS
                            
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
                        
                    for mapDet in map_info: 
                        if mapDet.has_key('ReplaceTag'):
                            if mapDet is not None and replaceItem['ReplaceString'] == mapDet['ReplaceTag'] and replaceItem['ReplaceType'] == 'Map':
                                
                                replaceItem['ItemID'] = mapDet['MapInfo']['Results']['id']
                                replaceItem['ItemFolder'] = mapDet['MapInfo']['folderId']
                            elif mapDet is not None and replaceItem['ReplaceType'] == 'Layer':
                                repInfo = replaceItem['ReplaceString'].split("|")
                                if len(repInfo) == 2:
                                    if repInfo[0] == mapDet['ReplaceTag']:
                                        for lay in  mapDet['MapInfo']['Layers']:
                                            if lay["Name"] == repInfo[1]:
                                                replaceItem['ReplaceString'] = lay["ID"] 
                                    
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
            elif appDet['Type'] == 'Operation View':
                itemInfo['AppInfo']  = self._publishDashboard(config=appDet,
                                                               replaceInfo=replaceInfo)                
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
                    elif replaceItem['ReplaceType'] == 'Layer' and 'ReplaceString' in replaceItem:
                        itemData = Common.find_replace(itemData,replaceItem['SearchString'],replaceItem['ReplaceString'])
                      
                    elif replaceItem['ReplaceType'] == 'Global':
                        itemData = Common.find_replace(itemData,replaceItem['SearchString'],replaceItem['ReplaceString'])
                        
        else:
            print "%s does not exist." %itemJson
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
     
        tags = ''
        description = ''
        extent = ''
    
    
        itemJson = config['ItemJSON']
    
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        adminusercontent = admin.content.usercontent()   
         
        layerIDSwitch = []
         
        if os.path.exists(itemJson):
            with open(itemJson) as json_data:
                try:
                    itemData = json.load(json_data)
                except:
                    raise ValueError("%s is not a valid JSON File" % itemJson)
                
                for replaceItem in replaceInfo:
                    if replaceItem['ReplaceType'] == 'Global':
                        itemData = find_replace(itemData,replaceItem['SearchString'],replaceItem['ReplaceString'])
                    elif replaceItem['ReplaceType'] == 'Map' and 'ItemID' in replaceItem:
                        item = admin.content.item(itemId=replaceItem['ItemID'])
                        response = item.itemData()           
                
                        layerNamesID = {}
                        layerIDs =[]
                    
                        tableNamesID = {}
                        tableIDs =[]
                
                        if 'operationalLayers' in response:
                            for opLayer in response['operationalLayers']:
                                layerNamesID[opLayer['title']] = opLayer['id']
                                layerIDs.append(opLayer['id'])
                        if 'tables' in response:
                            for opLayer in response['tables']:
                                tableNamesID[opLayer['title']] = opLayer['id']
                                tableIDs.append(opLayer['id']) 
                        
                        widgets = itemData['widgets']
                        for widget in widgets:
                        
                            if widget.has_key('mapId'):
                                if replaceItem['SearchString'] == widget['mapId']:
                                    widget['mapId'] = replaceItem['ItemID']
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
                                              
                                    
    
        configFileAsString = json.dumps(itemData)
        for repl in layerIDSwitch:
            configFileAsString.replace(repl['OrigID'],repl['NewID'])
    
        itemData = json.loads(configFileAsString)
    
    
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
            updateResults = adminusercontent.updateItem(itemId=resultApp['id'],
                                                        updateItemParameters=updateParams,
                                                        folderId=folderId)
            resultApp['folderId'] = folderId
            resultApp['Name'] = name
        return resultApp
    
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
            
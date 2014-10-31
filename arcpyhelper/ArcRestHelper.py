

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
        
   
    def publishMap(self,maps_info,fsInfo=None):
      
        map_results = []
        for map_info in maps_info:
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
            
            itemInfo  = self._publishMap( config=map_info,
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
                                        
                                        itemParams = arcrest.manageorg.ItemParameter()
                                        itemParams.type = "Feature Service"
                                       
                                    
                                        updateResults = adminusercontent.updateItem(itemId = replaceItem['ItemID'],
                                                                    updateItemParameters=itemParams,
                                                                    folderId=replaceItem['ItemFolder'],
                                                                    text=text)                                                                   
                                                  
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
                    
                                    itemParams = arcrest.manageorg.ItemParameter()
                                    itemParams.type = "Feature Service"
                                   
                                
                                    updateResults = adminusercontent.updateItem(itemId = replaceItem['ItemID'],
                                                                updateItemParameters=itemParams,
                                                                folderId=replaceItem['ItemFolder'],
                                                                text=text )                                           
                   
            
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
                        print str(resFS)                    
                else:
                    print str(resFS)
            else:
                print str(resFS)
        return res
    
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

########################################################################
class featureservicetools():
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
        
 
    def GetFeatureService(self,itemId,returnURLOnly=False):
        admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        item = admin.content.item(itemId=itemId)
        if item.itemType == "Feature Service":
            if returnURLOnly:
                return item.url
            else:
                return FeatureService(
                   url=item.url,
                   securityHandler=self._securityHandler)          
        return None
    def GetLayerFromFeatureServiceByURL(self,url,layerName="",returnURLOnly=False):
        fs = FeatureService(
                url=url,
                securityHandler=self._securityHandler) 
         
        return self.GetLayerFromFeatureService(fs=fs,layerName=layerName,returnURLOnly=returnURLOnly)
         
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
        return None
            
    def AddFeaturesToFeatureLayer(self,url,pathToFeatureClass):
        #admin = arcrest.manageorg.Administration(securityHandler=self._securityHandler)
        
        fl = FeatureLayer(
               url=url,
               securityHandler=self._securityHandler) 
        fl.addFeatures(fc=pathToFeatureClass)
        pass

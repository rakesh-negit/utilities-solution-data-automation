

dateTimeFormat = '%Y-%m-%d %H:%M'

import arcrest
import datetime

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
        
    def publish_FS_config(self,fs_config):
        """
            publishs a feature service from a config file
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
            
        for res in resItm:
            if not 'error' in res:
        
                if 'serviceurl' in res:
                    print "            %s created" % res['serviceurl']
                
                else:
                    print str(res)
            else:
                print str(res)
        return resItm
    
    def _publishFSfromConfig(self,config):
        
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
        
        service_name_safe = service_name.replace(' ','_')
        service_name_safe = service_name_safe.replace(':','-')
    
      
        sd_Info = arcrest.common.servicedef.MXDtoFeatureServiceDef(mxd_path=mxd, 
                                                             service_name=service_name_safe, 
                                                             tags=None, 
                                                             description=None, 
                                                             folder_name=folderName, 
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
        userContent = admin.content.getUserContent()
        
        folderID = admin.content.getFolderID(name=folderName,userContent=userContent)
        if folderID is None:
            res = adminusercontent.createFolder(name=folderName)
            if 'success' in res:
                folderID = res['folder']['id']                 
            else:
                pass
        #   Add the Web Map
        #
        result = adminusercontent.addItem( itemParameters=itemParams,
                    filePath=sd_Info['servicedef'],
                    overwrite=True,
                    folder=folderID,
                    url=None,
                    text=None,
                    relationshipType=None,
                    originItemId=None,
                    destinationItemId=None,
                    serviceProxyParams=None,
                    metadata=None)
        if 'error' in result:
            if 'code' in result['error']:
                if result['error']['code'] == 409:
                    userContent = admin.content.getUserContent(folderId=folderID)
                    
                    itemID = admin.content.getItemID(name=service_name_safe,itemType='Service Definition',userContent=userContent)
                    if not itemID is None:
                        result = adminusercontent.deleteItems(itemID)
                        if 'success' in result:
                            result = adminusercontent.addItem( itemParameters=itemParams,
                                             filePath=sd_Info['servicedef'],
                                             overwrite=True,
                                             folder=folderID,
                                             url=None,
                                             text=None,
                                             relationshipType=None,
                                             originItemId=None,
                                             destinationItemId=None,
                                             serviceProxyParams=None,
                                             metadata=None)                    
                    pass#self.deleteItems(items)
            
        #service_url = ''
    
           #for service in itemInfo['services']:
               #if 'error' in service:
                   #raise ValueError(str(service))
               #item_id = service['serviceItemId']
               #service_url = service['serviceurl']
               #service['folderId'] = folderID
    
           #group_ids = self.get_group_IDs(share_groups)
    
           #errors = []
           #result = self.enableSharing(agol_id=item_id, everyone=share_everyone.lower()== "true" , orgs= share_org.lower()== "true", groups=','.join(group_ids),folder=folderID)
           #if 'error' in result:
               #errors.append(result['error'])
    
           #result = self.updateTitle(agol_id=item_id,title= service_name,folder=folderID)
           #if 'error' in result:
               #errors.append(result['error'])
    
           #if not thumbnail is None:
               #if os.path.isfile(thumbnail):
                   #if not os.path.isabs(thumbnail):
                       #thumbnail = os.path.abspath(thumbnail)
                   #result = self.updateThumbnail(agol_id=item_id,thumbnail=thumbnail,folder=folderID)
                   #if 'error' in result:
                       #errors.append(result['error'])
           #if len(errors)> 0:
    
               #itemInfo['errors'] =  errors
           #return itemInfo    
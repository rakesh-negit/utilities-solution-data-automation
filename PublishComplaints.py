import sys, os, datetime
from arcpy import env
from arcpyhelper import helper


log_file='./logs/CustomerComplaints.log'

configFiles=  ['./configs/CustomerComplaints.json']
globalLoginInfo = './configs/GlobalLoginInfo.json'
dateTimeFormat = '%Y-%m-%d %H:%M'

if __name__ == "__main__":    
    
    env.overwriteOutput = True
    
    helper.init_localization()
    
    log = helper.init_log(log_file=log_file)

    if log is None:
        print _("Log file could not be created")
    
    print _("********************Script Started********************")
    print datetime.datetime.now().strftime(dateTimeFormat)
    webmaps = []
    cred_info = None
    if os.path.isfile(globalLoginInfo):
        loginInfo = helper.init_config_json(config_file=globalLoginInfo)
        if 'Credentials' in loginInfo:
            cred_info = loginInfo['Credentials']
        
    for configFile in configFiles:
        
        config = helper.init_config_json(config_file=configFile)
        if config is not None:  
            print _("  ")
            
            print _("  ---------")
            print _("    Processing config %s" % configFile)
            if cred_info is not None:
                if 'PublishingDetails' in config:
                    config['PublishingDetails']['Credentials'] = cred_info
                        
            if helper.create_report_layers_using_config(config):
                if 'PublishingDetails' in config:
                    serv_update = helper.update_existing_service_from_config(config)
                    mapInfo =  helper.publish_service_map_from_config(config)
                    if mapInfo != None:
                        if 'MapInfo' in mapInfo:
                            if len(mapInfo['MapInfo']) > 0:
                                for webmap in mapInfo['MapInfo']:    
                                    if 'ItemID' in webmap:
                                        webmaps.append(webmap['ItemID'])
            print _("    Config %s completed" % configFile)
            print _("  ---------")
        
    
    print datetime.datetime.now().strftime(dateTimeFormat)
    
    
    print _("###############Script Completed#################")
    print ""
    if log is not None:
        log.close()
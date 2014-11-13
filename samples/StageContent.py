import sys, os, datetime
import csv
from arcpyhelper import ArcRestHelper
from arcpyhelper import Common


log_file='..//logs/CreateGroups.log'

configFiles=  ['..//configs/WaterGroups.json']
globalLoginInfo = '..//configs/___GlobalLoginInfo.json'

dateTimeFormat = '%Y-%m-%d %H:%M'

if __name__ == "__main__":
    log = Common.init_log(log_file=log_file)
 
    try:

        if log is None:
            print "Log file could not be created"

        print "********************Script Started********************"
        print datetime.datetime.now().strftime(dateTimeFormat)
        webmaps = []
        cred_info = None
        if os.path.isfile(globalLoginInfo):
            loginInfo = Common.init_config_json(config_file=globalLoginInfo)
            if 'Credentials' in loginInfo:
                cred_info = loginInfo['Credentials']
        if cred_info is None:
            print "Login info not found"
        else: 
            arh = ArcRestHelper.orgTools(username = cred_info['Username'], password=cred_info['Password'],org_url=cred_info['Orgurl'],
                                               token_url=None, 
                                               proxy_url=None, 
                                               proxy_port=None)
            
            if arh is None:
                print "Error: Security handler not created"
            else:
                print "Security handler created"
            
                for configFile in configFiles:
                 
                    config = Common.init_config_json(config_file=configFile)
                    if config is not None:
                       
                        print " "
                        print "    ---------"
                        print "        Processing config %s" % configFile

                        contentInfo = config['ContentItems']
                        for cont in contentInfo:
                            content = cont['Content']
                            group = cont['ShareToGroup']            
            
                            print "             Sharing content to: %s" % group
                            if os.path.isfile(content):
                                with open(content, 'rb') as csvfile:
                                    items = []
                                    groups = []
                                    for row in csv.DictReader(csvfile,dialect='excel'):
                                        if cont['Type'] == "Group":
                                            groups.append(row['id'])         
                                        elif cont['Type'] == "Items":
                                            items.append(row['id'])
                                    results = arh.shareItemsToGroup(shareToGroupName=group,items=items,groups=groups)

                        print "        Config %s completed" % configFile
                        print "    ---------"                                            
                    else:
                        print "Config %s not found" % configFile
                    
            
    except(TypeError,ValueError,AttributeError),e:
        print e
              
    finally:
        print datetime.datetime.now().strftime(dateTimeFormat)
        print "###############Script Completed#################"
        print ""
        if log is not None:
            log.close()
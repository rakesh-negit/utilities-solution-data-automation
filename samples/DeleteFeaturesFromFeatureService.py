"""
    @author: ArcGIS for Water Utilities
    @contact: ArcGISTeamUtilities@esri.com
    @company: Esri
    @version: 1.0.0
    @description: Used to stage the app in your organization.
    @requirements: Python 2.7.x, ArcGIS 10.2.1
    @copyright: Esri, 2014
"""

import sys, os, datetime
from arcpy import env
from arcpyhelper import ArcRestHelper
from arcpyhelper import Common

log_file='../logs/DeleteFeatureServiceData.log'
dateTimeFormat = '%Y-%m-%d %H:%M'
#globalLoginInfo = '../configs/GlobalLoginInfo.json'
configFiles = ['../configs/WaterServices.json','../configs/TelcoServices.json','../configs/ElectricServices.json','../configs/GasServices.json']

if __name__ == "__main__":
    env.overwriteOutput = True

    log = Common.init_log(log_file=log_file)

    try:

        if log is None:
            print "Log file could not be created"

        print "********************Script Started********************"
        print datetime.datetime.now().strftime(dateTimeFormat)
        #cred_info = None
        #if os.path.isfile(globalLoginInfo):
            #loginInfo = Common.init_config_json(config_file=globalLoginInfo)
            #if 'Credentials' in loginInfo:
                #cred_info = loginInfo['Credentials']
        
        arh = ArcRestHelper.featureservicetools(username =None, password=None,org_url=None,
                                                           token_url=None, 
                                                           proxy_url=None, 
                                                           proxy_port=None)
                        
        #arh = ArcRestHelper.featureservicetools(username = cred_info['Username'], password=cred_info['Password'],org_url=cred_info['Orgurl'],
                                                   #token_url=None, 
                                                   #proxy_url=None, 
                                                   #proxy_port=None)
                
        if arh is None:
            print "    Security handler not created"
        else:
            print "    Security handler created"        
            for configFile in configFiles:
          
                config = Common.init_config_json(config_file=configFile)
                if config is not None:
                    print " "
        
                    print "    ---------"
                    print "        Processing config %s" % configFile
                    if 'FeatureServices' in config:
                        for itm in config['FeatureServices']:
                            print "         " +  str(arh.DeleteFeaturesFromFeatureLayer(url=itm['url'], sql=itm['sql']))
                    else:
                        print "        Missing FeatureServices Section"
                    print "        Process Complate %s" % configFile
                    print "    ---------"
                    print " "
    except(TypeError,ValueError,AttributeError),e:
        print e
              
    finally:
        print datetime.datetime.now().strftime(dateTimeFormat)
        print "###############Script Completed#################"
        print ""
        if log is not None:
            log.close()
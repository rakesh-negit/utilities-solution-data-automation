import sys, io, os, datetime
import csv
from arcpyhelper import ArcRestHelper
from arcpyhelper import Common

import csv,json

log_file='..//logs/GroupReporter.log'

configFiles=  ['..//configs/WaterGroups.json']
globalLoginInfo = '..//configs/___GlobalLoginInfo.json'

dateTimeFormat = '%Y-%m-%d %H:%M'
def noneToString(value):
    if( value is None):
        return ""
    else:
        return value
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
                groupName = "Portland Water Conf"
                results = arh.getGroupContent(groupName=groupName)  
                groups=[]
                if 'results' in results:
                    file = io.open("groupReport.json", "w", encoding='utf-8')
                    #file.write(unicode("'Groups':["))
                    for result in results['results']:
                        thumbLocal = arh.getThumbnailForItem(itemId=result['id'],fileName=result['title'],filePath='C:\\temp')
                        result['thumbnail']=thumbLocal
                        groups.append(result)
                        #file.write(unicode(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))))
                    file.write(unicode(json.dumps(groups, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))))
                    
                    #file.write(unicode("]"))
                #if os.path.abspath(iconPath):
        
                    #sciptPath = os.getcwd()
        
                    #iconPath = os.path.join(sciptPath,iconPath)
        
                #for group in groups:
                    #image = Portal.group_thumbnaild(portal, group['id'],iconPath)
                    #print(image)
        
              
                file.close()                
                #with open('groupReport.csv', 'w') as csvfile:
                    #fieldnames = ['name','title','type','itemType','description','tags','snippet','thumbnail','extent','accessInformation','licenseInfo','itemData']
                    #writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval=None)
                
                    #writer.writeheader()
                    #for item in results:
                        #writer.writerow(item)
                            
                    
                #with open('groupReport.csv', 'wb') as csvfile:
                    #csvWriter = csv.writer(csvfile, delimiter=',',
                                            #quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    #csvWriter.writerow("name,title,type,itemType,description,tags,snippet,thumbnail,extent,accessInformation,licenseInfo,itemData")
                    #for item in results:
                                     
                        #csvLine = noneToString(item.name) + ","
                        #csvLine = csvLine + noneToString(item.title) + ","
                        #csvLine = csvLine + noneToString(item.type) + ","
                        #csvLine = csvLine + noneToString(item.itemType) + ","
                        #csvLine = csvLine + noneToString(item.description) + ","
                        #csvLine = csvLine + noneToString(item.tags) + ","
                        #csvLine = csvLine + noneToString(item.snippet) + ","
                        #csvLine = csvLine + noneToString(item.thumbnail) + ","
                        #csvLine = csvLine + noneToString(item.extent) + ","
                        #csvLine = csvLine + noneToString(item.accessInformation) + ","
                        #csvLine = csvLine + noneToString(item.licenseInfo) + ","
                        #csvLine = csvLine + noneToString(item.itemData)                    
                        #csvWriter.writerow(csvLine)                
              
                #file = io.open("groupReport.csv", "w", encoding='utf-8')
                #file.write("name,title,type,itemType,description,tags,snippet,thumbnail,extent,accessInformation,licenseInfo,itemData")
                #for item in results:
                    
                    #csvLine = item.name + ","
                    #csvLine = csvLine + item.title + ","
                    #csvLine = csvLine + item.type + ","
                    #csvLine = csvLine + item.itemType + ","
                    #csvLine = csvLine + item.description + ","
                    #csvLine = csvLine + item.tags + ","
                    #csvLine = csvLine + item.snippet + ","
                    #csvLine = csvLine + item.thumbnail + ","
                    #csvLine = csvLine + item.extent + ","
                    #csvLine = csvLine + item.accessInformation + ","
                    #csvLine = csvLine + item.licenseInfo + ","
                    #csvLine = csvLine + item.itemData + ","
                    #file.write(csvLine)
                #file.close()              
                #for configFile in configFiles:
        
                    #config = Common.init_config_json(config_file=configFile)
                    #if config is not None:
                       
                        #print " "
                        #print "    ---------"
                        #print "        Processing config %s" % configFile

                        #print "        Config %s completed" % configFile
                        #print "    ---------"                                            
                    #else:
                        #print "Config %s not found" % configFile
                    
            
    except(TypeError,ValueError,AttributeError),e:
        print e
    except(ArcRestHelper.ArcRestHelperError),e:
        print e              
    finally:
        print datetime.datetime.now().strftime(dateTimeFormat)
        print "###############Script Completed#################"
        print ""
        if log is not None:
            log.close()
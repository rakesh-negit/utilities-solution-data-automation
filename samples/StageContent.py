import sys, os, datetime
from arcpy import env
from arcpyhelper import helper
import csv


from arcrest.agol import admin

log_file='./logs/StageContent.log'

configFiles=  ['./configs/config.json']

dateTimeFormat = '%Y-%m-%d %H:%M'

if __name__ == "__main__":

    helper.init_localization()

    log = helper.init_log(log_file=log_file)

    if log is None:
        print _("Log file could not be created")

    print _("********************Script Started********************")
    print datetime.datetime.now().strftime(dateTimeFormat)
    for configFile in configFiles:

        config = helper.init_config_json(config_file=configFile)
        if config is not None:
            print _("  ")
            print _("  ---------")
            print _("    Processing config %s" % configFile)
            cred_info = config['Credentials']
            contentInfo = config['ContentItems']
            username= cred_info['Username']
            password = cred_info['Password']
            portal = cred_info['Portal']
            agol = admin.AGOL(username=username,password=password,org_url=portal)

            for cont in contentInfo:
                content = cont['Content']
                group = cont['ShareToGroup']
                print _("    Sharing content to: %s" % group)
                if os.path.isfile(content):
                    with open(content, 'rb') as csvfile:

                        agol_groups = agol.get_group_IDs(group)
                        if len(agol_groups) == 0:
                            print "      %s Could not be located in the specified org" % group
                        else:
                            agol_groups = ",".join(agol_groups)
                            #Disaster
                            for row in csv.DictReader(csvfile,dialect='excel'):
                                if cont['Type'] == "Group":
                                    grp_content = agol.get_group_content(row['id'])

                                    print "      %s Items in %s" % (len(grp_content['results']), row['id'])
                                    for result in grp_content['results']:
                                       print agol.enableSharing(result['id'], everyone='false', orgs='true', groups=agol_groups)
                                elif cont['Type'] == "Items":

                                    print agol.enableSharing(row['id'], everyone='false', orgs='true', groups=agol_groups)

            print _("  ---------")

    print datetime.datetime.now().strftime(dateTimeFormat)


    print _("###############Script Completed#################")
    print ""
    if log is not None:
        log.close()
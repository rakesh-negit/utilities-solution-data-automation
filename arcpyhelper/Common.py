import os

import json
import inspect
import random
import string
import datetime
from urlparse import urlparse

def getLayerIndex(url):
    urlInfo = urlparse(url)
    urlSplit = str(urlInfo.path).split('/')
    inx = urlSplit[len(urlSplit)-1]

    if is_number(inx):
        return int(inx)
    
def getLayerName(url):
    urlInfo = urlparse(url)
    urlSplit = str(urlInfo.path).split('/')
    name = urlSplit[len(urlSplit)-3]
    return name   

def random_string_generator(size=6, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

def random_int_generator(maxrange):
    return random.randint(0,maxrange)

def local_time_to_online(dt=None):
    """
       converts datetime object to a UTC timestamp for AGOL
       Inputs:
          dt - datetime object
       Output:
          Long value
    """
    if dt is None:
        dt = datetime.datetime.now()

    is_dst = time.daylight > 0 and time.localtime().tm_isdst > 0
    utc_offset =  (time.altzone if is_dst else time.timezone)

    return (time.mktime(dt.timetuple()) * 1000) + (utc_offset * 1000)

def online_time_to_string(value,timeFormat):
    """
       Converts a timestamp to date/time string
       Inputs:
          value - timestamp as long
          timeFormat - output date/time format
       Output:
          string
    """
    return datetime.datetime.fromtimestamp(value /1000).strftime(timeFormat)
#----------------------------------------------------------------------
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False
#----------------------------------------------------------------------
def init_config_json(config_file):
    if os.path.exists(config_file):
        #Load the config file
        
        with open(config_file) as json_file:
            json_data = json.load(json_file)
            return unicode_convert( json_data)
    else:
        return None
#----------------------------------------------------------------------
def write_config_json(config_file, data):
    with open(config_file, 'w') as outfile:
        json.dump(data, outfile)  
      
#----------------------------------------------------------------------
def unicode_convert(obj):
    try:    
        """ converts unicode to anscii """
        
        if isinstance(obj, dict):
            return {unicode_convert(key): unicode_convert(value) for key, value in obj.iteritems()}
        elif isinstance(obj, list):
            return [unicode_convert(element) for element in obj]
        elif isinstance(obj, unicode):
            return obj.encode('utf-8')
        else:
            return obj
    except:
        return obj
def find_replace_string(obj,find,replace):
    
    obj = str(obj)
    return string.replace(obj,find, replace)

def find_replace(obj,find,replace):
    """ searchs an object and does a find and replace """
    if isinstance(obj, dict):
        return {find_replace(key,find,replace): find_replace(value,find,replace) for key, value in obj.iteritems()}
    elif isinstance(obj, list):
        return [find_replace(element,find,replace) for element in obj]
    elif obj == find:
        return unicode_convert(replace)
    else:
        try:
            return unicode_convert(find_replace_string(obj, find, replace))
            #obj = unicode_convert(json.loads(obj))
            #return find_replace(obj,find,replace)
        except:    
            return unicode_convert(obj)
#----------------------------------------------------------------------
def init_log(log_file,):

    #Create the log file
    log = None
    try:
        log = open(log_file, 'a')

        #Change the output to both the windows and log file
        #original = sys.stdout
        sys.stdout = Tee(sys.stdout, log)
    except Exception:
        pass
    return log


#----------------------------------------------------------------------
def init_localization():
    '''prepare l10n'''
    locale.setlocale(locale.LC_ALL, '') # use user's preferred locale
    # take first two characters of country code
    filename = "res/messages_%s.mo" % locale.getlocale()[0][0:2]

    try:
        #print( "Opening message file %s for locale %s") % (filename, loc[0])
        trans = gettext.GNUTranslations(open( filename, "rb" ) )
    except IOError:
        #print( "Locale not found. Using default messages" )
        trans = gettext.NullTranslations()

    trans.install()

#----------------------------------------------------------------------
def trace():
    """
        trace finds the line, the filename
        and error message and returns it
        to the user
    """
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    filename = inspect.getfile( inspect.currentframe() )
    # script name + line number
    line = tbinfo.split(", ")[1]
    # Get Python syntax error
    #
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror



import json
import requests
import logging
import config

################################
# Load config
################################


config_path = config.conifg_load()
with open(config_path) as json_data_file:
    conf = json.load(json_data_file)


################################
# Logging
################################


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sonarr")


################################
# Init
################################

url = conf['sonarr']['host']
headers = {'X-Api-Key': conf['sonarr']['api']}


################################
# Main
################################


def qprofile_lookup():
    """Check sonarr quality profile ID"""
    r = requests.get(url + '/api/profile', headers=headers)
    qprofile_id = r.json()
    x = 0
    for _ in qprofile_id:
        if qprofile_id[x]['name'].lower() == conf['sonarr']['quality_profile'].lower():
            return qprofile_id[x]['id']
        else:
            x += 1


def get_library():
    """Get sonarr library in a list of tvdbid ids"""
    library = []
    r = requests.get(url + '/api/series', headers=headers)
    tv_lib_raw = r.json()
    for n in tv_lib_raw:
        library.append(n['tvdbId'])
    return library

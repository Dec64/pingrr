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


logger = logging.getLogger("Sonarr")
logging.basicConfig(level=logging.INFO)


################################
# Init
################################

url = conf['sonarr']['host']
headers = {'X-Api-Key': conf['sonarr']['api']}


################################
# Main
################################


def get_library():
    """Get sonarr library in a list of tvdbid ids"""
    library = []
    r = requests.get(url + '/api/series', headers=headers, timeout=5.000)
    tv_lib_raw = r.json()
    for n in tv_lib_raw:
        library.append(n['tvdbId'])
    return library

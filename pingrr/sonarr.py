import logging
import config
import sys
import requests

################################
# Load config
################################

conf = config.Config().config

################################
# Logging
################################

logger = logging.getLogger(__name__)

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
    r = requests.get(url + '/api/series', headers=headers, timeout=60)
    try:
        if r.status_code == 401:
            logger.warning("Error when connecting to sonarr, unauthorised. check api/url")
            sys.exit(1)
        tv_lib_raw = r.json()
        for n in tv_lib_raw:
            library.append(n['tvdbId'])
    except requests.ConnectionError:
        logger.warning("Can not connect to sonarr check if sonarr is up, or URL is right")
        sys.exit(1)
    return library

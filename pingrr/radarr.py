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

url = conf['radarr']['host']
headers = {'X-Api-Key': conf['radarr']['api']}

################################
# Main
################################


def get_library():
    """Get radarr library in a list of imdb ids"""
    library = []
    r = requests.get(url + '/api/movie', headers=headers, timeout=5.000)
    try:
        if r.status_code == 401:
            logger.warning("Error when connecting to radarr, unauthorised. check api/url")
            sys.exit(1)
        movie_lib_raw = r.json()
        for n in movie_lib_raw:
            library.append(n['imdbId'])
    except requests.ConnectionError:
        logger.warning("Can not connect to sonarr check if radarr is up, or URL is right")
        sys.exit(1)
    return library

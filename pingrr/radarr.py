import logging
import config
import sys
import requests
import json

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


def search_movie(movie_id):

    payload = {
        "name": "moviesSearch",
        "movieIds": [movie_id]
               }

    r = requests.post(url + '/api/command', headers=headers, data=json.dumps(payload), timeout=30)

    if r.status_code == 201:
        logger.info("radarr search request OK")
        return True
    else:
        return False


def get_library():
    """Get radarr library in a list of imdb ids"""
    library = []
    r = requests.get(url + '/api/movie', headers=headers, timeout=60)
    try:
        if r.status_code == 401:
            logger.warning("Error when connecting to radarr, unauthorised. check api/url")
            sys.exit(1)
        movie_lib_raw = r.json()
        for n in movie_lib_raw:
            library.append(n['tmdbId'])
    except requests.ConnectionError:
        logger.warning("Can not connect to radarr check if radarr is up, or URL is right")
        sys.exit(1)
    return library

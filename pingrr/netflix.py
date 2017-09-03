import json
import requests
import logging
import config

import trakt

################################
# Load config
################################


config_path = config.conifg_load()
with open(config_path) as json_data_file:
    conf = json.load(json_data_file)

################################
# Logging
################################


logger = logging.getLogger("Netflix")
logging.basicConfig(level=logging.INFO)


################################
# Init
################################


url = "https://unogs-unogs-v1.p.mashape.com/aaapi.cgi?q=get:new" + conf['unogs']['days'] + ":" + conf['unogs'][
    'country'] + "&p=1&t=ns&st=adv"
headers = {"X-Mashape-Key": conf['unogs']['api'], "Accept": "application/json"}


################################
# Main
################################

def get_list():
    """get list of recently added netflix items"""
    r = requests.get(url=url, headers=headers, timeout=5.000)
    if r.status_code == requests.codes.ok:
        logger.debug('got raw netflix list successfully')
        return r.json()
    else:
        logger.debug('failed to get raw netflix list, code return: ' + str(r.status_code))
        return False


def create_list():
    """create list of tv-shows from netflix data"""
    logger.info('creating list from netflix recent')
    if len(conf['unogs']['api']) > 0:
        logger.debug('unogs api key found, starting to create netflix list')
        data = get_list()
        x = []
        for item in data['ITEMS']:
            if item['type'] == 'series':
                try:
                    info = trakt.get_info(item['imdbid'])
                    if info is False:
                        logger.debug('Show: ', item['title'], ' does not have imdb ID, skipping')
                        pass
                    else:
                        x.append(info)
                        logger.debug('Show: ', item['title'], ' added to netflix list')
                except:
                    logger.warning('can not read netflix data, error creating list')
        logger.info('Netflix list created, ' + str(len(x)) + ' shows found')
        return x
    return []

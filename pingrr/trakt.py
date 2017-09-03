import requests
import logging
import json
import urllib
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


logger = logging.getLogger("Trakt")
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s')


################################
# Init
################################


data = []
headers = {'content-type': 'application/json',
           'trakt-api-version': '2',
           'trakt-api-key': conf['trakt']['api']}
popular = []
anticipated = []
trending = []


################################
# Main
################################


def get_info_search(tv_id):
    """Get info for a tv show"""
    url = "https://api.trakt.tv/search/show?query=" + urllib.quote_plus(tv_id) + "&extended=full"
    logger.debug('getting info from trakt for ' + tv_id)
    r = requests.get(url=url, headers=headers, timeout=5.000)
    if r.status_code == requests.codes.ok:
        x = []
        y = r.json()
        y = y[0]['show']
        x.append({'title': y['title'],
                  'status': y['status'],
                  'tvdb': y['ids']['tvdb'],
                  'imdb': y['ids']['imdb'],
                  'trakt': y['ids']['trakt'],
                  'rating': y['rating'],
                  'language': y['language'],
                  'genres': y['genres'],
                  'year': y['year']
                  })
        logger.debug('got tv show info successfully')
        return x
    else:
        logger.debug('failed to get trakt show info, code return: ' + str(r.status_code))
        return False


def make_url(list_type):
    """Generate the url for trakt api with filters as needed"""
    url = "https://api.trakt.tv" + "/shows/" + list_type + "/?limit=" + str(conf['trakt']['limit'])
    logger.debug('created trakt url for: ', list_type)
    return url


def get_trakt_popular():
    """Get trakt popular list info"""
    r = requests.get(url=make_url('popular'), headers=headers)
    if r.status_code == requests.codes.ok:
        logger.debug('got trakt popular list successfully')
        return r.json()
    else:
        logger.debug('failed to get trakt popular list, code return: ' + str(r.status_code))
        return False


def get_trakt_anticipated():
    """Get trakt anticipated list info"""
    r = requests.get(url=make_url('anticipated'), headers=headers)
    if r.status_code == requests.codes.ok:
        logger.debug('got trakt list anticipated successfully')
        return r.json()
    else:
        logger.debug('failed to get trakt anticipated list, code return: ' + str(r.status_code))
        return False


def get_trakt_trending():
    """Get trakt anticipated list info"""
    r = requests.get(url=make_url('trending'), headers=headers)
    if r.status_code == requests.codes.ok:
        logger.debug('got trakt trending list successfully')
        return r.json()
    else:
        logger.debug('failed to get trakt trending list, code return: ' + str(r.status_code))
        return False


def get_info(tv_id):
    """Get info for a tv show"""
    url = "https://api.trakt.tv/shows/" + tv_id + "?extended=full"
    logger.debug('getting info from trakt for ', tv_id)
    r = requests.get(url=url, headers=headers, timeout=5.000)
    if r.status_code == requests.codes.ok:
        x = []
        y = r.json()
        x.append({'title': y['title'], 'status': y['status'], 'tvdb': y['ids']['tvdb'], 'imdb': y['ids']['imdb'],
                  'trakt': y['ids']['trakt'], 'rating': y['rating'], 'language': y['language'], 'genres': y['genres']})
        logger.debug('got tv show info successfully')
        return x
    else:
        logger.debug('failed to get trakt show info, code return: ' + str(r.status_code))
        return False


def create_list():
    x = []
    logger.info('creating list from trakt.tv')
    if conf['trakt']['list']['popular']:
        for item in get_trakt_anticipated():
            x.append(get_info(item['show']['ids']['imdb']))
            logger.debug('adding ', item['show']['title'], ' from popular')
    if conf['trakt']['list']['popular']:
        for item in get_trakt_trending():
            if item['show']['ids']['imdb'] not in x:
                x.append(get_info(item['show']['ids']['imdb']))
                logger.debug('adding ', item['show']['title'], ' from trending')
    if conf['trakt']['list']['trending']:
        for item in get_trakt_anticipated():
            if item['show']['ids']['imdb'] not in x:
                x.append(get_info(item['show']['ids']['imdb']))
                logger.debug('adding ', item['show']['title'], ' from anticipated')
    else:
        logger.info('no trakt lists wanted, skipping')
        pass
    logger.info('trakt list created, ' + str(len(x)) + ' shows found')
    return x
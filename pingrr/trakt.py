import logging
import config
import time
import requests
import urllib

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

data = []
headers = {
    'content-type': 'application/json',
    'trakt-api-version': '2',
    'trakt-api-key': conf['trakt']['api']
}
popular = []
anticipated = []
trending = []

################################
# Main
################################


#def get_info_search(tv_id):
#    """Get info for a tv show"""
#    url = "https://api.trakt.tv/search/show?query=" + urllib.quote_plus(tv_id) + "&extended=full"
#    logger.debug('getting info from trakt for ' + tv_id)
#    r = requests.get(url=url, headers=headers, timeout=5.000)
#    if r.status_code == requests.codes.ok:
#        x = []
#        y = r.json()
#        y = y[0]['show']
#        x.append({'title': y['title'],
#                  'status': y['status'],
#                  'tvdb': y['ids']['tvdb'],
#                  'imdb': y['ids']['imdb'],
#                  'trakt': y['ids']['trakt'],
#                  'rating': y['rating'],
#                  'language': y['language'],
#                  'country': y['country'],
#                  'genres': y['genres'],
#                  'network': y['network'],
#                  'votes': y['votes'],
#                  'runtime': y['runtime'],
#                  'year': y['year']
#                  })
#        logger.debug('got tv show info successfully')
#        return x
#    else:
#        logger.debug('failed to get trakt show info, code return: ' + str(r.status_code))
#        return False


def get_info_search(tv_id, trakt_type):
    """Get info for a tv show"""

    if tv_id is None:
        return False

    url = "https://api.trakt.tv/search/" + trakt_type + "?query=" + urllib.quote_plus(tv_id) + "&extended=full"
    logger.debug('getting info from trakt for ' + tv_id)
    r = requests.get(url=url, headers=headers, timeout=10)

    if r.status_code == requests.codes.ok:
        if trakt_type == "movie":
            x = []
            y = r.json()
            y = y[0]['movie']
            x.append({
                'title': y['title'],
                # 'status': y['status'],
                # 'tvdb': y['ids']['tvdb'],
                'imdb': y['ids']['imdb'],
                'trakt': y['ids']['trakt'],
                'rating': y['rating'],
                'language': y['language'],
                # 'country': y['country'],
                'genres': y['genres'],
                # 'network': y['network'],
                'votes': y['votes'],
                'runtime': y['runtime'],
                'year': y['year']
            })
            logger.debug('got movie show info successfully')
            return x

        else:
            x = []
            y = r.json()
            y = y[0]['show']
            x.append({
                'title': y['title'],
                'status': y['status'],
                'tvdb': y['ids']['tvdb'],
                'imdb': y['ids']['imdb'],
                'trakt': y['ids']['trakt'],
                'rating': y['rating'],
                'language': y['language'],
                'country': y['country'],
                'genres': y['genres'],
                'network': y['network'],
                'votes': y['votes'],
                'runtime': y['runtime'],
                'year': y['year']
            })
            logger.debug('got tv show info successfully')
            return x

    else:
        logger.debug('failed to get trakt show info, code return: ' + str(r.status_code))
        return False


def make_url(list_type):
    """Generate the url for trakt api with filters as needed"""
    if list_type == 'trending':
        url = "https://api.trakt.tv/shows/" + list_type + "/?limit=100"
    else:
        url = "https://api.trakt.tv/shows/" + list_type + "/?limit=" + str(conf['trakt']['limit'])
    logger.debug('created trakt url for: ' + list_type)
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
    while True:
        r = requests.get(url=make_url('trending'), headers=headers)
        if r.status_code == 200:
            logger.debug('got trakt trending list successfully')
            return r.json()
        else:
            logger.debug('failed to get trakt trending list, code return: ' + str(r.status_code))
            logger.debug('trying again in 5 seconds')
            time.sleep(5)


def get_info(tv_id):
    """Get info for a tv show"""

    if tv_id is None:
        return False

    url = "https://api.trakt.tv/shows/%s?extended=full" % tv_id
    logger.debug('getting info from trakt for %r', tv_id)
    r = requests.get(url=url, headers=headers)

    if r.status_code == requests.codes.ok:
        x = []
        y = r.json()
        x.append({
            'title': y['title'],
            'status': y['status'],
            'tvdb': y['ids']['tvdb'],
            'imdb': y['ids']['imdb'],
            'trakt': y['ids']['trakt'],
            'rating': y['rating'],
            'language': y['language'],
            'country': y['country'],
            'genres': y['genres'],
            'network': y['network'],
            'votes': y['votes'],
            'runtime': y['runtime'],
            'year': y['year']
        })
        logger.debug('got tv show info successfully')
        return x

    else:
        logger.debug('failed to get trakt show info, code return: ' + str(r.status_code))
        return False


def create_list():
    x = []
    logger.info('creating list from trakt.tv')

    if conf['trakt']['list']['popular']:
        for item in get_trakt_popular():
            show_info = get_info(item['ids']['imdb'])

            if show_info:
                x.append(show_info)
                logger.debug('adding ' + item['title'] + ' from popular')

            else:
                logger.warn('Error getting info for ' + item['title'] + ' from popular')

    if conf['trakt']['list']['trending']:
        for item in get_trakt_trending():
            if item['show']['ids']['imdb'] not in x:
                show_info = get_info(item['show']['ids']['imdb'])
                if show_info:
                    x.append(show_info)
                    logger.debug('adding ' + item['show']['title'] + ' from trending')

                else:
                    logger.warn('Error getting info for ' + item['show']['title'] + ' from trending')

    if conf['trakt']['list']['anticipated']:
        for item in get_trakt_anticipated():
            if item['show']['ids']['imdb'] not in x:
                show_info = get_info(item['show']['ids']['imdb'])
                if show_info:
                    x.append(show_info)
                    logger.debug('adding ' + item['show']['title'] + ' from anticipated')

                else:
                    logger.warn('Error getting info for ' + item['show']['title'] + ' from anticipated')

    else:
        logger.info('no trakt lists wanted, skipping')
        pass

    logger.info('trakt list created, %d shows found', len(x))

    return x

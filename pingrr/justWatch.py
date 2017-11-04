import requests
import logging
import urllib
import config
from time import sleep

################################
# Load config
################################

# Load initial config
configuration = config.Config()

# Load config file
configuration.load()
conf = configuration.config

################################
# Logging
################################

logger = logging.getLogger(__name__)

################################
# Init
################################

headers = {'content-type': 'application/json',
           'trakt-api-version': '2',
           'trakt-api-key': "661beaf337a80ade68c88603cef20b4b80e529752017e5a04d63d264757eca42"}

################################
# Main
################################


def get_info_search(title, trakt_type):
    """Get info for a show or movie from trakt"""
    url = "https://api.trakt.tv/search/{}?query={}&extended=full".format(trakt_type, urllib.quote_plus(title))
    logger.debug('getting info from trakt for ' + title)
    try:
        r = requests.get(url=url, headers=headers, timeout=5.000)
    except requests.exceptions.ReadTimeout:
        return False
    y = r.json()
    x = []

    if r.status_code == requests.codes.ok and len(y):
        if trakt_type == "movie":
            y = y[0]['movie']
            x.append({'title': y['title'],
                    #'status': y['status'],
                    #'tvdb': y['ids']['tvdb'],
                    'imdb': y['ids']['imdb'],
                    'trakt': y['ids']['trakt'],
                    'rating': y['rating'],
                    'language': y['language'],
                    #'country': y['country'],
                    'genres': y['genres'],
                    #'network': y['network'],
                    'votes': y['votes'],
                    'runtime': y['runtime'],
                    'year': y['year']
                    })
            logger.debug('got movie show info successfully')
            return x

        else:
            y = y[0]['show']
            x.append({'title': y['title'],
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
        logger.debug('failed to get trakt show info, code return: {}'.format(r.status_code))
        return False


#def get_providers():
#    r = requests.get("https://apis.justwatch.com/content/providers/locale/en_" + conf['just_watch']['country'])
#    providers = []
#    for x in r.json():
#        providers.append(str(x['short_name']))
#    return providers


def get_recent(page):

    r = requests.get("https://apis.justwatch.com/content/titles/en_{}/new?body=%7B%22"
                     "age_certifications%22:null,"
                     "%22content_types%22:%5B%22show_season%22%5D,"
                     "%22genres%22:null,"
                     "%22languages%22:null,"
                     "%22max_price%22:null,"
                     "%22min_price%22:null,"
                     "%22monetization_types%22:%5B%22flatrate%22,"
                     "%22rent%22,%22buy%22,"
                     "%22free%22,%22ads%22%5D,"
                     "%22page%22:{},"
                     "%22page_size%22:null,"
                     "%22presentation_types%22:null,"
                     "%22providers%22:null,"
                     "%22release_year_from%22:null,"
                     "%22release_year_until%22:null,"
                     "%22scoring_filter_types%22:null,"
                     "%22titles_per_provider%22:6%7D".format(conf['just_watch']['country'].upper(), str(page)))

    try:
        if r.status_code == 200:
            return r.json()
        else:
            logger.debug("Failed to get JustWatch list")
            return []

    except ValueError:
        logger.warning("Value Error while getting recent from just watch")


def create_list():
    logger.info("Creating Just Watch list")
    tv_list = []
    #movie_list = []

    try:
        pages = int(conf['just_watch']['pages'])
    except TypeError:
        pages = 1
        logger.warning("WARNING: NO PAGES SET IN CONFIG, SETTING TO 1 TO BE SAFE")
    x = 1

    while x <= pages:
        data = get_recent(x)
        if data:
            for day in data['days']:
                logger.debug("Getting new releases from: {}".format(str(day['date'])))
                for provider in day['providers']:
                    for item in provider['items']:
                        if item['object_type'] == 'show_season':
                            show_title = item['show_title']
                            if "?" in show_title:
                                show_title = show_title.replace("?", "")
                            sleep(0.5)
                            y = get_info_search(show_title.encode('utf8'), "show")
                            if not y:
                                logger.info("trakt api connection timed out, failed to get show\n"
                                            "Continuing, will be missing some possible shows")
                                break
                            #while not y:
                            #    logger.info("trakt api connection timed out, trying again in 5mins")
                            #    sleep(350)
                            #    y = get_info_search(show_title.encode('utf8'), "show")
                            if y:
                                if y[0]['title'].lower() == item['show_title'].lower() and y not in tv_list:
                                    logger.debug(item['show_title'])
                                    tv_list.append(y)
                            else:
                                try:
                                    logger.debug("Failed to get data on show: {}".format(str(item['show_title'].encode('utf8'))))
                                except UnicodeEncodeError:
                                    logger.debug("Failed to get data on show, unicode error: {}".format(item))
                        elif item['object_type'] == 'movie':
                            pass

                        ### TODO add radarr/movie support
                        #y = get_info_search(item['show_title'].encode('utf8'), "movie")
                        #if y[0]['title'].lower() == item['title'].lower():
                        #logger.info(get_info_search(item['title'].encode('utf8'), "movie"))
                        #movie_list.append(y)
                        #else:
                        #logger.info("no movie title found " + item['title'])

        logger.debug('page {}'.format(str(x)))
        x += 1
    logger.info("Just Watch list created, {} shows found".format(len(tv_list)))
    return tv_list

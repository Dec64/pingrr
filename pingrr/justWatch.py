import requests
import logging
import config
import re
import pingrr.trakt as trakt

from time import sleep

################################
# Load config
################################

conf = config.Config().config

################################
# Logging
################################

logger = logging.getLogger(__name__)

################################
# Main
################################

# def get_providers():
#    r = requests.get("https://apis.justwatch.com/content/providers/locale/en_" + conf['just_watch']['country'])
#    providers = []
#    for x in r.json():
#        providers.append(str(x['short_name']))
#    return providers


def get_recent(page, get_type):

    if get_type == "movies":
        content_type = "%5B%22movie%22%5D"
    elif get_type == "shows":
        content_type = "%5B%22show_season%22%5D"

    r = requests.get("https://apis.justwatch.com/content/titles/en_{}/new?body=%7B%22"
                     "age_certifications%22:null,"
                     "%22content_types%22:{},"
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
                     "%22titles_per_provider%22:6%7D".format(conf['just_watch']['country'].upper(), content_type, str(page)))

    try:
        if r.status_code == 200:
            return r.json()
        else:
            logger.debug("Failed to get JustWatch list")
            return []

    except ValueError:
        logger.warning("Value Error while getting recent from just watch")


def create_list(wanted):
    logger.info("Creating Just Watch list")
    tv_list = []
    movie_list = []

    try:
        pages = int(conf['just_watch']['pages'])
    except TypeError:
        pages = 1
        logger.warning("WARNING: NO PAGES SET IN CONFIG, SETTING TO 1 TO BE SAFE")
    x = 1

    while x <= pages:

        if wanted == "shows":
            data = get_recent(x, "shows")
        elif wanted == "movies":
            data = get_recent(x, "movies")

        if data:
            for day in data['days']:
                logger.info("Getting new releases from: {}".format(str(day['date'])))
                for provider in day['providers']:
                    for item in provider['items']:
                        skip = False

                        # Get TV from Just Watch

                        if item['object_type'] == 'show_season' and wanted == "shows":

                            for obj in tv_list:
                                if item['show_title'].lower() in obj['title'].lower():
                                    skip = True

                            show_title = item['show_title']
                            show_title = re.sub(r'([^\s\w]|_)+', '', show_title)

                            # Sleep for half a second to avoid trakt api rate limit - Needs more testing
                            # sleep(0.5)

                            if not skip:
                                y = trakt.search(show_title, "show")

                                if not y:
                                    logger.debug("failed to get show continuing, will be missing some possible shows")
                                    break

                                if y:
                                    if y[0]['title'].lower().replace(":", "") == \
                                            item['show_title'].lower().replace(":", ""):
                                        tv_list.append(y[0])
                                else:
                                    try:
                                        logger.debug("Failed to get data on show: {}".format(str(item['show_title'].encode('utf8'))))
                                    except UnicodeEncodeError:
                                        logger.debug("Failed to get data on show, unicode error: {}".format(item))

                        # Get movies from Just Watch

                        elif item['object_type'] == 'movie' and wanted == "movies":

                            for obj in movie_list:
                                if item['title'].lower() in obj['title'].lower():
                                    skip = True
                            movie_title = item['title']
                            #movie_title = re.sub(r'([^\s\w]|_)+', '', movie_title)
                            movie_title = re.sub(r'[^\w\s\-]*', '', movie_title)

                            # Sleep for half a second to avoid trakt api rate limit - Needs more testing
                            # sleep(0.5)

                            if not skip:
                                y = trakt.search(movie_title, "movie")

                                if not y:
                                    logger.info("failed to get movie continuing, will be missing some possible movies")
                                    break

                                if y:
                                    if y[0]['title'].lower().replace(":", "") == item['title'].lower().replace(":", ""):
                                        movie_list.append(y[0])
                                else:
                                    try:
                                        logger.info("Failed to get data on show: {}".format(str(item[movie_title].encode('utf8'))))
                                    except UnicodeEncodeError:
                                        logger.debug("Failed to get data on show, unicode error: {}".format(item))

        logger.debug('page {}'.format(str(x)))
        x += 1

    if wanted == "movies":
        logger.info("Just Watch list created, {} movies found".format(len(movie_list)))
        return movie_list

    elif wanted == "shows":
        logger.info("Just Watch list created, {} shows found".format(len(tv_list)))
        return tv_list

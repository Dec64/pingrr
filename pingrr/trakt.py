import logging
import config
import requests
import urllib
import re

import imdb

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

i = imdb.IMDb()

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


def search(search_string, trakt_type):
    """Get info for a tv show or movie"""

    if search_string is None:
        return False

    url = "https://api.trakt.tv/search/{}?query={}&extended=full"\
        .format(trakt_type, urllib.quote_plus(search_string.encode('utf8')))
    logger.debug('getting info from trakt for {}'.format(search_string.encode('utf8')))
    r = requests.get(url=url, headers=headers, timeout=10)

    # If request was as ok, and json data returned continue
    if r.status_code == requests.codes.ok and r.json():
        x = []
        y = r.json()

        # If the titles do not match exactly do not process

        title1 = re.sub(r'[^\w\s\-]*', '', y[0][trakt_type]['title'].lower())
        title2 = re.sub(r'[^\w\s\-]*', '', search_string.lower())

        if title1 not in title2:
            logger.debug("Can't get info for {}, does not match with {}".format(search_string.encode('utf8'), (y[0][trakt_type]['title'].encode('utf8'))))
            return False

        if trakt_type == "movie":
            y = y[0]['movie']
        elif trakt_type == "show":
            y = y[0]['show']

        user_rating = y['rating']
        genre = y['genres']
        votes = y['votes']

        if conf['trakt']['imdb_info']:
            # Load imdb api for show/movie
            try:
                m = i.get_movie(y['ids']['imdb'][2:])
            except TypeError:
                return False

            # Get imdb user rating for show/movie
            try:
                user_rating = m['user rating']
            except KeyError:
                logger.info("{0}:{2} using trakt rating ({1}), not imdb".format(y[0][trakt_type]['title'], user_rating, search_string.encode('utf8')))

            # Get imdb genres for show/movie
            try:
                genre = m['genre']
            except KeyError:
                logger.info("{0}:{2} using trakt genres ({1}), not imdb".format(y[0][trakt_type]['title'], genre, search_string.encode('utf8')))

            # Get imdb votes for show/movie
            try:
                votes = m['votes']
            except KeyError:
                logger.info("{0}:{2} using trakt votes ({1}), not imdb".format(y[0][trakt_type]['title'], votes, search_string.encode('utf8')))

        # if movie details where requested return movie payload
        if trakt_type == "movie":
            x.append({'title': y['title'],
                      'tmdb': y['ids']['tmdb'],
                      'imdb': y['ids']['imdb'],
                      'trakt': y['ids']['trakt'],
                      'rating': user_rating,
                      'language': y['language'],
                      'genres': genre,
                      'votes': votes,
                      'runtime': y['runtime'],
                      'certification': y['certification'],
                      'released': y['released'],
                      'year': y['year']})
            logger.debug("got {}'s info successfully".format(y['title']))
            return x

        # if TV details where requested return TV payload
        elif trakt_type == "show":
            x.append({'title': y['title'],
                      'status': y['status'],
                      'tvdb': y['ids']['tvdb'],
                      'imdb': y['ids']['imdb'],
                      'trakt': y['ids']['trakt'],
                      'rating': user_rating,
                      'language': y['language'],
                      'country': y['country'],
                      'genres': genre,
                      'network': y['network'],
                      'votes': votes,
                      'runtime': y['runtime'],
                      'year': y['year'],
                      'aired': y['aired_episodes']})
            logger.debug("got {}'s info successfully".format(y['title']))
            return x

    else:
        logger.debug('failed to get trakt show info for {}, code return: {}'.format(search_string, str(r.status_code)))
        return False


def get_trakt_data(name, cat):
    """Get trakt list info"""

    if cat == 'trending':
        url = "https://api.trakt.tv/{}/{}/?limit=100&extended=full".format(name, cat)
    else:
        url = "https://api.trakt.tv/{}/{}/?limit={}&extended=full".format(name, cat, str(conf['trakt']['limit']))

    r = requests.get(url=url, headers=headers)

    if r.status_code == requests.codes.ok:
        logger.debug('got trakt {} {} list successfully'.format(name, cat))
    else:
        logger.debug('failed to get trakt {} {} list, code return: {}'.format(name, cat, str(r.status_code)))
        return False

    response = r.json()

    x = []

    for element in response:

        if cat == 'trending' or cat == 'anticipated':
            if name == 'shows':
                obj = element['show']
            if name == 'movies':
                obj = element['movie']
        else:
            obj = element

        user_rating = obj['rating']
        genre = obj['genres']
        votes = obj['votes']

        if conf['trakt']['imdb_info']:

            # Load imdb api for show/movie
            try:
                m = i.get_movie(obj['ids']['imdb'][2:])
            except TypeError:
                return False

            # Get imdb user rating for show/movie
            try:
                user_rating = m['user rating']
            except KeyError:
                user_rating = obj['rating']

            # Get imdb genres for show/movie
            try:
                genre = m['genre']
            except KeyError:
                genre = obj['genres']

            # Get imdb votes for show/movie
            try:
                votes = m['votes']
            except KeyError:
                votes = obj['votes']

        if name == 'movies':
            x.append({'title': obj['title'],
                      'tmdb': obj['ids']['tmdb'],
                      'imdb': obj['ids']['imdb'],
                      'trakt': obj['ids']['trakt'],
                      'rating': user_rating,
                      'language': obj['language'],
                      'genres': genre,
                      'votes': votes,
                      'runtime': obj['runtime'],
                      'certification': obj['certification'],
                      'released': obj['released'],
                      'year': obj['year']})
            logger.debug("got {}'s info successfully".format(obj['title'].encode('utf8')))
        else:
            x.append({'title': obj['title'],
                      'status': obj['status'],
                      'tvdb': obj['ids']['tvdb'],
                      'imdb': obj['ids']['imdb'],
                      'trakt': obj['ids']['trakt'],
                      'rating': user_rating,
                      'language': obj['language'],
                      'country': obj['country'],
                      'genres': genre,
                      'network': obj['network'],
                      'votes': votes,
                      'runtime': obj['runtime'],
                      'year': obj['year'],
                      'aired': obj['aired_episodes']})
            logger.debug("got {}'s info successfully".format(obj['title'].encode('utf8')))
    return x


# def get_json_data(tvdb):
#     url = "http://skyhook.sonarr.tv/v1/tvdb/shows/en/{}".format(tvdb)
#     r = requests.get(url)
#     if r.status_code == requests.codes.ok:
#         logger.debug('got json data for {} successfully'.format(tvdb))
#         return r.json()
#     else:
#         logger.debug('failed to get json data for {}'.format(tvdb))
#         return False


def get_info(arg):

    trakt_temp_tv = []
    trakt_temp_movie = []

    if arg == 'tv':
        logger.info("Checking if any trakt tv lists are required")
        for tv_list in conf['trakt']['tv_list']:
            if conf['trakt']['tv_list'][tv_list]:
                logger.info("Getting {} tv list from trakt".format(tv_list))
                trakt_temp_tv.append(get_trakt_data('shows', tv_list))

        trakt_complete_tv = []

        for trakt_list in trakt_temp_tv:
            for line in trakt_list:
                if line not in trakt_complete_tv:
                    trakt_complete_tv.append(line)

        return trakt_complete_tv

    if arg == 'movie':
        logger.info("Checking if any trakt movie lists are required")
        for movie_list in conf['trakt']['movie_list']:
            if conf['trakt']['movie_list'][movie_list]:
                logger.info("Getting {} movie list from trakt".format(movie_list))
                trakt_temp_movie.append(get_trakt_data('movies', movie_list))

        trakt_complete_movie = []

        for trakt_list in trakt_temp_movie:
            for line in trakt_list:
                if line not in trakt_complete_movie:
                    trakt_complete_movie.append(line)

        return trakt_complete_movie

import pingrr.config as config

import json
import logging
from logging.handlers import RotatingFileHandler
import sys

from requests import post
from time import sleep

################################
# Logging
################################

# Logging format
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

# root logger
logger = logging.getLogger()
# Set initial level to INFO
logger.setLevel(logging.INFO)

# Console handler, log to stdout
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

# Other modules logging levels
logging.getLogger("requests").setLevel(logging.WARNING)

################################
# Load config
################################

# Load initial config
configuration = config.Config()

# Set configured log level
logger.setLevel(configuration.settings['loglevel'])

# Load config file
configuration.load()
conf = configuration.config

# Log file handler
fileHandler = RotatingFileHandler(configuration.settings['logfile'], maxBytes=1024 * 1024 * 2, backupCount=1)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

################################
# Init
################################

import pingrr.trakt as trakt
import pingrr.sonarr as sonarr
import pingrr.allflicks as allflicks
import pingrr.justWatch as justwatch
from pingrr.notifications import Notifications

new_shows = []
delay_time = conf['pingrr']['timer'] * 3600
options = {
    "ignoreEpisodesWithFiles": False,
    "ignoreEpisodesWithoutFiles": False,
    "searchForMissingEpisodes": conf['sonarr']['search_missing_episodes']
}
notify = Notifications()

if conf['pushover']['enabled']:
    notify.load(
        service="pushover",
        app_token=conf['pushover']['app_token'],
        user_token=conf['pushover']['user_token']
    )

if conf['slack']['enabled']:
    notify.load(
        service="slack",
        webhook_url=conf['slack']['webhook_url'],
        sender_name=conf['slack']['sender_name'],
        sender_icon=conf['slack']['sender_icon'],
        channel=conf['slack']['channel']
    )

################################
# Main
################################


def send_to_sonarr(a, b):
    """Send found tv program to sonarr"""

    payload = {
        "tvdbId": a,
        "title": b,
        "qualityProfileId": conf['sonarr']['quality_profile'],
        "images": [],
        "seasons": [],
        "seasonFolder": True,
        "monitored": conf['sonarr']['monitored'],
        "rootFolderPath": conf['sonarr']['folder_path'],
        "addOptions": options,
    }

    r = post(sonarr.url + '/api/series', headers=sonarr.headers, data=json.dumps(payload), timeout=10)

    if r.status_code == 201:
        logger.debug("sent to sonarr successfully")

        return True

    else:
        logger.debug("failed to send to sonarr, code return: %r", r.status_code)

        return False


def add_shows():
    sonarr_library = sonarr.get_library()
    added_list = []
    n = 0
    limit = conf['pingrr']['limit']

    for show in new_shows:
        if show['tvdb'] not in sonarr_library:
            title = show['title']
            tvdb_id = show['tvdb']

            try:
                logger.info('sending show to sonarr: {}'.format(show['title'].encode('utf8')))

                if send_to_sonarr(tvdb_id, title):
                    logger.info('{} has been added to Sonarr'.format(title.encode('utf8')))
                    added_list.append(show['title'])

                    n += 1
                    if 0 < limit == n:
                        logger.info('{} shows added limit reached'.format(str(n)))

                        break

                    elif limit > 0 and not n == limit:
                        logger.debug('limit not yet reached: {}'.format(str(n)))

                else:
                    configuration.blacklist.add(str(show['tvdb']))
                    logger.warning('{} failed to be added to Sonarr! Adding to blacklist'.format(title.encode('utf8')))

            except IOError:
                logger.warning('error sending show: {} tvdbid: {}'.format(title.encode('utf8'), str(tvdb_id)))

    if conf['pushover']['enabled'] or conf['slack']['enabled'] and n != 0:
        if n > 1:
            text = (str(n), "TV Show", "have", str(len(new_shows)))
        else:
            text = (str(n), "TV Show", "has", str(len(new_shows)))
        message = "The following %s %s out of %s %s been added to Sonarr: " % text + "\n" + '\n'.join(added_list)
        notify.send(message=message)


def new_check():
    """Check for new trakt items in list"""
    library = sonarr.get_library()
    global new_shows
    new_shows = filter_list()
    logger.info('checking for new shows in lists')
    for x in new_shows:
        logger.debug('checking show from list: {}'.format(x['title']))
        if x['tvdb'] not in library and conf['filters']['allow_ended']:
            logger.info('new show(s) found, adding shows now')
            add_shows()
            break
        elif x['tvdb'] not in library and not x['status'] == 'ended':
            logger.info('new continuing show(s) found, adding shows now')
            add_shows()
            break


def check_lists(arg, arg2):
    for filters in conf['filters'][arg]:
        for data in arg2:
            if filters == data:
                return True
    return False


def filter_check(arg):
    title = arg
    country = title[0]['country']
    lang = title[0]['language']
    if str(title[0]['imdb']) in configuration.blacklist or str(title[0]['tvdb']) in configuration.blacklist:
        logger.info("{} was rejected as it was found in the blacklist".format(title[0]['title'].encode('utf8')))
        return False
    if conf['filters']['year'] > title[0]['year']:
        logger.info("{} was rejected as it was outside allowed year range: {}".format(title[0]['title'].encode('utf8'),
                                                                                      str(title[0]['year'])))
        return False
    if conf['filters']['runtime'] > title[0]['runtime']:
        logger.info("{} was rejected as it was outside allowed runtime: {}".format(title[0]['title'].encode('utf8'),
                                                                                   str(title[0]['runtime'])))
        return False
    if title[0]['network'] is None or conf['filters']['network'] in title[0]['network']:
        logger.info("{} was rejected as it was by a disallowed network: {}".format(title[0]['title'].encode('utf8'),
                                                                                   str(title[0]['network'])))
        return False
    if conf['filters']['votes'] > title[0]['votes']:
        logger.info("{} was rejected as it did not meet vote requirement: {}".format(title[0]['title'].encode('utf8'),
                                                                                     str(title[0]['votes'])))
        return False
    if conf['filters']['allow_ended'] is False and 'ended' in title[0]['status']:
        logger.info("{} was rejected as it is an ended tv series".format(title[0]['title'].encode('utf8')))
        return False
    if conf['filters']['allow_canceled'] is False and 'canceled' in title[0]['status']:
        logger.info("{} was rejected as it an canceled tv show".format(title[0]['title'].encode('utf8')))
        return False
    if float(title[0]['rating']) < float(conf['filters']['rating']):
        logger.info("{} was rejected as it was outside the allowed ratings: {}".format(title[0]['title'].encode('utf8'),
                                                                                       str(title[0]['rating'])))
        return False
    if isinstance(conf['filters']['genre'], list):
        if check_lists('genre', title[0]['genres']):
            logger.info("{} was rejected as it wasn't a wanted genre: {}".format(title[0]['title'].encode('utf8'),
                                                                                 str(title[0]['genres'])))
            return False
    elif conf['filters']['genre'] == title[0]['genres']:
        logger.info("{} was rejected as it wasn't a wanted genre: {}".format(title[0]['title'].encode('utf8'),
                                                                             str(title[0]['genres'])))
        return False
    if country not in conf['filters']['country']:
        logger.info("{} was rejected as it wasn't a wanted country: {}".format(title[0]['title'].encode('utf8'),
                                                                               str(title[0]['country'])))
        return False
    if lang not in conf['filters']['language']:
        logger.info("{} was rejected as it wasn't a wanted language: {}".format(title[0]['title'].encode('utf8'),
                                                                                str(title[0]['country'])))
        return False
    return True


def filter_list():
    raw_list = trakt.create_list()
    if conf['allflicks']['enabled']:
        raw_list += allflicks.create_list()
    if conf['just_watch']['enabled']:
        raw_list += justwatch.create_list()
    filtered = []
    for title in raw_list:
        try:
            if filter_check(title):
                logger.debug('adding {} to the list to check with sonarr'.format(title[0]['title'].encode('utf8')))
                filtered.append(title[0])
        except TypeError:
            logger.debug('{} failed to check against filters'.format(title[0]['title'].encode('utf8')))
    logger.debug("Filtered list successfully")
    return filtered


def remove_dupes(dupe_list):
    deduped = []
    for show in dupe_list:
        if show not in deduped:
            deduped.append(show)
    return deduped


if __name__ == "__main__":
    while True:
        new_check()
        # Save updated blacklist
        configuration.save_blacklist()

        if conf['pingrr']['timer'] == 0:
            logger.info('Scan finished, shutting down')
            sys.exit()

        if conf['pingrr']['timer'] > 1:
            hours = "s"
        else:
            hours = ""

        logger.info("check finish, sleeping for {} hour{}".format(conf['pingrr']['timer'], hours))
        sleep(float(delay_time))
        logger.debug('sleep over, checking again')

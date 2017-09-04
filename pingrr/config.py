import json
import logging
import sys
import os
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Config")


def conifg_load():
    if os.path.exists('config.json'):
        path = os.path.join(os.path.dirname(sys.argv[0]), 'config.json')
        return path
    else:
        create_config()


def get_quality_profiles(sonarr_url, key):
    url = sonarr_url
    r = requests.get(url + '/api/profile', headers={'X-Api-Key': key}, timeout=5.000)
    data = r.json()
    for profile in data:
        if profile['name']:
            print str(profile['id']) + ': ' + profile['name']
    wanted = ''
    while wanted is not int and len(data) < wanted:
        try:
            wanted = int(raw_input("Which quality profile do you want to download shows with?: "))
        except ValueError:
            print "Please enter the ID of your profile you want"
            continue
    return wanted


def check_api(sonarr_url, api_key):
    url = sonarr_url
    r = requests.get(url + '/api/system/status', headers={'X-Api-Key': api_key}, timeout=5.000)
    if r.status_code == 200:
        return True
    else:
        return False


def check_host(sonarr_url):
    url = sonarr_url
    try:
        r = requests.get(url + '/api/system/status', timeout=5.000)
        if r.status_code == 401:
            return True
        else:
            return False
    except:
        return False


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1", "y")


def create_config():
    print '\033[93m' + "\nPingrr has no config, please follow the instructions to create one\n" + '\x1b[0m'

    print "\n"
    print "####################################\n" \
          "############ SONARR ################\n" \
          "####################################\n"

    sonarr_host = raw_input("Enter URL for your sonarr server, normally http://localhost:8989: \n")
    while not check_host(sonarr_host):
        try:
            sonarr_host = raw_input("Sonarr URL invalid, check URL and try again: \n")
        except:
            print "Error getting host, try again"
    print '\033[94m' + str(sonarr_host) + '\x1b[0m' + '\n'

    sonarr_api = raw_input("Enter your sonarr API: \n")
    while not check_api(sonarr_host, sonarr_api):
        try:
            sonarr_api = raw_input("Sonarr API invalid, check API and try again: \n")
        except:
            print "Error with api key, try again"
    print '\033[94m' + str(sonarr_api) + '\x1b[0m' + '\n'

    sonarr_folder_path = raw_input("Enter the folder path you want your shows to download to: \n")
    print '\033[94m' + str(sonarr_folder_path) + '\x1b[0m' + '\n'
    sonarr_quality_profile = get_quality_profiles(sonarr_host, sonarr_api)
    print '\033[94m' + str(sonarr_quality_profile) + '\x1b[0m' + '\n'

    print "\n"
    print "####################################\n" \
          "############# TRAKT ################\n" \
          "####################################\n"

    trakt_api = raw_input("Enter your trakt.tv api key: \n")
    print '\033[94m' + str(trakt_api) + '\x1b[0m' + '\n'
    trakt_list_anticipated = raw_input("Do you want to use Trakt's anticipated list? (yes/no): \n")
    print '\033[94m' + str(str2bool(trakt_list_anticipated)) + '\x1b[0m' + '\n'
    trakt_list_popular = raw_input("Do you want to use Trakt's popular list? (yes/no): \n")
    print '\033[94m' + str(str2bool(trakt_list_popular)) + '\x1b[0m' + '\n'
    trakt_list_trending = raw_input("Do you want to use Trakt's trending list? (yes/no): \n")
    print '\033[94m' + str(str2bool(trakt_list_trending)) + '\x1b[0m' + '\n'

    print "\n"
    print "####################################\n" \
          "############ PINGRR ################\n" \
          "####################################\n"

    pingrr_timer = raw_input("How often do you want Pingrr to re-check for new shows, in hours? (0 for never): \n")
    print '\033[94m' + str(pingrr_timer) + '\x1b[0m' + '\n'
    pingrr_limit = raw_input("How many shows to add per check?(0 for no limit): \n")
    print '\033[94m' + str(pingrr_limit) + '\x1b[0m' + '\n'

    print "\n"
    print "####################################\n" \
          "######## NOTIFICATIONS #############\n" \
          "####################################\n"

    notifications_wanted = raw_input("Would you like to use notifications?(yes/no): \n")
    print '\033[94m' + str(str2bool(notifications_wanted)) + '\x1b[0m' + '\n'
    if str2bool(notifications_wanted):
        pushover = raw_input("Enable Pushover notifications?(yes/no): \n")
        print '\033[94m' + str(str2bool(pushover)) + '\x1b[0m' + '\n'
        if str2bool(pushover):
            pushover_user_token = raw_input("Enter your pushover user token: \n")
            print '\033[94m' + str(pushover_user_token) + '\x1b[0m' + '\n'
            pushover_app_token = raw_input("Enter your pushover app token: \n")
            print '\033[94m' + str(pushover_app_token) + '\x1b[0m' + '\n'
        else:
            pushover_user_token = ''
            pushover_app_token = ''
        slack = raw_input("Enable Slack notifications?(yes/no): \n")
        print '\033[94m' + str(str2bool(slack)) + '\x1b[0m' + '\n'
        if str2bool(slack):
            slack_webhook_url = raw_input("Enter your Slack webhook URL: \n")
            print '\033[94m' + str(slack_webhook_url) + '\x1b[0m' + '\n'
            slack_channel = raw_input("Enter the Slack channel to send messages to: \n")
            print '\033[94m' + str(slack_channel) + '\x1b[0m' + '\n'
        else:
            slack_webhook_url = ''
            slack_channel = ''
    else:
        pushover = False
        slack = False
        pushover_user_token = ''
        pushover_app_token = ''
        slack_webhook_url = ''
        slack_channel = ''

    #print '\033[93m' + "\nIf you want to use the Netflix list to add recently added netflix shows you will\n" \
    #                   "need to get a free unogs api from https://market.mashape.com/unogs/unogs first!\n" + '\x1b[0m'

    #netflix_enabled = raw_input("Enable recently added Netflix list?(yes/no): \n")
    #print "\n" * 100
    #if str2bool(netflix_enabled):
    #    netflix_api = raw_input("Enter your Unogs API key: \n")
    #    print "\n" * 100
    #    netflix_country = raw_input("Enter the Netflix country code you want to use(e.g. GB, US or ES): \n")
    #    print "\n" * 100
    #    netflix_days = raw_input("Enter how many days back to check: \n")
    #    print "\n" * 100
    #else:
    #    netflix_api = ''
    #    netflix_country = ''
    #    netflix_days = ''

    print "\n"
    print "####################################\n" \
          "############ NETFLIX ###############\n" \
          "####################################\n"
    allflicks_enabled = raw_input("Enable recently added Netflix list?(yes/no): \n")
    print '\033[94m' + str(str2bool(allflicks_enabled)) + '\x1b[0m' + '\n'

    print "\n"
    print "####################################\n" \
          "############ FILTERS ###############\n" \
          "####################################\n"

    print '\033[93m' + "\nIf you have selected more then one list, it is highly recommended that\n" \
                       "you add filters to avoid spamming Soanrr with rubbish content\n" + '\x1b[0m'

    filters_rating = raw_input("Enter the minimum rating a show must have to be added: \n")
    print '\033[94m' + str(filters_rating) + '\x1b[0m' + '\n'
    # filters_genre = raw_input("Enter the minimum rating a show must have to be added: \n")
    filters_lang = raw_input("Enter the two letter language code for the language a show must be in(e.g. en): \n")
    print '\033[94m' + str(filters_lang) + '\x1b[0m' + '\n'
    filters_year = raw_input("What is the minimum year to grab a movie from? (Hit enter to get all): \n")
    print '\033[94m' + str(filters_year) + '\x1b[0m' + '\n'
    filters_end = raw_input("Do you want to add shows that have finished?(yes/no): \n")
    print '\033[94m' + str(str2bool(filters_end)) + '\x1b[0m' + '\n'
    filters_cancel = raw_input("Do you want to add shows that have been cancelled?(yes/no): \n")
    print '\033[94m' + str(str2bool(filters_cancel)) + '\x1b[0m' + '\n'

    fresh_config = {
        "sonarr": {"host": sonarr_host,
                   "quality_profile": sonarr_quality_profile,
                   "folder_path": sonarr_folder_path,
                   "api": sonarr_api},
        "trakt": {"api": trakt_api,
                  "limit": 0,
                  "list": {
                      "anticipated": str2bool(trakt_list_anticipated),
                      "popular": str2bool(trakt_list_popular),
                      "trending": str2bool(trakt_list_trending)}},
        "pingrr": {"timer": int(pingrr_timer),
                   "limit": int(pingrr_limit),
                   "log_level": "info"},
        "pushover": {"enabled": str2bool(pushover),
                     "user_token": pushover_user_token,
                     "app_token": pushover_app_token},
        "slack": {"enabled": str2bool(slack),
                  "webhook_url": slack_webhook_url,
                  "sender_name": "Pingrr",
                  "sender_icon": ":robot_face:",
                  "channel": slack_channel},
        "filters": {"rating": int(filters_rating),
                    "genre": [""], "language": filters_lang,
                    "allow_ended": str2bool(filters_end),
                    "allow_canceled": str2bool(filters_cancel),
                    "year": int(filters_year)},
        "unogs": {"enabled": '',
                  "api": '',
                  "country": '',
                  "days": ''},
        "allflicks": {"enabled": str2bool(allflicks_enabled),
                      "rating_match": 94}
    }

    with open('config.json', 'w') as outfile:
        json.dump(fresh_config, outfile, indent=4, sort_keys=True)

    logger.info('config file created, please check config and re-run Pingrr')
    sys.exit()

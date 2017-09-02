import json
import logging
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Config")


def conifg_load():
    if os.path.exists('config.json'):
        path = os.path.join(os.path.dirname(sys.argv[0]), 'config.json')
        return path
    else:
        create_config()


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1", "y")


def create_config():
    sonarr_host = raw_input("Enter URL for your sonarr server, normally http://localhost:8989: \n")
    sonarr_quality_profile = raw_input("Enter the quality profile you want to add new shows as: \n")
    sonarr_folder_path = raw_input("Enter the folder path you want your shows to download to: \n")
    sonarr_api = raw_input("Enter your sonarr API: \n")

    trakt_api = raw_input("Enter your trakt.tv api key: \n")
    trakt_list_anticipated = raw_input("Do you want to use Trakt's anticipated list? (yes/no): \n")
    trakt_list_popular = raw_input("Do you want to use Trakt's popular list? (yes/no): \n")
    trakt_list_trending = raw_input("Do you want to use Trakt's trending list? (yes/no): \n")

    pingrr_timer = raw_input("How often do you want Pingrr to re-check for new shows, in hours? (0 for never): \n")
    pingrr_limit = raw_input("How many shows to add per check?(0 for no limit): \n")

    notifications_wanted = raw_input("Would you like to use notifications?(yes/no): \n")
    if str2bool(notifications_wanted):
        pushover = raw_input("Enable Pushover notifications?(yes/no): \n")
        if str2bool(pushover):
            pushover_user_token = raw_input("Enter your pushover user token: \n")
            pushover_app_token = raw_input("Enter your pushover app token: \n")
        else:
            pushover_user_token = ''
            pushover_app_token = ''
        slack = raw_input("Enable Slack notifications?(yes/no): \n")
        if str2bool(slack):
            slack_webhook_url = raw_input("Enter your Slack webhook URL: \n")
            slack_channel = raw_input("Enter the Slack channel to send messages to: \n")
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

    print '\033[93m' + "\nIf you want to use the Netflix list to add recently added netflix shows you will\n" \
                       "need to get a free unogs api from https://market.mashape.com/unogs/unogs first!\n" + '\x1b[0m'

    netflix_enabled = raw_input("Enable recently added Netflix list?(yes/no): \n")
    if str2bool(netflix_enabled):
        netflix_api = raw_input("Enter your Unogs API key: \n")
        netflix_country = raw_input("Enter the Netflix country code you want to use(e.g. GB, US or ES): \n")
        netflix_days = raw_input("Enter how many days back to check: \n")
    else:
        netflix_api = ''
        netflix_country = ''
        netflix_days = ''

    print '\033[93m' + "\nIf you have selected more then one list, it is highly recommended that\n" \
                       "you add filters to avoid spamming Soanrr with rubbish content\n" + '\x1b[0m'

    filters_rating = raw_input("Enter the minimum rating a show must have to be added: \n")
    # filters_genre = raw_input("Enter the minimum rating a show must have to be added: \n")
    filters_lang = raw_input("Enter the two letter country code for the language a show must be in(e.g. en): \n")
    filters_end = raw_input("Do you want to add shows that have finished?(yes/no): \n")
    filters_cancel = raw_input("Do you want to add shows that have been cancelled?(yes/no): \n")

    fresh_config = {
        "sonarr": {"host": sonarr_host, "quality_profile": sonarr_quality_profile, "folder_path": sonarr_folder_path,
                   "api": sonarr_api}, "trakt": {"api": trakt_api, "limit": 0,
                                                 "list": {"anticipated": str2bool(trakt_list_anticipated),
                                                          "popular": str2bool(trakt_list_popular),
                                                          "trending": str2bool(trakt_list_trending)}},
        "pingrr": {"timer": int(pingrr_timer), "limit": int(pingrr_limit), "log_level": "info"},
        "pushover": {"enabled": str2bool(pushover), "user_token": pushover_user_token, "app_token": pushover_app_token},
        "slack": {"enabled": str2bool(slack), "webhook_url": slack_webhook_url, "sender_name": "Pingrr",
                  "sender_icon": ":robot_face:", "channel": slack_channel},
        "filters": {"rating": int(filters_rating), "genre": [""], "language": filters_lang,
                    "allow_ended": str2bool(filters_end), "allow_canceled": str2bool(filters_cancel)},
        "unogs": {"api": netflix_api, "country": netflix_country, "days": netflix_days}}

    with open('config.json', 'w') as outfile:
        json.dump(fresh_config, outfile)

    print '\033[93m' + "\nIf you have selected more then one list, it is highly recommended that\n" \
                       "you add filters to avoid spamming Soanrr with rubbish content\n" + '\x1b[0m'

    if str2bool(raw_input("Config file created, would you like to start Pingrr now?(yes/no)")):
        pass
    else:
        logger.info('config file created, stopping pingrr')
        sys.exit()

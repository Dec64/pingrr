import logging
import argparse
import sys
import os
import json
import requests

################################
# Logging
################################

logger = logging.getLogger(__name__)

################################
# Config class
################################


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]


class Config(object):
    __metaclass__ = Singleton

    base_settings = {
        'config': {
            'argv': '--config',
            'env': 'PINGRR_CONFIG',
            'default': os.path.join(os.path.dirname(sys.argv[0]), 'config.json')
        },
        'logfile': {
            'argv': '--logfile',
            'env': 'PINGRR_LOGFILE',
            'default': os.path.join(os.path.dirname(sys.argv[0]), 'logs', 'pingrr.log')
        },
        'loglevel': {
            'argv': '--loglevel',
            'env': 'PINGRR_LOGLEVEL',
            'default': 'INFO'
        },
        'blacklist': {
            'argv': '--blacklist',
            'env': 'PINGRR_BLACKLIST',
            'default': os.path.join(os.path.dirname(sys.argv[0]), 'blacklist.json')
        }
    }

    def __init__(self):
        """Initializes config"""
        # Args and settings
        self.args = self.parse_args()
        self.settings = self.get_settings()
        # Config
        self.config = None
        self.blacklist = set()

    # Parse command line arguments
    def parse_args(self):
        parser = argparse.ArgumentParser(
            description=(
                "Checks lists on Trakt and Netflix's recently added shows, and if they \n"
                "meet your configured filters, adds them to your sonarr library."
            ),
            formatter_class=argparse.RawTextHelpFormatter
        )

        # Config file
        parser.add_argument(
            self.base_settings['config']['argv'],
            '-c',
            nargs='?',
            const=None,
            help='Config file location (default: %s)' % self.base_settings['config']['default']
        )

        # Log file
        parser.add_argument(
            self.base_settings['logfile']['argv'],
            nargs='?',
            const=None,
            help='Log to the file (default: %s)' % self.base_settings['logfile']['default']
        )

        # Logging level
        parser.add_argument(
            self.base_settings['loglevel']['argv'],
            choices=('WARN', 'INFO', 'DEBUG'),
            help='Log level (default: %s)' % self.base_settings['loglevel']['default']
        )

        # Blacklist file
        parser.add_argument(
            self.base_settings['blacklist']['argv'],
            nargs='?',
            const=None,
            help='Blacklist file (default: %s)' % self.base_settings['blacklist']['default']
        )

        return vars(parser.parse_args())

    def get_settings(self):
        setts = {}
        for name, data in self.base_settings.items():
            # Argrument priority: cmd < environment < default
            try:
                value = None
                # Command line argument
                if self.args[name]:
                    value = self.args[name]
                    logger.info("Using ARG setting %s=%s", name, value)

                # Envirnoment variable
                elif data['env'] in os.environ:
                    value = os.environ[data['env']]
                    logger.info("Using ENV setting %s=%s" % (
                        data['env'],
                        value
                    ))

                # Default
                else:
                    value = data['default']
                    logger.info("Using default setting %s=%s" % (
                        data['argv'],
                        value
                    ))

                setts[name] = value

            except Exception:
                logger.exception("Exception retrieving setting value: %r" % name)

        return setts

    def save_blacklist(self):
        with open(self.settings['blacklist'], 'w') as data_file:
            json.dump(
                {"blacklist": list(self.blacklist)},
                data_file
            )

    def load_blacklist(self):
        try:
            with open(self.settings['blacklist']) as data_file:
                self.blacklist = set(json.load(data_file)['blacklist'])

        except IOError:
            logger.info("No blacklist file, creating a blank file now.")
            self.save_blacklist()

        except (TypeError, IndexError, ValueError):
            logger.warning("Blacklist file contains invalid syntax, please check.")
            sys.exit(1)

    def load(self):
        if os.path.exists(self.settings['config']):
            with open(self.settings['config'], 'r') as f:
                self.config = json.load(f)

        else:
            logger.warn("No config file found, creating new config.")
            self.create_config(self.settings['config'])

        # Load blacklist
        self.load_blacklist()

    ################################
    # Create config
    ################################

    @staticmethod
    def ask_year(low, high):
        while True:
            try:
                number = int(raw_input("What is the minimum year to grab a tv show from? (0 for all ): \n"))
            except ValueError:
                continue
            if low <= number <= high:
                return number

    @staticmethod
    def ask_rating():
        while True:
            try:
                number = int(raw_input("Enter the minimum rating a show must have to be added (0-10) \n"))
            except ValueError:
                continue
            if 0 <= number <= 10:
                return number

    @staticmethod
    def genre_list():
        string_input = raw_input("Enter which genres you do NOT want to grab(Enter to skip/allow all): \n")
        string_input = string_input.lower()
        created_list = string_input.split()
        return created_list

    @staticmethod
    def get_quality_profiles(sonarr_url, key):
        url = sonarr_url
        r = requests.get(url + '/api/profile', headers={'X-Api-Key': key}, timeout=30)
        data = r.json()
        for profile in data:
            if profile['name']:
                print("{}: {}".format(profile['id'], profile['name']))
        wanted = ''
        while wanted is not int and len(data) < wanted:
            try:
                wanted = int(raw_input("Which quality profile do you want to download shows with?: \n"))
            except ValueError:
                print("Please enter the ID of your profile you want")
                continue
        return wanted

    @staticmethod
    def check_api(sonarr_url, api_key):
        url = sonarr_url
        r = requests.get(url + '/api/system/status', headers={'X-Api-Key': api_key}, timeout=30)
        if r.status_code == 200:
            return True
        else:
            return False

    @staticmethod
    def check_host(sonarr_url):
        url = sonarr_url
        try:
            r = requests.get(url + '/api/system/status', timeout=30)
            if r.status_code == 401:
                return True
            else:
                return False
        except Exception:
            return False

    @staticmethod
    def str2bool(v):
        return str(v).lower() in ("yes", "true", "t", "1", "y")

    def create_config(self, arg_loc):
        print '\033[93m' + "\nPingrr has no config, please follow the instructions to create one\n" + '\x1b[0m'

        print "\n"
        print "####################################\n" \
              "############ SONARR ################\n" \
              "####################################\n"

        sonarr_host = raw_input("Enter URL for your sonarr server, normally http://localhost:8989: \n")
        while not self.check_host(sonarr_host):
            try:
                sonarr_host = raw_input("Sonarr URL invalid, check URL and try again: \n")
            except Exception:
                print "Error getting host, try again"
        print '\033[94m' + str(sonarr_host) + '\x1b[0m' + '\n'

        sonarr_api = raw_input("Enter your sonarr API: \n")
        while not self.check_api(sonarr_host, sonarr_api):
            try:
                sonarr_api = raw_input("Sonarr API invalid, check API and try again: \n")
            except Exception:
                print "Error with api key, try again"
        print '\033[94m' + str(sonarr_api) + '\x1b[0m' + '\n'

        sonarr_folder_path = raw_input("Enter the folder path you want your shows to download to: \n")
        print '\033[94m' + str(sonarr_folder_path) + '\x1b[0m' + '\n'
        sonarr_quality_profile = self.get_quality_profiles(sonarr_host, sonarr_api)
        print '\033[94m' + str(sonarr_quality_profile) + '\x1b[0m' + '\n'

        sonarr_monitored = raw_input("Add TV Shows as monitored? (yes/no): \n")
        print '\033[94m' + str(self.str2bool(sonarr_monitored)) + '\x1b[0m' + '\n'

        sonarr_search_episodes = raw_input("Search for missing episodes? (yes/no): \n")
        print '\033[94m' + str(self.str2bool(sonarr_search_episodes)) + '\x1b[0m' + '\n'

        print "\n"
        print "####################################\n" \
              "############# TRAKT ################\n" \
              "####################################\n"

        trakt_api = raw_input("Enter your trakt.tv api key: \n")
        print '\033[94m' + str(trakt_api) + '\x1b[0m' + '\n'
        trakt_list_anticipated = raw_input("Do you want to use Trakt's anticipated list? (yes/no): \n")
        print '\033[94m' + str(self.str2bool(trakt_list_anticipated)) + '\x1b[0m' + '\n'
        trakt_list_popular = raw_input("Do you want to use Trakt's popular list? (yes/no): \n")
        print '\033[94m' + str(self.str2bool(trakt_list_popular)) + '\x1b[0m' + '\n'
        trakt_list_trending = raw_input("Do you want to use Trakt's trending list? (yes/no): \n")
        print '\033[94m' + str(self.str2bool(trakt_list_trending)) + '\x1b[0m' + '\n'

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
        print '\033[94m' + str(self.str2bool(notifications_wanted)) + '\x1b[0m' + '\n'
        if self.str2bool(notifications_wanted):
            pushover = raw_input("Enable Pushover notifications?(yes/no): \n")
            print '\033[94m' + str(self.str2bool(pushover)) + '\x1b[0m' + '\n'
            if self.str2bool(pushover):
                pushover_user_token = raw_input("Enter your pushover user token: \n")
                print '\033[94m' + str(pushover_user_token) + '\x1b[0m' + '\n'
                pushover_app_token = raw_input("Enter your pushover app token: \n")
                print '\033[94m' + str(pushover_app_token) + '\x1b[0m' + '\n'
            else:
                pushover_user_token = ''
                pushover_app_token = ''
            slack = raw_input("Enable Slack notifications?(yes/no): \n")
            print '\033[94m' + str(self.str2bool(slack)) + '\x1b[0m' + '\n'
            if self.str2bool(slack):
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

        print "\n"
        # print "####################################\n" \
        #       "############ NETFLIX ###############\n" \
        #       "####################################\n"
        # allflicks_enabled = raw_input("Enable recently added Netflix list?(yes/no): \n")
        # print '\033[94m' + str(self.str2bool(allflicks_enabled)) + '\x1b[0m' + '\n'
        #
        # print "\n"
        print "####################################\n" \
              "############ FILTERS ###############\n" \
              "####################################\n"

        print '\033[93m' + "\nIf you have selected more then one list, it is highly recommended that\n" \
                           "you add filters to avoid spamming Soanrr with rubbish content\n" + '\x1b[0m'

        filters_rating = self.ask_rating()
        print '\033[94m' + str(filters_rating) + '\x1b[0m' + '\n'
        filters_genre = self.genre_list()
        print '\033[94m' + str(filters_genre) + '\x1b[0m' + '\n'
        filters_lang = raw_input("Enter the two letter language code for the language a show must be in(e.g. en): \n")
        print '\033[94m' + str(filters_lang) + '\x1b[0m' + '\n'
        filters_year = self.ask_year(0, 3000)
        print '\033[94m' + str(filters_year) + '\x1b[0m' + '\n'
        filters_end = raw_input("Do you want to add shows that have finished?(yes/no): \n")
        print '\033[94m' + str(self.str2bool(filters_end)) + '\x1b[0m' + '\n'
        filters_cancel = raw_input("Do you want to add shows that have been cancelled?(yes/no): \n")
        print '\033[94m' + str(self.str2bool(filters_cancel)) + '\x1b[0m' + '\n'
        filters_runtime = raw_input("What is the minimum runtime for a show to be grabbed?: \n")
        print '\033[94m' + filters_runtime + '\x1b[0m' + '\n'
        filters_votes = raw_input("What is the minimum number of votes for a show to be grabbed?: \n")
        print '\033[94m' + filters_votes + '\x1b[0m' + '\n'

        fresh_config = {
            "sonarr": {
                "host": sonarr_host,
                "quality_profile": sonarr_quality_profile,
                "folder_path": sonarr_folder_path,
                "api": sonarr_api,
                "monitored": self.str2bool(sonarr_monitored),
                "search_missing_episodes": self.str2bool(sonarr_search_episodes),
                "genre_paths": False,
                "path_root": "/mnt/media/",
                "paths": {
                    "Anime": ["anime"],
                    "Kids-TV": ["children, family"],
                    "Doc-TV": ["documentary"],
                    "Reality-TV": ["reality", "game-show"]}
            },
            "radarr": {
                "host": "localhost:7878",
                "quality_profile": "1",
                "folder_path": "/mnt/movies",
                "api": "",
                "monitored": True,
                "genre_paths": False,
                "path_root": "/mnt/media/",
                "paths": {
                    "Anime-movies": ["anime"],
                    "Kids": ["children, family"],
                    "Docs": ["documentary"]
                }
            },
            "trakt": {
                "api": trakt_api,
                "imdb_info": False,
                "limit": 0,
                "tv_list": {
                    "anticipated": self.str2bool(trakt_list_anticipated),
                    "popular": self.str2bool(trakt_list_popular),
                    "trending": self.str2bool(trakt_list_trending)
                },
                "movie_list": {
                    "anticipated": False,
                    "popular": False,
                    "trending": False
                }
            },
            "pingrr": {
                "limit": {
                    "sonarr": int(pingrr_limit),
                    "radarr": 0
                },
                "timer": int(pingrr_timer),
                "log_level": "info",
                "aired": 0,
                "dry_run": False
            },
            "pushover": {
                "enabled": self.str2bool(pushover),
                "user_token": pushover_user_token,
                "app_token": pushover_app_token
            },
            "slack": {
                "enabled": self.str2bool(slack),
                "webhook_url": slack_webhook_url,
                "sender_name": "Pingrr",
                "sender_icon": ":robot_face:",
                "channel": slack_channel
            },
            "filters": {
                "rating": int(filters_rating),
                "genre": filters_genre,
                "language": filters_lang,
                "allow_ended": self.str2bool(filters_end),
                "allow_canceled": self.str2bool(filters_cancel),
                "runtime": int(filters_runtime),
                "votes": int(filters_votes),
                "network": "",
                "country": "",
                "year": {
                    "movies": 0,
                    "shows": filters_year
                    }
            },
            "just_watch": {
                "enabled": {
                    "movies": False,
                    "shows": False
                },
                "country": 'US',
                "pages": 1
            }
        }

        with open(arg_loc, 'w') as outfile:
            json.dump(fresh_config, outfile, indent=4, sort_keys=True)

        logger.info('config file created, please check config and re-run Pingrr')
        sys.exit()

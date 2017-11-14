import logging
import config
import requests
import re
import trakt
import urllib
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

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

headers = {
    'content-type': 'application/json',
    'trakt-api-version': '2',
    'trakt-api-key': conf['trakt']['api']
}

################################
# get cookie info
################################


def get_ident():
    page = requests.get("https://www.allflicks.net")
    data = page.content
    pattern = re.compile(r'identifier=(\w*)', re.MULTILINE | re.DOTALL)
    soup = BeautifulSoup(data, "html.parser")
    script = soup.find("script", text=pattern)
    if script:
        match = pattern.search(script.text)
        if match:
            ident = match.group(1)
            return ident


################################
# Main
################################


def format_string(text_input):
    string = text_input
    pattern = re.compile('\W')
    string = re.sub(pattern, '', string)
    return string


def get_info_search(tv_id):
    """Get info for a tv show"""
    url = "https://api.trakt.tv/search/show?query=" + urllib.quote_plus(tv_id) + "&extended=full"
    logger.debug('getting info from trakt for ' + tv_id)
    r = requests.get(url=url, headers=headers, timeout=10)
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


def create_list():
    with requests.session() as req:
        head = {'Accept-Language': 'en-US,en;q=0.8,pt-PT;q=0.6,pt;q=0.4',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                              '(KHTML, like Gecko) Chrome/61.0.3163.59 Safari/537.36', 'Connection': 'keep-alive',
                'DNT': '1',
                'cookie': 'identifier=' + get_ident()
                }
        resp = req.get("https://www.allflicks.net", headers=head)
        if resp.status_code == 200:
            logger.debug("sending payload to processing_us.php")
            params = {
                "draw": 1,
                "columns[0][data]": "box_art",
                "columns[0][name]": "",
                "columns[0][searchable]": "true",
                "columns[0][orderable]": "false",
                "columns[0][search][value]": "",
                "columns[0][search][regex]": "false",
                "columns[1][data]": "title",
                "columns[1][name]": "",
                "columns[1][searchable]": "true",
                "columns[1][orderable]": "true",
                "columns[1][search][value]": "",
                "columns[1][search][regex]": "false",
                "columns[2][data]": "year",
                "columns[2][name]": "",
                "columns[2][searchable]": "true",
                "columns[2][orderable]": "true",
                "columns[2][search][value]": "",
                "columns[2][search][regex]": "false",
                "columns[3][data]": "genre",
                "columns[3][name]": "",
                "columns[3][searchable]": "true",
                "columns[3][orderable]": "false",
                "columns[3][search][value]": "",
                "columns[3][search][regex]": "false",
                "columns[4][data]": "rating",
                "columns[4][name]": "",
                "columns[4][searchable]": "true",
                "columns[4][orderable]": "true",
                "columns[4][search][value]": "",
                "columns[4][search][regex]": "false",
                "columns[5][data]": "available",
                "columns[5][name]": "",
                "columns[5][searchable]": "true",
                "columns[5][orderable]": "true",
                "columns[5][search][value]": "",
                "columns[5][search][regex]": "false",
                "columns[6][data]": "director",
                "columns[6][name]": "",
                "columns[6][searchable]": "true",
                "columns[6][orderable]": "true",
                "columns[6][search][value]": "",
                "columns[6][search][regex]": "false",
                "columns[7][data]": "cast",
                "columns[7][name]": "",
                "columns[7][searchable]": "true",
                "columns[7][orderable]": "true",
                "columns[7][search][value]": "",
                "columns[7][search][regex]": "false",
                "order[0][column]": 5,
                "order[0][dir]": "desc",
                "start": 0,
                "length": 100,
                "search[value]": "",
                "search[regex]": "false",
                "movies": "false",
                "shows": "true",
                "documentaries": "false",
                "min": 1900,
                "max": 2017
            }

            headers2 = {
                'Origin': 'https://www.allflicks.net',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.8,pt-PT;q=0.6,pt;q=0.4',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                              '(KHTML, like Gecko) Chrome/61.0.3163.59 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': 'https://www.allflicks.net/genre/tv-shows/', 'X-Requested-With': 'XMLHttpRequest',
                'Connection': 'keep-alive',
                'DNT': '1',
                'cookie': 'identifier=' + get_ident()
            }

            resp = req.post(
                "https://www.allflicks.net/wp-content/themes/responsive/processing/processing_us.php",
                data=params,
                headers=headers2
            )

            if resp.status_code == 200:
                logger.info('creating list from allflicks.net')
                shows = resp.json()
                y = []
                for tv in shows['data']:
                    try:
                        x = trakt.search(tv['title'], "show", "search")
                        title1 = x[0]['title']
                        title2 = tv['title']
                        s1 = fuzz.token_sort_ratio(title1, title1)
                        s2 = fuzz.partial_ratio(title1, title2)
                        average = (s1 + s2) / 2
                        if title1 == title2:
                            y.append(x)
                            logger.debug("match found for: " + x[0]['title'] + " / " + tv['title'])
                            continue
                        if format_string(title1) == format_string(title2):
                            y.append(x)
                            logger.debug("match found for: " + x[0]['title'] + " / " + tv['title'])
                            continue
                        elif x[0]['year'] == tv['year']:
                            average += 10
                            if average >= conf['allflicks']['rating_match']:
                                y.append(x)
                                logger.debug("match found for: " + x[0]['title'] + " / " + tv['title'])
                                continue
                        else:
                            logger.debug("no match found for: " + x[0]['title'] + " / " + tv['title'])
                    except Exception:
                        logger.debug("no match on trakt for title: " + tv['title'])
            logger.info('Allflicks list created, ' + str(len(y)) + ' shows found')
            return y

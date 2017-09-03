![alt text](http://img.pixady.com/2017/09/143837_pingrr_460x168.png)<br />
# pingrr.
Python script that checks certain lists on [Trakt](http://trakt.tv) and [Netflix's](https://www.allflicks.net/) recently added shows, and if they meet your configured filters, adds them to your sonarr library.
Sonarr Pusher will check the trakt.tv lists every 24 hours by default to keep sonarr constantly updated with new TV shows

Currently supports:
1. [Trakt Trending](https://trakt.tv/shows/trending)
2. [Trakt Anticipated](https://trakt.tv/shows/anticipated)
3. [Trakt Popular](https://trakt.tv/shows/popular)
4. [Netflix recently added](https://www.allflicks.net/)

## Getting Started

You will need a trakt.tv account with a [Trakt api key](https://trakt.tv/oauth/applications/new),
as well as your sonarr API.

Quick warning when setting up the script. If you activate lots of lists with no filters,
you will get a lot of shows that you may not want.
At minimum it is recommended to use the language code filter and limit shows added per run.

### Prerequisites

You will need a Trakt account and an api key (client ID),
you can create a new API app in trakt [here](https://trakt.tv/oauth/applications/new)

1. Python 2.7
2. requests 2.18.4
3. BeautifulSoup 3.2.1
4. fuzzywuzzy 0.15.1

`
sudo apt-get install python
`

`
pip install -r requirements.txt
`

### Installing

`git clone https://github.com/Dec64/pingrr.git`

`cd pingrr`

`python pingrr.py`

Follow the insutrctions in the console to complete the configuration file.
This is only needed on the first run. Once complete you will need to re run pingrr.

`python pingrr.py`

If you intend to leave it running, it would be best to use systemd startup or screen.

`screen -S pingrr python pingrr.py``

Check it's all running fine by tailing the log

`tail -f logs/pingrr.log`

### Todo

1. Radarr support for netflix list
2. More list sources if found
3. Easier config generation
4. Command line arguments.e.g <br />
`python pingrr.py --conf /my/config/location/conf.json`
`python pingrr.py --quality_profile 720p`

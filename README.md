![alt text](http://img.pixady.com/2017/09/143837_pingrr.png)<br />
# pingrr.
Python script that checks certain lists on [Trakt](http://trakt.tv) and [Netflix's](https://www.allflicks.net/) recently added shows, as well as
 [JustWatch](https://www.justwatch.com/)'s recent shows and if they meet your configured filters, adds them to your sonarr library.

Currently supports:
1. [Trakt Trending](https://trakt.tv/shows/trending)
2. [Trakt Anticipated](https://trakt.tv/shows/anticipated)
3. [Trakt Popular](https://trakt.tv/shows/popular)
4. [Netflix recently added](https://www.allflicks.net/)
5. [Just Watch recently added](https://www.justwatch.com/)

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
2. requests
3. BeautifulSoup
4. fuzzywuzzy

`sudo apt-get install python`

`pip install -r requirements.txt`

### Installing

`git clone https://github.com/Dec64/pingrr.git`

`cd pingrr`

`python pingrr.py`

Follow the insutrctions in the console to complete the configuration file.
This is only needed on the first run. Once complete you will need to re run pingrr.

`python pingrr.py`

If you intend to leave it running, it would be best to use systemd startup or screen.

`screen -S pingrr python pingrr.py`

Check it's all running fine by tailing the log

`tail -f logs/pingrr.log`


### Command line arguments

If you want to define a config location for pingrr (running multiple
instances with different categories/folder locations/lists) you can define
the config location via:

- Command line by using `-c` or `--config=`:
  - `python pingrr.py -c /my/config/location/conf.json`
  - `python pingrr.py --config=/my/config/location/conf.json`


- Environment variable by setting `PINGRR_CONFIG`:
  - `PINGRR_CONFIG=/my/config/location/conf.json python pingrr.py`

Logging level can be increased if you are having issues and want more output in the log/console by using `--loglevel`:
- `python pingrr.py --loglevel=DEBUG`

To list all possible arguments and options run:
- `python pingrr.py -h`

### Blacklist

There is a blacklist.json file created on first run. This file will
have failed shows and any show you want to add to it outside of filters that
you never want to add. To add a show, either use the shows IMDB id or TVDB id.

```
{"blacklist": ["imdb id", "or tvdb id", "332493", "75760", "79168", "334069"]}
```

### Just Watch

https://www.justwatch.com/

Early support for justwatch is included.

```
    "just_watch": {
        "enabled": true,
        "country": "GB",
        "pages": "1"
    }
```

Each page is a single day, so if you set 1 page, it will check against
all services justwatch supports in your chosen country for the last day.

Set more pages to scan back more days, doing this will cause the scan to
take longer and potentially add a lot of shows.

Should support any two letter country code that Just Watch has data for.

E.g:
```
Germany
Austria
Switzerland
United Kingdom
Ireland
Russia
Italy
France
Spain
Netherlands
Norway
Sweden
Denmark
Finland
Lithuania
Latvia
Estonia
USA
Canada
Mexico

and more
```

### Config

There are a few config settings that are not set by the user on first run,
if you fancy messing with more advanced settings you can open up the config.json
file and change as needed.

`"rating_match":94` <br />
How close the match has to be out of 100 when parsing netflix titles.
If you feel you are missing some titles feel free to play with this figure, but anything lower
then 90 will most likely result in incorrect matches.

For the unwanted genres list, you need to type them as found on imdb, here are some examples:

```
comedy
action
drama
fantasy
science-fiction
adventure
reality
superhero
crime
mystery
horror
thriller
romance
animation
children
home-and-garden
anime
family
documentary
game-show
suspense
```

### Start on boot

To have pingrr start on boot on ubuntu

`cd /opt`

`git clone https://github.com/Dec64/pingrr.git`

run pingrr, and complete the config.

`sudo nano /etc/systemd/system/pingrr.service`

copy and paste the below, after editing `User=` and `Group=`

```
[Unit]
Description=pingrr
After=network-online.target

[Service]
User=YOUR_USER
Group=YOUR_USER
Type=simple
WorkingDirectory=/opt/pingrr/
ExecStart=/usr/bin/python /opt/pingrr/pingrr.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

Then enabled and start it with:

`sudo systemctl enable pingrr.service`

`sudo systemctl start pingrr`

***

If you are have set pingrr to not loop (setting the timer to 0) then you
must remove `Restart=always RestartSec=10` from systemd file, otherwise it will restart every 10seconds.

### Todo

1. Radarr support
2. Learn python

### Thanks

Thanks to horjulf and l3uddz for assisting me with a few bits so far,
and everyone that helped test it along the way.

If you have any suggestions for features ect, feel free to create a new issue
on github for it!

### Donate

If you absolutely feel the need to donate, the link is below.
Pull requests and help cleaning up my amateur python would be more helpful :)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/Dec64)
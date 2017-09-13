# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale per http://bleachportal.it
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# By MrTruth
# ------------------------------------------------------------

import re

from core import httptools
from core import logger
from core import scrapertools
from core.item import Item

__channel__ = "bleachportal"

host = "http://bleachportal.it"

headers = [['Referer', host]]


def mainlist(item):
    logger.info("[BleachPortal.py]==> mainlist")
    itemlist = [Item(channel=__channel__,
                     action="episodi",
                     title="[COLOR azure] Bleach [/COLOR] - [COLOR deepskyblue]Lista Episodi[/COLOR]",
                     url=host + "/streaming/bleach/stream_bleach.htm",
                     thumbnail="http://i45.tinypic.com/286xp3m.jpg",
                     fanart="http://i40.tinypic.com/5jsinb.jpg",
                     extra="bleach"),
                Item(channel=__channel__,
                     action="episodi",
                     title="[COLOR azure] D.Gray Man [/COLOR] - [COLOR deepskyblue]Lista Episodi[/COLOR]",
                     url=host + "/streaming/d.gray-man/stream_dgray-man.htm",
                     thumbnail="http://i59.tinypic.com/9is3tf.jpg",
                     fanart="http://wallpapercraft.net/wp-content/uploads/2016/11/Cool-D-Gray-Man-Background.jpg",
                     extra="dgrayman")
                ]

    return itemlist


def episodi(item):
    logger.info("[BleachPortal.py]==> episodi")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = '<td>?[<span\s|<width="\d+%"\s]+?class="[^"]+">\D+([\d\-]+)\s?<[^<]+<[^<]+<[^<]+<[^<]+<.*?\s+?.*?<span style="[^"]+">([^<]+).*?\s?.*?<a href="\.*(/?[^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(data)

    animetitle = "Bleach" if item.extra == "bleach" else "D.Gray Man"
    for scrapednumber, scrapedtitle, scrapedurl in matches:
        scrapedtitle = scrapedtitle.decode('latin1').encode('utf8')
        itemlist.append(Item(channel=__channel__,
                             action="findvideos",
                             title="[COLOR azure]" + animetitle + " Ep: [/COLOR][COLOR deepskyblue] " + scrapednumber + " [/COLOR]",
                             url=item.url.replace("stream_bleach.htm",scrapedurl) if "stream_bleach.htm" in item.url else item.url.replace("stream_dgray-man.htm", scrapedurl),
                             plot=scrapedtitle,
                             extra=item.extra,
                             thumbnail=item.thumbnail,
                             fanart=item.fanart,
                             fulltitle="[COLOR red]" + animetitle + " Ep: " + scrapednumber + "[/COLOR] | [COLOR deepskyblue]" + scrapedtitle + "[/COLOR]",
                             show=animetitle))

    if item.extra == "bleach":
        itemlist.append(Item(channel=__channel__,
                             action="oav",
                             title="[COLOR azure] OAV e Movies [/COLOR]",
                             url=item.url.replace("stream_bleach.htm", "stream_bleach_movie_oav.htm"),
                             extra=item.extra,
                             thumbnail=item.thumbnail,
                             fanart=item.fanart
                             ))

    return list(reversed(itemlist))


def oav(item):
    logger.info("[BleachPortal.py]==> oav")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = '<td>?[<span\s|<width="\d+%"\s]+?class="[^"]+">-\s+(.*?)<[^<]+<[^<]+<[^<]+<[^<]+<.*?\s+?.*?<span style="[^"]+">([^<]+).*?\s?.*?<a href="\.*(/?[^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapednumber, scrapedtitle, scrapedurl in matches:
        itemlist.append(Item(channel=__channel__,
                             action="findvideos",
                             title="[COLOR deepskyblue] " + scrapednumber + " [/COLOR]",
                             url=item.url.replace("stream_bleach_movie_oav.htm", scrapedurl),
                             plot=scrapedtitle,
                             extra=item.extra,
                             thumbnail=item.thumbnail,
                             fulltitle="[COLOR red]" + scrapednumber + "[/COLOR] | [COLOR deepskyblue]" + scrapedtitle + "[/COLOR]",
                             show="Bleach"))

    return list(reversed(itemlist))


def findvideos(item):
    logger.info("[BleachPortal.py]==> findvideos")
    itemlist = []

    if "bleach//" in item.url:
        newurl = re.sub(r'\w+//', "", item.url)
    else:
        newurl = item.url

    data = httptools.downloadpage(newurl).data

    if "bleach" in item.extra:
        video = scrapertools.find_single_match(data, 'file: "(.*?)",')
    else:
        video = scrapertools.find_single_match(data, 'file=(.*?)&')
        video = video.rsplit('/', 1)[-1]

    newurl = newurl.replace(newurl.split("/")[-1], "/" + video)
    estensionevideo = video.split(".")[-1]

    itemlist.append(Item(channel=__channel__,
                         action="play",
                         title=item.title + "[." + estensionevideo + "]",
                         url=newurl,
                         thumbnail=item.thumbnail,
                         fulltitle=item.fulltitle,
                         show=item.fulltitle))
    return itemlist

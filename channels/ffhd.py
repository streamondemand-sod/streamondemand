# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale per http://altadefinizionehd.com/
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# By DrZ3r0
# ------------------------------------------------------------

import re

from core import logger, httptools, config
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod
from servers.decrypters import adfly

__channel__ = "ffhd"

host = "http://www.ffhd.pw"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', host]
]


# ----------------------------------------------------------------------------------------------------------------
def mainlist(item):
    logger.info("[AltadefinizioneHD.py]==> mainlist")
    itemlist = [
        Item(channel=__channel__,
             action="film",
             title=color("Ultimi film", "azure"),
             url="%s/movies" % host,
             thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png", ),
        Item(channel=__channel__,
             action="film",
             title=color("Top IMDb", "azure"),
             url="%s/top-imdb" % host,
             thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png", ),
        Item(channel=__channel__,
             action="serietv",
             title=color("SerieTV", "green"),
             url="%s/series" % host,
             thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png", ),
        Item(channel=__channel__,
             action="search",
             title=color("Cerca", "yellow"),
             url=host,
             thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search", )
    ]

    return itemlist


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def search(item, texto):
    logger.info("[ffHD.py]==> search")
    item.url = "%s/?s=%s" % (host, texto)
    item.extra = "movie"
    try:
        return film(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def film(item):
    logger.info("[ffHD.py]==> film")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    start = data.find('<div class="movies-list movies-list-full">')
    end = data.find('<div id="pagination"', start)
    blocco = data[start:end]
    patron = r'<a href="([^"]+)"[^>]+>[^>]+>[^>]+><img data-original="([^"]+)"[^>]+>[^>]+><h2>([^<]+)</h2>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedimg, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        if "/adult/" not in scrapedurl:
            itemlist.append(infoSod(
                Item(channel=__channel__,
                     action="findvideos",
                     title=scrapedtitle,
                     fulltitle=scrapedtitle,
                     url=scrapedurl,
                     thumbnail=scrapedimg.strip(),
                     extra=item.extra,
                     folder=True), tipo="movie"))


    patron = r'<li class="active"><a class>\d</a></li><li><a rel="nofollow" class="page larger" href="([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(data[end:])

    if len(matches) > 0:
        scrapedurl = matches[0]
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title=color("Torna Home", "yellow"),
                 folder=True))
        itemlist.append(
            Item(channel=__channel__,
                 action="film",
                 title=color("Successivo >>", "orange"),
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def serietv(item):
    logger.info("[ffHD.py]==> serietv")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    start = data.find('<div class="movies-list movies-list-full">')
    blocco = data[start:]
    patron = r'<a href="([^"]+)"[^>]+><img data-original="([^"]+)"[^>]+>[^>]+><h2>([^<]+)</h2>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedimg, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedimg.strip(),
                 extra=item.extra,
                 folder=True), tipo="tv"))

    patron = r'<li class="active"><a class>\d</a></li><li><a rel="nofollow" class="page larger" href="([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    if len(matches) > 0:
        scrapedurl = matches[0]
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title=color("Torna Home", "yellow"),
                 folder=True))
        itemlist.append(
            Item(channel=__channel__,
                 action="film",
                 title=color("Successivo >>", "orange"),
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def episodios(item):
    logger.info("[ffHD.py]==> episodios")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    u = item.url.replace('series', 'episode')
    s = 1
    e = 1
    while s < 15:
        url = "%s-season-%d-episode-%d" % (u, s, e)
        if data.find(url) != -1:
            title = str(s).zfill(2) + "x" + str(e).zfill(2) + " - " + item.show

            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos",
                     contentType="episode",
                     title=title,
                     url=url,
                     fulltitle=title,
                     show=item.show,
                     thumbnail=item.thumbnail))
            e += 1
        else:
            e = 1
            s += 1

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))

    return itemlist


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def findvideos(item):
    logger.info("[ffHD.py]==> findvideos")

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'http://adf\.ly/[0-9a-zA-Z]+'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url in matches:
        data += adfly.get_long_url(url)

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        server = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(["[%s] " % color(server, 'orange'), item.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def color(text, color):
    return "[COLOR " + color + "]" + text + "[/COLOR]"


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")

# ================================================================================================================

# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale per cineblog01 - anime
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import re

from core import config, httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

__channel__ = "cb01anime"

host = "http://www.cineblog01.cc"


# -----------------------------------------------------------------
def mainlist(item):
    logger.info("[cb01anime.py] mainlist")

    # Main options
    itemlist = [Item(channel=__channel__,
                     action="novita",
                     title="[COLOR azure]Anime - Novita'[/COLOR]",
                     url="%s/anime/" % host,
                     thumbnail="http://orig09.deviantart.net/df5a/f/2014/169/2/a/fist_of_the_north_star_folder_icon_by_minacsky_saya-d7mq8c8.png"),
                Item(channel=__channel__,
                     action="genere",
                     title="[COLOR azure]Anime - Per Genere[/COLOR]",
                     url="%s/anime/" % host,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/Genres.png"),
                Item(channel=__channel__,
                     action="alfabetico",
                     title="[COLOR azure]Anime - Per Lettera A-Z[/COLOR]",
                     url="%s/anime/" % host,
                     thumbnail="http://i.imgur.com/IjCmx5r.png"),
                Item(channel=__channel__,
                     action="listacompleta",
                     title="[COLOR azure]Anime - Lista Completa[/COLOR]",
                     url="%s/anime/lista-completa-anime-cartoon/" % host,
                     thumbnail="http://i.imgur.com/IjCmx5r.png"),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR yellow]Cerca Anime[/COLOR]",
                     extra="anime",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


# =================================================================


# -----------------------------------------------------------------
def novita(item):
    logger.info("[cb01anime.py] mainlist")
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4"> <a.*?<img src="(.*?)".*?'
    patronvideos += '<div class="span8">.*?<a href="(.*?)">.*?'
    patronvideos += '<h1>(.*?)</h1></a>.*?<br />(.*?)<br>.*?'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        scrapedthumbnail = match.group(1)
        scrapedurl = match.group(2)
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedplot = scrapertools.unescape(match.group(4))
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        if scrapedplot.startswith(""):
            scrapedplot = scrapedplot[64:]

        ## ------------------------------------------------
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        ## ------------------------------------------------				

        # Añade al listado de XBMC
        itemlist.append(
            Item(channel=__channel__,
                 action="listacompleta" if scrapedtitle == "Lista Alfabetica Completa Anime/Cartoon" else "episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 viewmode="movie_with_plot",
                 plot=scrapedplot))

    # Put the next page mark
    try:
        next_page = scrapertools.get_match(data, "<link rel='next' href='([^']+)'")
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="novita",
                 title="[COLOR orange]Successivo>>[/COLOR]",
                 url=next_page,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"))
    except:
        pass

    return itemlist


# =================================================================


# -----------------------------------------------------------------
def genere(item):
    logger.info("[cb01anime.py] genere")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<select name="select2"(.*?)</select>')

    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="novita",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=host + scrapedurl))

    return itemlist


# =================================================================


# -----------------------------------------------------------------
def alfabetico(item):
    logger.info("[cb01anime.py] listacompleta")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<option value=\'-1\'>Anime per Lettera</option>(.*?)</select>')

    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">\(([^<]+)\)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = url
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="novita",
                 title=scrapedtitle,
                 url=host + scrapedurl,
                 thumbnail="http://www.justforpastime.net/uploads/3/8/1/5/38155083/273372_orig.jpg",
                 plot=scrapedplot))

    return itemlist


# =================================================================


# -----------------------------------------------------------------
def listacompleta(item):
    logger.info("[cb01anime.py] listacompleta")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    # Narrow search by selecting only the combo
    patron = '<a href="#char_5a" title="Go to the letter Z">Z</a></span></div>(.*?)</ul></div><div style="clear:both;"></div></div>'
    bloque = scrapertools.get_match(data, patron)

    # The categories are the options for the combo  
    patron = '<li><a href="([^"]+)"><span class="head">([^<]+)</span></a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = url
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="http://www.justforpastime.net/uploads/3/8/1/5/38155083/273372_orig.jpg",
                 plot=scrapedplot))

    return itemlist


# =================================================================


# -----------------------------------------------------------------
def search(item, texto):
    logger.info("[cb01anime.py] " + item.url + " search " + texto)

    item.url = host + "/anime/?s=" + texto

    return novita(item)


# =================================================================


# -----------------------------------------------------------------
def episodios(item):
    logger.info("[cb01anime.py] episodios")

    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    data = scrapertools.decodeHtmlentities(data)

    patron1 = '(?:<p>|<td bgcolor="#ECEAE1">)<span class="txt_dow">(.*?)(?:</p>)?(?:\s*</span>)?\s*</td>'
    patron2 = '<a.*?href="([^"]+)"[^>]*>([^<]+)</a>'
    matches1 = re.compile(patron1, re.DOTALL).findall(data)
    if len(matches1) > 0:
        for match1 in re.split('<br />|<p>', matches1[0]):
            if len(match1) > 0:
                # Extrae las entradas
                titulo = None
                scrapedurl = ''
                matches2 = re.compile(patron2, re.DOTALL).finditer(match1)
                for match2 in matches2:
                    if titulo is None:
                        titulo = match2.group(2)
                    scrapedurl += match2.group(1) + '#' + match2.group(2) + '|'
                if titulo is not None:
                    title = item.title + " " + titulo
                    itemlist.append(
                        Item(channel=__channel__,
                             action="findvideos",
                             contentType="episode",
                             title=title,
                             extra=scrapedurl,
                             fulltitle=item.fulltitle,
                             show=item.show))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))

    return itemlist


# =================================================================


# -----------------------------------------------------------------
def findvideos(item):
    logger.info("[cb01anime.py] findvideos")

    itemlist = []

    for match in item.extra.split(r'|'):
        match_split = match.split(r'#')
        scrapedurl = match_split[0]
        if len(scrapedurl) > 0:
            scrapedtitle = match_split[1]
            title = item.title + " [COLOR blue][" + scrapedtitle + "][/COLOR]"
            itemlist.append(
                Item(channel=__channel__,
                     action="play",
                     title=title,
                     url=scrapedurl,
                     fulltitle=item.fulltitle,
                     show=item.show,
                     folder=False))

    return itemlist


# =================================================================


# -----------------------------------------------------------------
def play(item):
    logger.info("[cb01anime.py] play")

    if '/goto/' in item.url:
        item.url = item.url.split('/goto/')[-1].decode('base64')

    item.url = item.url.replace('http://cineblog01.pw', 'http://k4pp4.pw')

    logger.debug("##############################################################")
    if "go.php" in item.url:
        data = httptools.downloadpage(item.url).data
        try:
            data = scrapertools.get_match(data, 'window.location.href = "([^"]+)";')
        except IndexError:
            try:
                # data = scrapertools.get_match(data, r'<a href="([^"]+)">clicca qui</a>')
                # In alternativa, dato che a volte compare "Clicca qui per proseguire":
                data = scrapertools.get_match(data, r'<a href="([^"]+)".*?class="btn-wrapper">.*?licca.*?</a>')
            except IndexError:
                data = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get(
                    "location")
        while 'vcrypt' in data:
            data = httptools.downloadpage(data, only_headers=True, follow_redirects=False).headers.get("location")
        logger.debug("##### play go.php data ##\n%s\n##" % data)
    elif "/link/" in item.url:
        data = httptools.downloadpage(item.url).data
        from lib import jsunpack

        try:
            data = scrapertools.get_match(data, "(eval\(function\(p,a,c,k,e,d.*?)</script>")
            data = jsunpack.unpack(data)
            logger.debug("##### play /link/ unpack ##\n%s\n##" % data)
        except IndexError:
            logger.debug("##### The content is yet unpacked ##\n%s\n##" % data)

        data = scrapertools.find_single_match(data, 'var link(?:\s)?=(?:\s)?"([^"]+)";')
        while 'vcrypt' in data:
            data = httptools.downloadpage(data, only_headers=True, follow_redirects=False).headers.get("location")
        logger.debug("##### play /link/ data ##\n%s\n##" % data)
    else:
        data = item.url
        logger.debug("##### play else data ##\n%s\n##" % data)
    logger.debug("##############################################################")

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.show
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")

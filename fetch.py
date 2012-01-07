#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of f33dme.
#
#  f33dme is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  f33dme is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with f33dme.  If not, see <http://www.gnu.org/licenses/>.
#
# (C) 2011- by Adam Tauber, <asciimoo@gmail.com>


import sys, os, re

sys.path.append('/home/stf/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'f33dme.settings'

from django.conf import settings
from f33dme.models import Item, Feed, Tag
from feedparser import parse
from datetime import datetime
from itertools import imap
from lxml.html.clean import Cleaner
from urlparse import urljoin, urlparse, urlunparse
from itertools import ifilterfalse, imap
import urllib, httplib
import tidy

cleaner = Cleaner(host_whitelist=['www.youtube.com'])

utmRe=re.compile('utm_(source|medium|campaign|content)=')
def urlSanitize(url):
    # handle any redirected urls from the feed, like
    # ('http://feedproxy.google.com/~r/Torrentfreak/~3/8UY1UySQe1k/')
    us=httplib.urlsplit(url)
    if us.scheme=='http':
        conn = httplib.HTTPConnection(us.netloc)
        req = url[7+len(us.netloc):]
    elif us.scheme=='https':
        conn = httplib.HTTPSConnection(us.netloc)
        req = url[8+len(us.netloc):]
    #conn.set_debuglevel(9)
    conn.request("HEAD", req)
    res = conn.getresponse()
    if res.status in [301, 304]:
        url = res.getheader('Location')
    # removes annoying UTM params to urls.
    pcs=urlparse(urllib.unquote_plus(url))
    tmp=list(pcs)
    tmp[4]='&'.join(ifilterfalse(utmRe.match, pcs.query.split('&')))
    return urlunparse(tmp)

def clean(txt):
    return unicode(str(tidy.parseString(txt, **{'output_xhtml' : 1,
                                                'add_xml_decl' : 0,
                                                'indent' : 0,
                                                'tidy_mark' : 0,
                                                'doctype' : "strict",
                                                'wrap' : 0})),'utf8')

def fetchFeed(feed):
    #print '[!] parsing %s - %s' % (feed.name, feed.url)
    counter = 0
    modified = feed.modified.timetuple() if feed.modified else None
    f = parse(feed.url, etag=feed.etag, modified=modified)
    if not f:
        print >>sys.stderr, '[!] cannot parse %s - %s' % (feed.name, feed.url)
        return
    try:
        feed.etag = f.etag
    except AttributeError:
        pass
    try:
        feed.modified = datetime(*f.modified[:6])
    except AttributeError:
        pass
    d = feed.updated
    for item in reversed(f['entries']):
        try:
           u = urlSanitize(item['links'][0]['href'])
        except:
           u = ''
        if feed.item_set.filter(url=u).all():
            continue

        try:
            tmp_date = datetime(*item['updated_parsed'][:6])
        except:
            tmp_date = datetime.now()

        # title content updated
        try:
            c = cleaner.clean_html(clean(unicode(''.join([x.value for x in item.content]))))
        except:
            c = u'No content found, plz check the feed and fix me =)'
            for key in ['media_text', 'summary', 'description', 'media:description']:
                if item.has_key(key):
                    try:
                        c = cleaner.clean_html(clean(unicode(item[key])))
                    except:
                        print u
                        print clean(unicode(item.get(key)))
                    break
        t = unicode(item.get('title',''))
        #if feed.item_set.filter(title=t).filter(content=c).all():
        if feed.item_set.filter(title=t,content=c).count()>0:
            continue
        # date as tmp_date?!
        new_item = Item(url=u, title=t, content=c, feed=feed, date=tmp_date)
        new_item.save()
        for tag in item.get('tags',[]):
            if tag.get('term'):
                tag=Tag.objects.get_or_create(tag=tag['term'], scheme=tag.get('scheme'))[0]
                if not new_item in tag.items.all():
                    tag.items.add(new_item)
        counter += 1
    feed.updated = d
    feed.save()
    return counter

if __name__ == '__main__':
    counter = sum(imap(fetchFeed, Feed.objects.all()))
    print '[!] %d item added' % counter

#!/usr/bin/env python2.6

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

sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'f33dme.settings'

from django.conf import settings
from f33dme.models import Item, Feed
from feedparser import parse
from datetime import datetime
from itertools import imap
from lxml.html.clean import Cleaner
from urlparse import urljoin, urlparse, urlunparse
from itertools import ifilterfalse, imap
import urllib
import tidy

cleaner = Cleaner(host_whitelist=['www.youtube.com'])

utmRe=re.compile('utm_(source|medium|campaign|content)=')
def urlSanitize(url):
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
    counter = 0
    modified = feed.modified.timetuple() if feed.modified else None
    f = parse(feed.url, etag=feed.etag, modified=modified)
    if not f:
        print '[!] cannot parse %s - %s' % (feed.name, feed.url)
        return
    #print '[!] parsing %s - %s' % (feed.name, feed.url)
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
                    c = cleaner.clean_html(clean(unicode(item[key])))
                    break
        t = unicode(item.get('title',''))
        try:
           u = urlSanitize(item['links'][0]['href'])
        except:
           u = ''
        #if feed.item_set.filter(title=t).filter(content=c).all():
        if feed.item_set.filter(url=u).filter(feed=feed).all():
            continue
        # date as tmp_date?!
        new_item = Item(url=u, title=t, content=c, feed=feed, date=tmp_date)
        new_item.save()
        counter += 1
    feed.updated = d
    feed.save()
    return counter

if __name__ == '__main__':
    counter = sum(imap(fetchFeed, Feed.objects.all()))
    print '[!] %d item added' % counter

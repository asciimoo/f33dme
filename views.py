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

from django.http import HttpResponse
from django.shortcuts import render_to_response
from models import Item, Feed
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from forms import FeedForm
from django.conf import settings
from django.db.models import Q

def _main_view(request, iall, template_vars={}):
    paging = settings.PAGING
    item_num = len(iall)
    pag = Paginator(iall, paging)
    page = int(request.GET.get('page', '1'))
    if request.is_ajax() and page > 2 and settings.INFINITE_SCROLL:
        page = 2
    try:
        items = pag.page(page)
    except (EmptyPage, InvalidPage):
        return HttpResponse(0)
    form = FeedForm()
    item_ids = ' '.join([item.id.__str__() for item in items.object_list])
    feeds = Feed.objects.filter(item__archived = False).distinct().all()
    tpl_dict = {'items': items, 'form': form, 'item_num': item_num, 'page_num': page, 'item_ids': item_ids, 'feeds': feeds, 'is_inf_scroll': settings.INFINITE_SCROLL}
    tpl_dict.update(template_vars)
    return render_to_response('index.html', tpl_dict)

def index(request):
    return _main_view(request, Item.objects.filter(archived=False).all())

def feed_view(request, f_id):
    return _main_view(request, Item.objects.filter(feed__id=f_id).all(), {'msg': 'F33d "%s"' % Feed.objects.filter(id=f_id).all()[0].name})

def search(request):
    q = request.GET.get('q')
    if not q:
        return HttpResponse('no search strings found')
    return _main_view(request, Item.objects.filter(Q(content__contains=q) | Q(title__contains=q)).all(), {'msg': 'Search result for "%s"' % q, 'q': q})

def add_feed(request):
    if request.method == 'POST':
        form = FeedForm(data=request.POST)
        if form.is_valid() and not Feed.objects.filter(url=form.cleaned_data['url']).all():
            event = form.save()
            return HttpResponse('OK')
            #return HttpResponseRedirect("%s" % post.get_nice_url())
    else:
        form = FeedForm()
    return HttpResponse('0')

def remove_feed(request):
    if request.method == 'POST' and request.POST.get('id'):
        feed = Feed.objects.filter(id=request.POST.get('id'))
        if feed:
            feed.delete()
            return HttpResponse('0')
    return HttpResponse('1')

def archive(request, item_id):
    item = Item.objects.get(id=item_id)
    if not item:
        return HttpResponse('No item found')
    item.archived = True
    item.save()
    return HttpResponse('OK')

def feeds(request):
    feeds = Feed.objects.all()
    return render_to_response('feeds.html', {'feeds': feeds})

def bulk_archive(request):
    if not request.POST.get('ids'):
        return HttpResponse('Missing parameters')
    for item_id in request.POST.get('ids').split():
        try:
            item = Item.objects.filter(id=item_id).all()[0]
        except:
            continue
        item.archived = True
        item.save()
    return HttpResponse('OK')

def opml_import(request, url):
    import opml
    try:
        o = opml.parse(url)
    except:
        return HttpResponse('Cannot parse opml file %s' % url)
    for f in o:
        new = Feed.objects.create(url = f.xmlUrl,
                                  #tags = self.cleaned_data['tags'],
                                  name = f.title,
                                  )
        new.save()
    return HttpResponse('OK')

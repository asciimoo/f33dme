f33dme
======

LICENSE:
---------

f33dme is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

f33dme is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with f33dme. If not, see <http://www.gnu.org/licenses/>.

(C) 2011- by Adam Tauber, <asciimoo@gmail.com>

DEPENDENCIES:
-------------

- python django - www.djangoproject.com/
- python opml - http://pypi.python.org/pypi/opml/0.5
- python feedparser - http://www.feedparser.org/
- jquery - http://jquery.com/
- jquery infinite scroll - http://www.infinite-scroll.com/infinite-scroll-jquery-plugin/ ; https://github.com/paulirish/infinite-scroll
- python-utidylib
- lxml, beautifulsoup

INSTALL:
--------

1. Install dependencies
2. Create a directory and check out this repository to it
3. Go to the checked out directory
4. Move downloaded jquery.js to `media/js/jquery.min.js` - if infinite scroll enabled copy it to `media/js/jquery.infinitescroll.min.js`
5. Edit `settings.py` or `local_settings.py` - DATABASE_* settings are required
6. Run `./manage.py syncdb`
7. Run the software: `python ./manage.py runserver url:port`
8. Visit http://url:port/

FEATURES:
---------

- Archive/bulk archive
- Infinite scroll with auto archive
- Search
- OPML import
- Feed management

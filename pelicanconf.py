#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os

AUTHOR = u'NegativeDearc'
SITENAME = u'\u9648\u6653\u4f1f\u7684\u4e2a\u4eba\u535a\u5ba2'
SITEURL = ''
SITESUBTITLE = "Hello, I'm a Continues Improvement Engineer"

PATH = 'content'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = ((u'香阁公主', 'http://www.cxwloves.cc/'),
		 (u"酷酷马鹿", "http://www.kukumalu.cc"),
	)

# Social widget
SOCIAL = (('E-Mail', 'mailto:datingwithme@live.cn'),)

DEFAULT_PAGINATION = 5

# Archive 
ARCHIVES_SAVE_AS = 'archives.html'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# Theme path, will affect any css/js files related with the theme
THEME = os.path.join(os.path.dirname(__file__), "themes", "aboutwilson")

# Static path
STATIC_PATHS = ["images"]

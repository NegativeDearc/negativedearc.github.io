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
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# Theme path, will affect any css/js files related with the theme
THEME = os.path.join(os.path.dirname(__file__), "themes", "aboutwilson")

# Static path
STATIC_PATHS = ["images"]

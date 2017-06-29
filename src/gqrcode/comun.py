#! /usr/bin/python
# -*- coding: iso-8859-1 -*-
#
# com.py
#
# Copyright (C) 2011 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#
import os
import sys
import locale
import gettext


def is_package():
    return __file__.find('src') < 0

######################################


APP = 'gqrcode'
APPNAME = 'GQRCode'

# check if running from source
if is_package():
    ROOTDIR = '/usr/share'
    LANGDIR = os.path.join(ROOTDIR, 'locale-langpack')
    APPDIR = os.path.join(ROOTDIR, APP)
    CHANGELOG = os.path.join(APPDIR, 'gqrcode', 'changelog')
    ICONDIR = os.path.join(ROOTDIR, 'icons', 'hicolor', 'scalable', 'apps')
    ICON = os.path.join(ICONDIR, 'gqrcode.svg')
else:
    ROOTDIR = os.path.dirname(__file__)
    LANGDIR = os.path.normpath(os.path.join(ROOTDIR, '../../template1'))
    APPDIR = ROOTDIR
    DEBIANDIR = os.path.normpath(os.path.join(ROOTDIR, '../../debian'))
    CHANGELOG = os.path.join(DEBIANDIR, 'changelog')
    ICON = os.path.normpath(os.path.join(ROOTDIR,
                                         '../../data/icons/gqrcode.svg'))

HTML_WAI = os.path.join(APPDIR, 'whereami.html')

f = open(CHANGELOG, 'r')
line = f.readline()
f.close()
pos = line.find('(')
posf = line.find(')', pos)
VERSION = line[pos + 1:posf].strip()
if not is_package():
    VERSION = VERSION + '-src'

####
try:
    current_locale, encoding = locale.getdefaultlocale()
    language = gettext.translation(APP, LANGDIR, [current_locale])
    language.install()
    print(language)
    if sys.version_info[0] == 3:
        _ = language.gettext
    else:
        _ = language.ugettext
except Exception as e:
    print(e)
    _ = str
APPNAME = _(APPNAME)

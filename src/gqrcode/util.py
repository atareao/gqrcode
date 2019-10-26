#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of GQRCode
#
# Copyright (c) 2012-2019 Lorenzo Carbonell Cerezo <a.k.a. atareao>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import gi
try:
    gi.require_version('GdkPixbuf', '2.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import GdkPixbuf
import requests
import json


def get_latitude_longitude():
    try:
        response = requests.get('http://ip-api.com/json')
        if response.status_code == 200:
            ans = json.loads(response.text)
            return ans['lat'], ans['lon']
    except Exception as e:
        print(e)
    return 0, 0


def update_preview_cb(file_chooser, preview):
    filename = file_chooser.get_preview_filename()
    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 128, 128)
        preview.set_from_pixbuf(pixbuf)
        have_preview = True
    except Exception as e:
        print(e)
        have_preview = False
    file_chooser.set_preview_widget_active(have_preview)
    return

if __name__ == '__main__':
    ll = get_latitude_longitude()
    if ll is not None:
        print(ll)
    exit(0)
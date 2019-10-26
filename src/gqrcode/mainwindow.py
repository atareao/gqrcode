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
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    gi.require_version('Gio', '2.0')
    gi.require_version('GdkPixbuf', '2.0')
    gi.require_version('OsmGpsMap', '1.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GdkPixbuf
from gi.repository import OsmGpsMap
from enum import Enum
import os
import shlex
import subprocess
import tempfile
from . import comun
from .myqr import create_qr
from .util import get_latitude_longitude, update_preview_cb
# from .mylibs.draw import pixbuf2image
# import qreader
from .dasync import async_function
from .progreso import Progreso
from .parse import parse
from .comun import _

ST_GEO = 'GEO:{0},{1}'
ST_TEL = 'TEL:{0}'
ST_MAIL = 'MAILTO:{0}'
ST_WIFI = 'WIFI:T:{0};S:{1};P:{2};;'
ST_SMS = 'SMSTO:{0}:{1}'
ST_EMAIL_MSG = 'MATMSG:TO:{0};SUB:{1};BODY:{2};;'
ST_VCARD = '''BEGIN:VCARD
N;CHARSET=utf-8:{0};{1};;;
FN;CHARSET=utf-8:{2} {3}
ORG;CHARSET=utf-8:{4}
TITLE;CHARSET=utf-8:{5}
TEL;WORK:{6}
TEL;CELL:{7}
TEL;WORK;FAX:{8}
EMAIL;INTERNET;WORK;CHARSET=utf-8:{9}
ADR;WORK;CHARSET=utf-8:;;{10};{11};{12};{13};{14}
URL;WORK;CHARSET=utf-8:{15}
NOTE;CHARSET=utf-8:{16}
VERSION:2.1
END:VCARD
'''
ST_VEVENT = '''
BEGIN:VEVENT
SUMMARY:{0}
LOCATION:{1}
DESCRIPTION:{2}
DTSTART:{3}
DTEND:{4}
END:VEVENT
'''


def set_margins(widget, margin):
    widget.set_margin_left(margin)
    widget.set_margin_right(margin)
    widget.set_margin_top(margin)
    widget.set_margin_bottom(margin)
    if isinstance(widget, Gtk.Grid):
        widget.set_column_spacing(10)
        widget.set_row_spacing(10)


def select_value_in_combo(combo, value):
    model = combo.get_model()
    for i, item in enumerate(model):
        if value == item[1]:
            combo.set_active(i)
            return
    combo.set_active(0)


def get_selected_value_in_combo(combo):
    model = combo.get_model()
    return model.get_value(combo.get_active_iter(), 1)


def get_temporary_name():
    return tempfile.NamedTemporaryFile(mode='w+b',
                                       prefix='gqrcode',
                                       delete=True).name


def ejecuta(comando):
    args = shlex.split(comando)
    p = subprocess.Popen(args, bufsize=10000, stdout=subprocess.PIPE)
    valor = p.communicate()[0]
    return valor


class QRType(Enum):
    TEXT = 0
    GEOLOCATION = 1
    TELEPHONE_NUMBER = 2
    EMAIL = 3
    URL = 4
    WIFI_LOGIN = 5
    SMS = 6
    EMAIL_MESSAGE = 7
    VCARD = 8
    VEVENT = 9

    def get_type(decoded_string):
        if decoded_string.lower().startswith('geo:'):
            return QRType.GEOLOCATION
        if decoded_string.lower().startswith('tel:'):
            return QRType.TELEPHONE_NUMBER
        if decoded_string.lower().startswith('mailto:'):
            return QRType.EMAIL
        if decoded_string.lower().startswith('http://') or\
                decoded_string.lower().startswith('https://'):
            return QRType.URL
        if decoded_string.lower().startswith('wifi:'):
            return QRType.WIFI_LOGIN
        if decoded_string.lower().startswith('smsto:'):
            return QRType.SMS
        if decoded_string.lower().startswith('matmsg:'):
            return QRType.EMAIL_MESSAGE
        if decoded_string.lower().startswith('begin:vcard'):
            return QRType.VCARD
        if decoded_string.lower().startswith('begin:vevent'):
            return QRType.VEVENT
        return QRType.TEXT


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app, afile=None):
        Gtk.ApplicationWindow.__init__(self, application=app)

        self.qrcode_file = None
        self.frames = None
        self.background = None
        self.scale = 100
        self.pbuf = None

        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_title(comun.APP)
        self.set_icon_from_file(comun.ICON)
        self.set_resizable(False)
        self.set_default_size(600, 600)

        self.connect('destroy', self.close_application)
        hbox = Gtk.HBox(spacing=5)
        hbox.set_border_width(5)
        frame = Gtk.Frame()
        set_margins(frame, 5)
        self.add(frame)

        self.main_stack = Gtk.Stack.new()
        self.main_stack.set_transition_type(
            Gtk.StackTransitionType.UNDER_RIGHT)
        frame.add(self.main_stack)

        self.stack = Gtk.Stack.new()
        self.stack.set_transition_type(
            Gtk.StackTransitionType.UNDER_DOWN)
        self.main_stack.add_named(self.stack, 'Data')

        grid1 = Gtk.Grid()
        set_margins(grid1, 10)
        grid1.set_margin_right(10)
        self.stack.add_named(grid1, QRType.TEXT.name)
        label1 = Gtk.Label(_('Set text to encode: '))
        label1.set_alignment(0, .5)
        grid1.attach(label1, 0, 0, 1, 1)
        self.entry12 = Gtk.Entry()
        self.entry12.set_alignment(0)
        self.entry12.set_width_chars(40)
        grid1.attach(self.entry12, 1, 0, 1, 1)

        grid2 = Gtk.Grid()
        set_margins(grid2, 10)
        self.stack.add_named(grid2, QRType.GEOLOCATION.name)
        scrolledwindow0 = Gtk.ScrolledWindow()
        scrolledwindow0.set_policy(Gtk.PolicyType.AUTOMATIC,
                                   Gtk.PolicyType.AUTOMATIC)
        scrolledwindow0.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        scrolledwindow0.set_size_request(550, 550)
        grid2.attach(scrolledwindow0, 0, 0, 1, 1,)

        self.viewer = OsmGpsMap.Map()
        self.viewer.layer_add(OsmGpsMap.MapOsd(show_dpad=True,
                                               show_zoom=True,
                                               show_crosshair=True))

        # connect keyboard shortcuts
        self.viewer.set_keyboard_shortcut(OsmGpsMap.MapKey_t.FULLSCREEN,
                                          Gdk.keyval_from_name("F11"))
        self.viewer.set_keyboard_shortcut(OsmGpsMap.MapKey_t.UP,
                                          Gdk.keyval_from_name("Up"))
        self.viewer.set_keyboard_shortcut(OsmGpsMap.MapKey_t.DOWN,
                                          Gdk.keyval_from_name("Down"))
        self.viewer.set_keyboard_shortcut(OsmGpsMap.MapKey_t.LEFT,
                                          Gdk.keyval_from_name("Left"))
        self.viewer.set_keyboard_shortcut(OsmGpsMap.MapKey_t.RIGHT,
                                          Gdk.keyval_from_name("Right"))
        scrolledwindow0.add(self.viewer)
        scrolledwindow0.set_size_request(550, 550)

        grid3 = Gtk.Grid()
        set_margins(grid3, 10)
        self.stack.add_named(grid3, QRType.TELEPHONE_NUMBER.name)
        label1 = Gtk.Label(_('Set number to encode:'))
        label1.set_alignment(0, .5)
        grid3.attach(label1, 0, 0, 1, 1)
        #
        self.entry13 = Gtk.Entry()
        self.entry13.set_alignment(0)
        self.entry13.set_width_chars(40)
        grid3.attach(self.entry13, 1, 0, 1, 1)

        grid4 = Gtk.Grid()
        set_margins(grid4, 10)
        self.stack.add_named(grid4, QRType.EMAIL.name)
        label1 = Gtk.Label(_('Set email:'))
        label1.set_alignment(0, .5)
        grid4.attach(label1, 0, 0, 1, 1)

        self.entry14 = Gtk.Entry()
        self.entry14.set_alignment(0)
        self.entry14.set_width_chars(40)
        grid4.attach(self.entry14, 1, 0, 1, 1)

        grid5 = Gtk.Grid()
        set_margins(grid5, 10)
        self.stack.add_named(grid5, QRType.URL.name)
        label1 = Gtk.Label(_('Set url:'))
        label1.set_alignment(0, .5)
        grid5.attach(label1, 0, 0, 1, 1)

        self.entry15 = Gtk.Entry()
        self.entry15.set_alignment(0)
        self.entry15.set_width_chars(40)
        grid5.attach(self.entry15, 1, 0, 1, 1)

        grid6 = Gtk.Grid()
        set_margins(grid6, 10)
        self.stack.add_named(grid6, QRType.WIFI_LOGIN.name)
        label1 = Gtk.Label(_('SSID/Network name:'))
        label1.set_alignment(0, .5)
        grid6.attach(label1, 0, 0, 1, 1)

        self.entry161 = Gtk.Entry()
        self.entry161.set_alignment(0)
        self.entry161.set_width_chars(40)
        grid6.attach(self.entry161, 1, 0, 1, 1)

        label1 = Gtk.Label(_('Password:'))
        label1.set_alignment(0, .5)
        grid6.attach(label1, 0, 1, 1, 1)

        self.entry162 = Gtk.Entry()
        self.entry162.set_visibility(False)
        self.entry162.set_alignment(0)
        self.entry162.set_width_chars(40)
        grid6.attach(self.entry162, 1, 1, 1, 1,)

        label1 = Gtk.Label(_('Network type:'))
        label1.set_alignment(0, .5)
        grid6.attach(label1, 0, 2, 1, 1)
        self.liststore163 = Gtk.ListStore(str, str)
        self.liststore163.append([_('WEP'), 'WEP'])
        self.liststore163.append([_('WPA/WPA2'), 'WPA'])
        self.liststore163.append([_('No encryption'), 'nopass'])
        self.combobox163 = Gtk.ComboBox.new()
        self.combobox163.set_model(self.liststore163)
        cell163 = Gtk.CellRendererText()
        self.combobox163.pack_start(cell163, True)
        self.combobox163.add_attribute(cell163, 'text', 0)
        select_value_in_combo(self.combobox163, 'wpa')
        grid6.attach(self.combobox163, 1, 2, 1, 1)

        grid7 = Gtk.Grid()
        set_margins(grid7, 10)
        self.stack.add_named(grid7, QRType.SMS.name)

        label1 = Gtk.Label(_('Telephone Number:'))
        label1.set_alignment(0, .5)
        grid7.attach(label1, 0, 0, 1, 1)
        #
        self.entry171 = Gtk.Entry()
        self.entry171.set_alignment(0)
        self.entry171.set_width_chars(40)
        grid7.attach(self.entry171, 1, 0, 1, 1)
        #
        label1 = Gtk.Label(_('SMS Message:'))
        label1.set_alignment(0, .5)
        grid7.attach(label1, 0, 1, 1, 1)
        #
        scrolledwindow_sms = Gtk.ScrolledWindow()
        scrolledwindow_sms.set_hexpand(True)
        scrolledwindow_sms.set_vexpand(True)
        scrolledwindow_sms.set_shadow_type(type=Gtk.ShadowType.ETCHED_IN)
        scrolledwindow_sms.set_size_request(550, 550)
        grid7.attach(
            scrolledwindow_sms, 0, 2, 2, 2,)
        self.entry172 = Gtk.TextView()
        scrolledwindow_sms.add(self.entry172)

        grid8 = Gtk.Grid()
        set_margins(grid8, 10)
        self.stack.add_named(grid8, QRType.EMAIL_MESSAGE.name)

        label1 = Gtk.Label(_('Email:'))
        label1.set_alignment(0, .5)
        grid8.attach(label1, 0, 0, 1, 1)
        #
        self.entry181 = Gtk.Entry()
        self.entry181.set_alignment(0)
        self.entry181.set_width_chars(40)
        grid8.attach(self.entry181, 1, 0, 1, 1)
        #
        label1 = Gtk.Label(_('Subject:'))
        label1.set_alignment(0, .5)
        grid8.attach(label1, 0, 1, 1, 1)
        #
        self.entry182 = Gtk.Entry()
        self.entry182.set_alignment(0)
        self.entry182.set_width_chars(40)
        grid8.attach(self.entry182, 1, 1, 1, 1)
        #
        label1 = Gtk.Label(_('Body:'))
        label1.set_alignment(0, .5)
        grid8.attach(
            label1, 0, 2, 1, 1)
        #
        scrolledwindow_email = Gtk.ScrolledWindow()
        scrolledwindow_email.set_hexpand(True)
        scrolledwindow_email.set_vexpand(True)
        scrolledwindow_email.set_shadow_type(type=Gtk.ShadowType.ETCHED_IN)
        scrolledwindow_email.set_size_request(550, 300)
        grid8.attach(scrolledwindow_email, 0, 3, 2, 2)
        self.entry183 = Gtk.TextView()
        scrolledwindow_email.add(self.entry183)

        grid9 = Gtk.Grid()
        set_margins(grid9, 10)
        self.stack.add_named(grid9, QRType.VCARD.name)

        labels_card = {'01': _('Fist name'),
                       '02': _('Last name'),
                       '03': _('Job title'),
                       '04': _('Telephone Number (work)'),
                       '05': _('Fax Number (work)'),
                       '06': _('Cell Phone'),
                       '07': _('Email Address (work)'),
                       '08': _('Website Address'),
                       '09': _('Organization'),
                       '10': _('Street Address (work)'),
                       '11': _('City'),
                       '12': _('State'),
                       '13': _('Zip/Postcode'),
                       '14': _('Country'),
                       '15': _('Notes')}
        self.entries_vcard = {}
        for i, key in enumerate(sorted(labels_card.keys())):
            label1 = Gtk.Label(labels_card[key] + ':')
            label1.set_alignment(0, .5)
            grid9.attach(label1, 0, i, 1, 1)
            #
            self.entries_vcard[key] = Gtk.Entry()
            self.entries_vcard[key].set_alignment(0)
            self.entries_vcard[key].set_width_chars(40)
            grid9.attach(self.entries_vcard[key], 1, i, 1, 1)

        self.scrolled_code = Gtk.ScrolledWindow.new()
        self.scrolled_code.set_size_request(550, 550)
        self.main_stack.add_named(self.scrolled_code, 'Code')
        self.image = Gtk.Image()
        self.connect('key-release-event', self.on_key_release_event)
        self.scrolled_code.add_with_viewport(self.image)

        self.init_menu(hbox)
        self.init_headerbar()

        self.show_all()
        self.do_center()

    def on_key_release_event(self, widget, event):
        if event.keyval == 65451 or event.keyval == 43:
            self.scale = self.scale * 1.1
        elif event.keyval == 65453 or event.keyval == 45:
            self.scale = self.scale * 0.9
        elif event.keyval == 65456 or event.keyval == 48:
            self.scale = 100
        self.draw_code()

    def draw_code(self, first=False):
        if first is True:
            rectangle = self.scrolled_code.get_allocation()
            if rectangle.width == 1 or rectangle.height == 1:
                width = 400
                height = 400
            else:
                width = rectangle.width
                height = rectangle.height
            scale_w = width / self.pbuf.get_width() * 100
            scale_h = height / self.pbuf.get_height() * 100
            if scale_w > scale_h:
                self.scale = scale_h
            else:
                self.scale = scale_w

        if self.pbuf is not None:
            w = int(self.pbuf.get_width() * self.scale / 100)
            h = int(self.pbuf.get_height() * self.scale / 100)
            pixbuf = self.pbuf.scale_simple(w, h,
                                            GdkPixbuf.InterpType.BILINEAR)
            self.image.set_from_pixbuf(pixbuf)

    def init_headerbar(self):
        self.control = {}

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = comun.APPNAME
        self.set_titlebar(hb)

        file_model = Gio.Menu()

        file_section1_model = Gio.Menu()
        file_section1_model.append(_('Open QR Image'), 'app.open')
        file_section1 = Gio.MenuItem.new_section(None, file_section1_model)
        file_model.append_item(file_section1)

        file_section2_model = Gio.Menu()
        file_section2_model.append(_('Load background'), 'app.load')
        file_section2_model.append(_('Reset background'), 'app.reset')
        file_section2 = Gio.MenuItem.new_section(None, file_section2_model)
        file_model.append_item(file_section2)

        file_section3_model = Gio.Menu()
        file_section3_model.append(_('Save QR Image'), 'app.save')
        file_section3 = Gio.MenuItem.new_section(None, file_section3_model)
        file_model.append_item(file_section3)

        file_section4_model = Gio.Menu()
        file_section4_model.append(_('Close'), 'app.close')
        file_section4 = Gio.MenuItem.new_section(None, file_section4_model)
        file_model.append_item(file_section4)

        self.control['file'] = Gtk.MenuButton()
        self.control['file'].set_menu_model(file_model)
        self.control['file'].add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(
            name='folder-open-symbolic'), Gtk.IconSize.BUTTON))
        hb.pack_start(self.control['file'])

        model = Gtk.ListStore(str, object)
        model.append([_('Text'), QRType.TEXT])
        model.append([_('Geolocation'), QRType.GEOLOCATION])
        model.append([_('Telephone number'), QRType.TELEPHONE_NUMBER])
        model.append([_('Email'), QRType.EMAIL])
        model.append([_('Url'), QRType.URL])
        model.append([_('Wifi Login'), QRType.WIFI_LOGIN])
        model.append([_('SMS'), QRType.SMS])
        model.append([_('Email message'), QRType.EMAIL_MESSAGE])
        model.append([_('vCard'), QRType.VCARD])

        self.control['encoder'] = Gtk.ComboBox.new()
        self.control['encoder'].set_model(model)
        cell = Gtk.CellRendererText()
        self.control['encoder'].pack_start(cell, True)
        self.control['encoder'].add_attribute(cell, 'text', 0)
        select_value_in_combo(self.control['encoder'], 'Text')
        self.control['encoder'].connect('changed', self.on_encoder_changed)
        hb.pack_start(self.control['encoder'])

        self.control['run'] = Gtk.Button()
        self.control['run'].set_tooltip_text(_('Encode'))
        self.control['run'].add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(
            name='go-next-symbolic'), Gtk.IconSize.BUTTON))
        self.control['run'].connect('clicked', self.on_run)
        hb.pack_start(self.control['run'])

        help_model = Gio.Menu()

        help_section1_model = Gio.Menu()
        help_section1_model.append(_('Homepage'), 'app.goto_homepage')
        help_section1 = Gio.MenuItem.new_section(None, help_section1_model)
        help_model.append_item(help_section1)

        help_section2_model = Gio.Menu()
        help_section2_model.append(_('Code'), 'app.goto_code')
        help_section2_model.append(_('Issues'), 'app.goto_bug')
        help_section2 = Gio.MenuItem.new_section(None, help_section2_model)
        help_model.append_item(help_section2)

        help_section3_model = Gio.Menu()
        help_section3_model.append(_('Twitter'), 'app.goto_twitter')
        help_section3_model.append(_('Facebook'), 'app.goto_facebook')
        help_section3_model.append(_('Google+'), 'app.goto_google_plus')
        help_section3 = Gio.MenuItem.new_section(None, help_section3_model)
        help_model.append_item(help_section3)

        help_section4_model = Gio.Menu()
        help_section4_model.append(_('Donations'), 'app.goto_donate')
        help_section4 = Gio.MenuItem.new_section(None, help_section4_model)
        help_model.append_item(help_section4)

        help_section5_model = Gio.Menu()
        help_section5_model.append(_('About'), 'app.about')
        help_section5 = Gio.MenuItem.new_section(None, help_section5_model)
        help_model.append_item(help_section5)

        self.control['help'] = Gtk.MenuButton()
        self.control['help'].set_menu_model(help_model)
        self.control['help'].add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(
            name='open-menu-symbolic'), Gtk.IconSize.BUTTON))
        hb.pack_end(self.control['help'])

    def on_run(self, widget):
        if self.main_stack.get_visible_child_name() == 'Data':
            selected = get_selected_value_in_combo(self.control['encoder'])
            if selected == QRType.GEOLOCATION:
                to_encode = ST_GEO.format(
                    '{:10.4f}'.format(self.viewer.props.latitude),
                    '{:10.4f}'.format(self.viewer.props.longitude))
            elif selected == QRType.TEXT:
                to_encode = self.entry12.get_text()
            elif selected == QRType.TELEPHONE_NUMBER:
                to_encode = ST_TEL.format(self.entry13.get_text())
            elif selected == QRType.EMAIL:
                to_encode = ST_MAIL.format(self.entry14.get_text())
            elif selected == QRType.URL:
                to_encode = self.entry15.get_text()
                if not to_encode.startswith('http://') and\
                        not to_encode.startswith('https://'):
                    if to_encode.startswith('//'):
                        to_encode = 'http:' + to_encode
                    elif to_encode.startswith('/'):
                        to_encode = 'http:/' + to_encode
                    else:
                        to_encode = 'http://' + to_encode
            elif selected == QRType.WIFI_LOGIN:
                ssid = self.entry161.get_text()
                password = self.entry162.get_text()
                network_type = get_selected_value_in_combo(self.combobox163)
                to_encode = ST_WIFI.format(
                    network_type, ssid, password)
            elif selected == QRType.SMS:
                number = self.entry171.get_text()
                textbuffer = self.entry172.get_buffer()
                start_iter, end_iter = textbuffer.get_bounds()
                message = textbuffer.get_text(start_iter, end_iter, True)
                to_encode = ST_SMS.format(number, message)
            elif selected == QRType.EMAIL_MESSAGE:
                email = self.entry181.get_text()
                subject = self.entry182.get_text()
                textbuffer = self.entry183.get_buffer()
                start_iter, end_iter = textbuffer.get_bounds()
                message = textbuffer.get_text(start_iter, end_iter, True)
                to_encode = ST_EMAIL_MSG.format(email, subject, message)
            elif selected == QRType.VCARD:
                first_name = self.entries_vcard['01'].get_text()
                last_name = self.entries_vcard['02'].get_text()
                job_title = self.entries_vcard['03'].get_text()
                telephone_number = self.entries_vcard['04'].get_text()
                cell_phone = self.entries_vcard['05'].get_text()
                fax = self.entries_vcard['06'].get_text()
                email = self.entries_vcard['07'].get_text()
                web = self.entries_vcard['08'].get_text()
                organization = self.entries_vcard['09'].get_text()
                street = self.entries_vcard['10'].get_text()
                city = self.entries_vcard['11'].get_text()
                state = self.entries_vcard['12'].get_text()
                postcode = self.entries_vcard['13'].get_text()
                country = self.entries_vcard['14'].get_text()
                notes = self.entries_vcard['15'].get_text()
                if not web.startswith('http') and\
                        not web.startswith('https'):
                    web = 'http:\\' + web
                to_encode = ST_VCARD.format(last_name, first_name, first_name,
                                            last_name, organization, job_title,
                                            telephone_number, cell_phone, fax,
                                            email, street, city, state,
                                            postcode, country, web, notes)
            elif selected == 'vCal':
                to_encode = '''
BEGIN:VEVENT
SUMMARY:{0}
LOCATION:{1}
DESCRIPTION:{2}
DTSTART:{3}
DTEND:{4}
END:VEVENT
'''
            else:
                return
            self.do_encode(to_encode)
        elif self.main_stack.get_visible_child_name() == 'Code':
            print(23)
            self.do_decode(self.image.get_pixbuf())

    def do_encode(self, to_encode):
        # self.entry21.set_text(to_encode)

        def on_encode_done(result, error):
            if self.main_stack.get_visible_child_name() == 'Data':
                if isinstance(result, GdkPixbuf.Pixbuf):
                    self.pbuf = result
                    self.draw_code(first=True)
                elif isinstance(result, GdkPixbuf.PixbufSimpleAnim):
                    self.pbuf = result
                    self.draw_code(first=True)
                else:
                    print(type(result))

                self.main_stack.set_visible_child_name('Code')
                self.main_stack.set_transition_type(
                    Gtk.StackTransitionType.UNDER_LEFT)
                self.control['run'].get_child().set_from_gicon(
                    Gio.ThemedIcon(name='go-previous-symbolic'),
                    Gtk.IconSize.BUTTON)

            elif self.main_stack.get_visible_child_name() == 'Code':
                self.main_stack.set_visible_child_name('Data')
                self.main_stack.set_transition_type(
                    Gtk.StackTransitionType.UNDER_RIGHT)
                self.control['run'].get_child().set_from_gicon(
                    Gio.ThemedIcon(name='go-next-symbolic'),
                    Gtk.IconSize.BUTTON)

            self.main_stack.get_visible_child().show_all()
            self.get_window().set_cursor(None)

        @async_function(on_done=on_encode_done)
        def do_encode_in_thread(to_encode, picture, progreso):
            qr, frames = create_qr(to_encode, picture=picture,
                                   progreso=progreso)
            self.frames = frames
            return qr
        self.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))
        p = Progreso(_('Creating QR Code'), self)
        do_encode_in_thread(to_encode, self.background, progreso=p)
        p.run()

    def on_encoder_changed(self, widget):
        selected = get_selected_value_in_combo(self.control['encoder'])
        self.stack.set_visible_child_name(selected.name)
        self.stack.get_visible_child().show_all()

    def do_center(self):
        def on_center_done(result, error):
            # Do stuff with the result and handle errors in the main thread.
            if result is not None:
                latitude, longitude = result
                self.viewer.set_center_and_zoom(latitude, longitude, 14)

        @async_function(on_done=on_center_done)
        def do_center_in_thread():
            return get_latitude_longitude()

        do_center_in_thread()

    def init_menu(self, vbox):
        menubar = Gtk.MenuBar()
        vbox.pack_start(menubar, False, False, 0)
        accel_group = Gtk.AccelGroup()
        self.add_accel_group(accel_group)

        ################################################################
        self.filemenu = Gtk.Menu.new()
        self.filem = Gtk.MenuItem.new_with_label(_('File'))
        self.filem.set_submenu(self.filemenu)
        #
        self.menus = {}
        #
        self.menus['load'] = Gtk.ImageMenuItem.new_with_label(_('load file'))
        self.menus['load'].connect('activate',
                                   self.on_menu_clicked, 'load')
        self.menus['load'].add_accelerator(
            'activate', accel_group, ord('L'), Gdk.ModifierType.CONTROL_MASK,
            Gtk.AccelFlags.VISIBLE)
        self.filemenu.append(self.menus['load'])
        self.filemenu.append(Gtk.SeparatorMenuItem())
        self.menus['save-as'] = Gtk.ImageMenuItem.new_with_label(_('Save as'))
        self.menus['save-as'].connect('activate',
                                      self.on_menu_clicked, 'save-as')
        self.menus['save-as'].add_accelerator(
            'activate', accel_group, ord('S'), Gdk.ModifierType.CONTROL_MASK,
            Gtk.AccelFlags.VISIBLE)
        self.filemenu.append(self.menus['save-as'])

    def on_menu_clicked(self, widget, option):
        if option == 'save-as':
            self.save_encoded()
        elif option == 'load':
            self.load_qrcode()

    def load_qrcode(self):
        fcd = Gtk.FileChooserDialog(
            _('Set file to load qrcode'),
            self, Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                     Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))

        afilter = Gtk.FileFilter()
        afilter.set_name(_('png files'))
        afilter.add_mime_type('image/png')
        afilter.add_pattern('*.png')
        fcd.add_filter(afilter)
        fcd.set_current_folder(os.getenv('HOME'))
        preview = Gtk.Image()
        fcd.set_preview_widget(preview)
        fcd.connect('update-preview', update_preview_cb, preview)
        res = fcd.run()
        if res == Gtk.ResponseType.ACCEPT:
            filename = fcd.get_filename()
            if os.path.exists(filename):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename,
                                                                400, 400)
                self.image.set_from_pixbuf(pixbuf)
                self.qrcode_file = filename
                self.do_decode(filename)
        fcd.destroy()



    def load_background(self):
        self.background = None
        fcd = Gtk.FileChooserDialog(
            _('Set file for QR background'),
            self, Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                     Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        afilter = Gtk.FileFilter()
        afilter.set_name(_('Image files'))
        afilter.add_mime_type('image/png')
        afilter.add_mime_type('image/jpeg')
        afilter.add_mime_type('image/gif')
        fcd.add_filter(afilter)
        afilter = Gtk.FileFilter()
        afilter.set_name(_('png files'))
        afilter.add_mime_type('image/png')
        fcd.add_filter(afilter)
        afilter = Gtk.FileFilter()
        afilter.set_name(_('jpeg files'))
        afilter.add_mime_type('image/jpeg')
        fcd.add_filter(afilter)
        afilter = Gtk.FileFilter()
        afilter.set_name(_('gif files'))
        afilter.add_mime_type('image/gif')
        fcd.add_filter(afilter)
        fcd.set_current_folder(os.getenv('HOME'))
        preview = Gtk.Image()
        fcd.set_preview_widget(preview)
        fcd.connect('update-preview', update_preview_cb, preview)
        res = fcd.run()
        if res == Gtk.ResponseType.ACCEPT:
            filename = fcd.get_filename()
            if os.path.exists(filename):
                self.background = filename
        fcd.destroy()

    def clean(self):
        self.entry12.set_text('')
        self.entry13.set_text('')
        self.entry14.set_text('')
        self.entry15.set_text('')
        self.entry161.set_text('')
        self.entry162.set_text('')
        self.entry171.set_text('')
        self.entry172.get_buffer().set_text('')
        select_value_in_combo(self.combobox163, 'WEP')
        self.entry181.set_text('')
        self.entry182.set_text('')
        self.entry183.get_buffer().set_text('')

    def do_decode(self, to_decode):

        def on_decode_done(result, error):
            self.clean()
            if result is not None:
                if QRType.get_type(result) == QRType.TEXT:
                    self.entry12.set_text(result)
                elif QRType.get_type(result) == QRType.GEOLOCATION:
                    r = parse(ST_GEO, result)
                    if r is not None:
                        self.viewer.set_center_and_zoom(float(r[0]),
                                                        float(r[1]),
                                                        14)
                elif QRType.get_type(result) == QRType.TELEPHONE_NUMBER:
                    r = parse(ST_TEL, result)
                    if r is not None:
                        self.entry13.set_text(r[0])
                elif QRType.get_type(result) == QRType.EMAIL:
                    r = parse(ST_MAIL, result)
                    if r is not None:
                        self.entry14.set_text(r[0])
                elif QRType.get_type(result) == QRType.URL:
                    self.entry15.set_text(result)
                elif QRType.get_type(result) == QRType.WIFI_LOGIN:
                    r = parse(ST_WIFI, result)
                    if r is not None:
                        self.entry161.set_text(r[1])
                        self.entry162.set_text(r[2])
                    select_value_in_combo(self.combobox163, r[0])
                elif QRType.get_type(result) == QRType.SMS:
                    r = parse(ST_SMS, result)
                    if r is not None:
                        self.entry171.set_text(r[0])
                        self.entry172.get_buffer().set_text(r[1])
                elif QRType.get_type(result) == QRType.EMAIL_MESSAGE:
                    r = parse(ST_EMAIL_MSG, result)
                    if r is not None:
                        self.entry181.set_text(r[0])
                        self.entry182.set_text(r[1])
                        self.entry183.get_buffer().set_text(r[2])
                elif QRType.get_type(result) == QRType.VCARD:
                    r = parse(ST_VCARD, result)
                    if r is not None:
                        self.entries_vcard['01'].set_text(r[0])
                        self.entries_vcard['02'].set_text(r[1])
                        self.entries_vcard['03'].set_text(r[2])
                        self.entries_vcard['04'].set_text(r[3])
                        self.entries_vcard['05'].set_text(r[4])
                        self.entries_vcard['06'].set_text(r[5])
                        self.entries_vcard['07'].set_text(r[6])
                        self.entries_vcard['08'].set_text(r[7])
                        self.entries_vcard['09'].set_text(r[8])
                        self.entries_vcard['10'].set_text(r[9])
                        self.entries_vcard['11'].set_text(r[10])
                        self.entries_vcard['12'].set_text(r[11])
                        self.entries_vcard['13'].set_text(r[12])
                        self.entries_vcard['14'].set_text(r[13])
                        self.entries_vcard['15'].set_text(r[14])

                select_value_in_combo(self.control['encoder'],
                                      QRType.get_type(result))

                print(24)
                self.main_stack.set_visible_child_name('Data')
                self.main_stack.set_transition_type(
                    Gtk.StackTransitionType.UNDER_RIGHT)
                self.control['run'].get_child().set_from_gicon(
                    Gio.ThemedIcon(name='go-next-symbolic'),
                    Gtk.IconSize.BUTTON)
                self.main_stack.get_visible_child().show_all()
                print(25)

        @async_function(on_done=on_decode_done)
        def do_decode_in_thread(to_decode):
            if to_decode is not None:
                if isinstance(to_decode, str) and os.path.exists(to_decode):
                    command = 'zbarimg %s' % (to_decode)
                elif isinstance(to_decode, GdkPixbuf.Pixbuf):
                    mtempfile = tempfile.NamedTemporaryFile(mode='w+b',
                                                            prefix='gqrcode',
                                                            delete=True).name
                    to_decode.savev(mtempfile, 'png', [], [])
                    command = 'zbarimg %s' % (mtempfile)
                else:
                    return None
                salida = ejecuta(command)
                try:
                    utf8Data = salida.decode()
                    salida = utf8Data.split('QR-Code:')[1]
                except UnicodeDecodeError as e:
                    print('UnicodeDecodeError', e)
                    utf8Data = salida.decode("utf-8").encode("sjis")
                    salida = utf8Data.decode("utf-8").split('QR-Code:')[1]
                if salida.endswith('\n'):
                    salida = salida[:-1]
                return salida
        do_decode_in_thread(to_decode)

    def save_encoded(self):
        animation = self.image.get_animation()
        if animation is None:
            pixbuf = self.image.get_pixbuf()
            if pixbuf is not None:
                fcd = Gtk.FileChooserDialog(
                    _('Set file to save encode image'),
                    self, Gtk.FileChooserAction.SAVE,
                    buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                             Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
                fcd.set_current_folder(os.getenv('HOME'))
                fcd.set_default_response(Gtk.ResponseType.OK)
                afilter = Gtk.FileFilter()
                afilter.set_name(_('png files'))
                afilter.add_mime_type('image/png')
                afilter.add_pattern('*.png')
                fcd.add_filter(afilter)
                res = fcd.run()
                if res == Gtk.ResponseType.ACCEPT:
                    filename = fcd.get_filename()
                    if not filename.endswith('.png'):
                        filename += '.png'
                    pixbuf.savev(filename, 'png', [], [])
                fcd.destroy()
        elif self.frames is not None and len(self.frames) > 0:
            fcd = Gtk.FileChooserDialog(
                _('Set file to save encode image'),
                self, Gtk.FileChooserAction.SAVE,
                buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                         Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
            fcd.set_current_folder(os.getenv('HOME'))
            fcd.set_default_response(Gtk.ResponseType.OK)
            filter = Gtk.FileFilter()
            filter.set_name(_('gif files'))
            filter.add_mime_type('image/gif')
            fcd.add_filter(filter)
            res = fcd.run()
            if res == Gtk.ResponseType.ACCEPT:
                filename = fcd.get_filename()
                if not filename.endswith('.gif'):
                    filename += '.gif'
                self.frames[0].save(filename,
                                    save_all=True,
                                    append_images=self.frames[1:],
                                    loop=0)
            fcd.destroy()

    def close_application(self, widget):
        self.destroy()

    def on_toolbar_clicked(self, action, name):
        if name == 'open':
            self.load_qrcode()
        elif name == 'load':
            self.load_background()
        elif name == 'reset':
            self.background = None
        elif name == 'save':
            self.save_encoded()
        elif name == 'close':
            self.destroy()


def main():
    MainWindow()
    Gtk.main()


if __name__ == '__main__':
    main()
    exit(0)

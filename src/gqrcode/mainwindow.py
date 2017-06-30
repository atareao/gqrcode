#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# <one line to give the program's name and a brief idea of what it does.>
#
# Copyright (C) 2010-2016 Lorenzo Carbonell
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
import os
import shlex
import subprocess
import tempfile
from . import comun
from .myqr import create_qr
from .geolocation import get_external_ip, get_latitude_longitude
# from .mylibs.draw import pixbuf2image
# import qreader
from .async import async_function
from .progreso import Progreso
from .comun import _


def set_margins(widget, margin):
    widget.set_margin_left(margin)
    widget.set_margin_right(margin)
    widget.set_margin_top(margin)
    widget.set_margin_bottom(margin)
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


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app, afile=None):
        Gtk.ApplicationWindow.__init__(self, application=app)

        self.qrcode_file = None
        self.frames = None
        self.background = None

        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_title(comun.APP)
        self.set_icon_from_file(comun.ICON)
        self.set_resizable(False)
        self.set_default_size(600, 600)

        self.connect('destroy', self.close_application)
        hbox = Gtk.HBox(spacing=5)
        hbox.set_border_width(5)
        self.add(hbox)

        self.frame = Gtk.Frame()
        hbox.pack_start(self.frame, True, True, 0)

        self.stack = Gtk.Stack.new()
        self.stack.set_transition_type(Gtk.StackTransitionType.UNDER_DOWN)
        self.frame.add(self.stack)

        grid1 = Gtk.Grid()
        set_margins(grid1, 10)
        grid1.set_margin_right(10)
        self.stack.add_named(grid1, 'Text')
        label1 = Gtk.Label(_('Set text to encode: '))
        label1.set_alignment(0, .5)
        grid1.attach(label1, 0, 0, 1, 1)
        self.entry12 = Gtk.Entry()
        self.entry12.set_alignment(0)
        self.entry12.set_width_chars(40)
        grid1.attach(self.entry12, 1, 0, 1, 1)

        grid2 = Gtk.Grid()
        set_margins(grid2, 10)
        self.stack.add_named(grid2, 'Geolocation')
        scrolledwindow0 = Gtk.ScrolledWindow()
        scrolledwindow0.set_policy(Gtk.PolicyType.AUTOMATIC,
                                   Gtk.PolicyType.AUTOMATIC)
        scrolledwindow0.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        scrolledwindow0.set_size_request(500, 400)
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
        scrolledwindow0.set_size_request(500, 400)

        grid3 = Gtk.Grid()
        set_margins(grid3, 10)
        self.stack.add_named(grid3, 'Telephone number')
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
        self.stack.add_named(grid4, 'Email')
        label1 = Gtk.Label(_('Set email:'))
        label1.set_alignment(0, .5)
        grid4.attach(label1, 0, 0, 1, 1)

        self.entry14 = Gtk.Entry()
        self.entry14.set_alignment(0)
        self.entry14.set_width_chars(40)
        grid4.attach(self.entry14, 1, 0, 1, 1)

        grid5 = Gtk.Grid()
        set_margins(grid5, 10)
        self.stack.add_named(grid5, 'Url')
        label1 = Gtk.Label(_('Set url:'))
        label1.set_alignment(0, .5)
        grid5.attach(label1, 0, 0, 1, 1)

        self.entry15 = Gtk.Entry()
        self.entry15.set_alignment(0)
        self.entry15.set_width_chars(40)
        grid5.attach(self.entry15, 1, 0, 1, 1)

        grid6 = Gtk.Grid()
        set_margins(grid6, 10)
        self.stack.add_named(grid6, 'Wifi Login')
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
        self.stack.add_named(grid7, 'SMS')

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
        scrolledwindow_sms.set_size_request(400, 300)
        grid7.attach(
            scrolledwindow_sms, 0, 2, 2, 2,)
        self.entry172 = Gtk.TextView()
        scrolledwindow_sms.add(self.entry172)

        grid8 = Gtk.Grid()
        set_margins(grid8, 10)
        self.stack.add_named(grid8, 'Email message')

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
        scrolledwindow_email.set_size_request(400, 300)
        grid8.attach(scrolledwindow_email, 0, 3, 2, 2)
        self.entry183 = Gtk.TextView()
        scrolledwindow_email.add(self.entry183)

        grid9 = Gtk.Grid()
        set_margins(grid9, 10)
        self.stack.add_named(grid9, 'vCard')

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

        self.notebook2 = Gtk.Notebook()
        hbox.pack_start(self.notebook2, False, False, 0)
        #
        table21 = Gtk.Table(rows=2, columns=2, homogeneous=False)
        table21.set_border_width(5)
        table21.set_col_spacings(5)
        table21.set_row_spacings(5)
        self.notebook2.append_page(table21, tab_label=Gtk.Label(_('Encode')))
        #
        self.image21 = Gtk.Image()
        table21.attach(
            self.image21, 0, 2, 0, 1,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.FILL)
        self.image21.set_size_request(400, 400)
        #
        label21 = Gtk.Label(_('Encoded text:'))
        label21.set_alignment(0, .5)
        table21.attach(
            label21, 0, 1, 1, 2,
            xoptions=Gtk.AttachOptions.SHRINK,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        self.entry21 = Gtk.Entry()
        self.entry21.set_alignment(0)
        self.entry21.set_editable(False)
        self.entry21.set_width_chars(40)
        table21.attach(
            self.entry21, 1, 2, 1, 2,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        #
        table22 = Gtk.Table(rows=2, columns=2, homogeneous=False)
        table22.set_border_width(5)
        table22.set_col_spacings(5)
        table22.set_row_spacings(5)
        self.notebook2.append_page(table22, tab_label=Gtk.Label(_('Decode')))
        #
        self.image22 = Gtk.Image()
        table22.attach(
            self.image22, 0, 2, 0, 1,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.FILL)
        self.image22.set_size_request(400, 400)
        #
        label22 = Gtk.Label(_('Decoded') + ': ')
        label22.set_alignment(0, 0.5)
        table22.attach(
            label22, 0, 1, 1, 2,
            xoptions=Gtk.AttachOptions.SHRINK,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        self.entry22 = Gtk.Entry()
        self.entry22.set_alignment(0)
        self.entry22.set_width_chars(50)
        table22.attach(
            self.entry22, 1, 2, 1, 2,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        self.init_menu(hbox)
        self.init_headerbar()
        #
        self.show_all()
        #
        self.do_center()

    def init_headerbar(self):
        self.control = {}

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = comun.APPNAME
        self.set_titlebar(hb)

        file_model = Gio.Menu()

        file_section1_model = Gio.Menu()
        file_section1_model.append(_('Open'), 'app.open')
        file_section1 = Gio.MenuItem.new_section(None, file_section1_model)
        file_model.append_item(file_section1)

        file_section2_model = Gio.Menu()
        file_section2_model.append(_('Load background'), 'app.load')
        file_section2_model.append(_('Reset background'), 'app.reset')
        file_section2 = Gio.MenuItem.new_section(None, file_section2_model)
        file_model.append_item(file_section2)

        file_section3_model = Gio.Menu()
        file_section3_model.append(_('Save'), 'app.save')
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

        model = Gtk.ListStore(str, str)
        model.append([_('Text'), 'Text'])
        model.append([_('Geolocation'), 'Geolocation'])
        model.append([_('Telephone number'), 'Telephone number'])
        model.append([_('Email'), 'Email'])
        model.append([_('Url'), 'Url'])
        model.append([_('Wifi Login'), 'Wifi Login'])
        model.append([_('SMS'), 'SMS'])
        model.append([_('Email message'), 'Email message'])
        model.append([_('vCard'), 'vCard'])

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
            name='system-run-symbolic'), Gtk.IconSize.BUTTON))
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
        selected = get_selected_value_in_combo(self.control['encoder'])
        if selected == 'Geolocation':
            to_encode = 'geo:%1.4f,%1.4f' % (self.viewer.props.latitude,
                                             self.viewer.props.longitude)
        elif selected == 'Text':
            to_encode = self.entry12.get_text()
        elif selected == 'Telephone number':
            to_encode = 'TEL:'+self.entry13.get_text()
        elif selected == 'Email':
            to_encode = 'MAILTO:'+self.entry14.get_text()
        elif selected == 'Url':
            to_encode = self.entry15.get_text()
            if not to_encode.startswith('http://') and\
                    not to_encode.startswith('https://'):
                if to_encode.startswith('//'):
                    to_encode = 'http:' + to_encode
                elif to_encode.startswith('/'):
                    to_encode = 'http:/' + to_encode
                else:
                    to_encode = 'http://' + to_encode
        elif selected == 'Wifi Login':
            ssid = self.entry161.get_text()
            password = self.entry162.get_text()
            network_type = get_selected_value_in_combo(self.combobox163)
            print(ssid, password, network_type)
            to_encode = 'WIFI:T:%s;S:%s;P:%s;;' % (
                network_type, ssid, password)
        elif selected == 'SMS':
            number = self.entry171.get_text()
            textbuffer = self.entry172.get_buffer()
            start_iter, end_iter = textbuffer.get_bounds()
            message = textbuffer.get_text(start_iter, end_iter, True)
            to_encode = 'SMSTO:%s:%s' % (number, message)
        elif selected == 'Email message':
            email = self.entry181.get_text()
            subject = self.entry182.get_text()
            textbuffer = self.entry183.get_buffer()
            start_iter, end_iter = textbuffer.get_bounds()
            message = textbuffer.get_text(start_iter, end_iter, True)
            to_encode = 'MATMSG:TO:%s;SUB:%s;BODY:%s;;' % (
                email, subject, message)
        elif selected == 'vCard':
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
            to_encode = '''
BEGIN:VCARD
N;CHARSET=utf-8:%s;%s;;;
FN;CHARSET=utf-8:%s %s
ORG;CHARSET=utf-8:%s
TITLE;CHARSET=utf-8:%s
TEL;WORK:%s
TEL;CELL:%s
TEL;WORK;FAX:%s
EMAIL;INTERNET;WORK;CHARSET=utf-8:%s
ADR;WORK;CHARSET=utf-8:;;%s;%s;%s;%s;%s
URL;WORK;CHARSET=utf-8:%s
NOTE;CHARSET=utf-8:%s
VERSION:2.1
END:VCARD
''' % (last_name, first_name, first_name, last_name, organization, job_title,
                telephone_number, cell_phone, fax, email, street, city, state,
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

    def do_encode(self, to_encode):
        self.entry21.set_text(to_encode)

        def on_encode_done(result, error):
            print('---', 1, '---')
            if isinstance(result, GdkPixbuf.Pixbuf):
                print('---', 2, '---')
                self.image21.set_from_pixbuf(result)
            elif isinstance(result, GdkPixbuf.PixbufSimpleAnim):
                print('---', 3, '---')
                self.image21.set_from_animation(result)
            else:
                print(type(result))
            '''
            pixbuf = result['pixbuf']
            mtempfile = result['tempfile']
            self.image21.set_from_pixbuf(pixbuf)
            if os.path.exists(mtempfile):
                os.remove(mtempfile)
            '''
            self.notebook2.set_current_page(0)
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
        self.frame.set_label(selected)
        print(selected)
        self.stack.set_visible_child_name(selected)
        self.stack.get_visible_child().show_all()

    def do_center(self):
        def on_center_done(result, error):
            # Do stuff with the result and handle errors in the main thread.
            if result is not None:
                latitude, longitude = result
                self.viewer.set_center_and_zoom(latitude, longitude, 14)

        @async_function(on_done=on_center_done)
        def do_center_in_thread():
            ip = get_external_ip()
            if ip is not None:
                ans = get_latitude_longitude(ip)
                return ans
            return None
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

        filter = Gtk.FileFilter()
        filter.set_name(_('png files'))
        filter.add_mime_type('image/png')
        filter.add_pattern('*.png')
        fcd.add_filter(filter)
        fcd.set_current_folder(os.getenv('HOME'))
        preview = Gtk.Image()
        fcd.set_preview_widget(preview)
        fcd.connect('update-preview', self.update_preview_cb, preview)
        res = fcd.run()
        if res == Gtk.ResponseType.ACCEPT:
            filename = fcd.get_filename()
            if os.path.exists(filename):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename,
                                                                400, 400)
                self.image22.set_from_pixbuf(pixbuf)
                self.qrcode_file = filename
        fcd.destroy()
        self.do_decode()

    def update_preview_cb(self, file_chooser, preview):
        filename = file_chooser.get_preview_filename()
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 128, 128)
            preview.set_from_pixbuf(pixbuf)
            have_preview = True
        except:
            have_preview = False
        file_chooser.set_preview_widget_active(have_preview)
        return

    def load_background(self):
        self.background = None
        fcd = Gtk.FileChooserDialog(
            _('Set file for QR background'),
            self, Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                     Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        filter = Gtk.FileFilter()
        filter.set_name(_('Image files'))
        filter.add_mime_type('image/png')
        filter.add_mime_type('image/jpeg')
        filter.add_mime_type('image/gif')
        fcd.add_filter(filter)
        filter = Gtk.FileFilter()
        filter.set_name(_('png files'))
        filter.add_mime_type('image/png')
        fcd.add_filter(filter)
        filter = Gtk.FileFilter()
        filter.set_name(_('jpeg files'))
        filter.add_mime_type('image/jpeg')
        fcd.add_filter(filter)
        filter = Gtk.FileFilter()
        filter.set_name(_('gif files'))
        filter.add_mime_type('image/gif')
        fcd.add_filter(filter)
        fcd.set_current_folder(os.getenv('HOME'))
        preview = Gtk.Image()
        fcd.set_preview_widget(preview)
        fcd.connect('update-preview', self.update_preview_cb, preview)
        res = fcd.run()
        if res == Gtk.ResponseType.ACCEPT:
            filename = fcd.get_filename()
            if os.path.exists(filename):
                self.background = filename
        fcd.destroy()

    def do_decode(self):

        def on_decode_done(result, error):
            if result is not None:
                self.entry22.set_text(result)
            self.notebook2.set_current_page(1)

        @async_function(on_done=on_decode_done)
        def do_decode_in_thread(pixbuf):
            if pixbuf is not None and self.qrcode_file is not None:
                mtempfile = tempfile.NamedTemporaryFile(mode='w+b',
                                                        prefix='gqrcode',
                                                        delete=True).name
                pixbuf.savev(mtempfile, 'png', [], [])
                command = 'zbarimg %s' % (mtempfile)
                salida = ejecuta(command)
                try:
                    utf8Data = salida.decode()
                    salida = utf8Data.split('QR-Code:')[1]
                except UnicodeDecodeError as e:
                    print(e)
                    utf8Data = salida.decode("utf-8").encode("sjis")
                    salida = utf8Data.decode("utf-8").split('QR-Code:')[1]
                if salida.endswith('\n'):
                    salida = salida[:-1]
            return salida
        pixbuf = self.image22.get_pixbuf()
        do_decode_in_thread(pixbuf)

    def save_encoded(self):
        animation = self.image21.get_animation()
        if animation is None:
            pixbuf = self.image21.get_pixbuf()
            if pixbuf is not None:
                fcd = Gtk.FileChooserDialog(
                    _('Set file to save encode image'),
                    self, Gtk.FileChooserAction.SAVE,
                    buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                             Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
                fcd.set_current_folder(os.getenv('HOME'))
                fcd.set_default_response(Gtk.ResponseType.OK)
                filter = Gtk.FileFilter()
                filter.set_name(_('png files'))
                filter.add_mime_type('image/png')
                filter.add_pattern('*.png')
                fcd.add_filter(filter)
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

#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# <one line to give the program's name and a brief idea of what it does.>
#
# Copyright (C) 2010-2016Lorenzo Carbonell
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
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import WebKit
import os
import shlex
import subprocess
import comun
import qrcode
import qrcode.image.svg
import tempfile
import time
import queue
from comun import _


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


class GQRCode(Gtk.Window):
    def __init__(self):
        self.qrcode_file = None
        #
        Gtk.Window.__init__(self)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_title(comun.APP)
        self.set_default_size(500, 400)
        self.set_resizable(False)
        self.set_icon_from_file(comun.ICON)
        self.connect('destroy', self.close_application)
        hbox = Gtk.HBox(spacing=5)
        hbox.set_border_width(5)
        self.add(hbox)
        #
        self.lat, self.lng = 0.0, 0.0
        #
        notebook1 = Gtk.Notebook()
        hbox.pack_start(notebook1, False, False, 0)
        #
        table12 = Gtk.Table(rows=2, columns=2, homogeneous=False)
        table12.set_border_width(5)
        table12.set_col_spacings(5)
        table12.set_row_spacings(5)
        notebook1.append_page(table12, tab_label=Gtk.Label(_('Text')))
        #
        label1 = Gtk.Label(_('Set text to encode: '))
        label1.set_alignment(0, .5)
        table12.attach(
            label1, 0, 1, 0, 1,
            xoptions=Gtk.AttachOptions.SHRINK,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        self.entry12 = Gtk.Entry()
        self.entry12.set_alignment(0)
        self.entry12.set_width_chars(40)
        table12.attach(
            self.entry12, 1, 2, 0, 1,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        self.button12 = Gtk.Button(_('Encode'))
        self.button12.connect('clicked', self.encode, 'text')
        table12.attach(
            self.button12, 0, 2, 1, 2,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        table11 = Gtk.Table(rows=1, columns=1, homogeneous=False)
        table11.set_border_width(5)
        table11.set_col_spacings(5)
        table11.set_row_spacings(5)
        notebook1.append_page(table11, tab_label=Gtk.Label(_('Geolocation')))
        scrolledwindow0 = Gtk.ScrolledWindow()
        scrolledwindow0.set_policy(Gtk.PolicyType.AUTOMATIC,
                                   Gtk.PolicyType.AUTOMATIC)
        scrolledwindow0.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        scrolledwindow0.set_size_request(500, 400)
        table11.attach(
            scrolledwindow0, 0, 1, 0, 1,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)

        self.viewer = WebKit.WebView()
        self.viewer.connect('title-changed', self.title_changed)
        self.viewer.connect('geolocation-policy-decision-requested',
                            self.on_permission_request)
        self.viewer.open('file://' + comun.HTML_WAI)
        # self.viewer.open('/home/atareao/Escritorio/whereami.html')
        scrolledwindow0.add(self.viewer)
        scrolledwindow0.set_size_request(500, 400)
        #
        self.button1 = Gtk.Button(_('Encode'))
        self.button1.connect('clicked', self.encode, 'geolocation')
        table11.attach(
            self.button1, 0, 1, 1, 2,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        self.coordinates = None
        self.time = time.time()
        self.message_queue = queue.Queue()
        #
        #
        table13 = Gtk.Table(rows=2, columns=2, homogeneous=False)
        table13.set_border_width(5)
        table13.set_col_spacings(5)
        table13.set_row_spacings(5)
        notebook1.append_page(table13,
                              tab_label=Gtk.Label(_('Telephone number')))
        #
        label1 = Gtk.Label(_('Set number to encode:'))
        label1.set_alignment(0, .5)
        table13.attach(
            label1, 0, 1, 0, 1,
            xoptions=Gtk.AttachOptions.SHRINK,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        self.entry13 = Gtk.Entry()
        self.entry13.set_alignment(0)
        self.entry13.set_width_chars(40)
        table13.attach(
            self.entry13, 1, 2, 0, 1,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        self.button13 = Gtk.Button(_('Encode'))
        self.button13.connect('clicked', self.encode, 'telephone')
        table13.attach(
            self.button13, 0, 2, 1, 2,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        table14 = Gtk.Table(rows=2, columns=2, homogeneous=False)
        table14.set_border_width(5)
        table14.set_col_spacings(5)
        table14.set_row_spacings(5)
        notebook1.append_page(table14,
                              tab_label=Gtk.Label(_('Email')))
        #
        label1 = Gtk.Label(_('Set email:'))
        label1.set_alignment(0, .5)
        table14.attach(
            label1, 0, 1, 0, 1,
            xoptions=Gtk.AttachOptions.SHRINK,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        self.entry14 = Gtk.Entry()
        self.entry14.set_alignment(0)
        self.entry14.set_width_chars(40)
        table14.attach(
            self.entry14, 1, 2, 0, 1,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        button14 = Gtk.Button(_('Encode'))
        button14.connect('clicked', self.encode, 'email')
        table14.attach(
            button14, 0, 2, 1, 2,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        table15 = Gtk.Table(rows=2, columns=2, homogeneous=False)
        table15.set_border_width(5)
        table15.set_col_spacings(5)
        table15.set_row_spacings(5)
        notebook1.append_page(table15,
                              tab_label=Gtk.Label(_('Url')))
        #
        label1 = Gtk.Label(_('Set url:'))
        label1.set_alignment(0, .5)
        table15.attach(
            label1, 0, 1, 0, 1,
            xoptions=Gtk.AttachOptions.SHRINK,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        self.entry15 = Gtk.Entry()
        self.entry15.set_alignment(0)
        self.entry15.set_width_chars(40)
        table15.attach(
            self.entry15, 1, 2, 0, 1,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        button15 = Gtk.Button(_('Encode'))
        button15.connect('clicked', self.encode, 'url')
        table15.attach(
            button15, 0, 2, 1, 2,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        table16 = Gtk.Table(rows=3, columns=2, homogeneous=False)
        table16.set_border_width(5)
        table16.set_col_spacings(5)
        table16.set_row_spacings(5)
        notebook1.append_page(table16,
                              tab_label=Gtk.Label(_('Wifi Login')))
        #
        label1 = Gtk.Label(_('SSID/Network name:'))
        label1.set_alignment(0, .5)
        table16.attach(
            label1, 0, 1, 0, 1,
            xoptions=Gtk.AttachOptions.SHRINK,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        self.entry161 = Gtk.Entry()
        self.entry161.set_alignment(0)
        self.entry161.set_width_chars(40)
        table16.attach(
            self.entry161, 1, 2, 0, 1,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        label1 = Gtk.Label(_('Password:'))
        label1.set_alignment(0, .5)
        table16.attach(
            label1, 0, 1, 1, 2,
            xoptions=Gtk.AttachOptions.SHRINK,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        self.entry162 = Gtk.Entry()
        self.entry162.set_visibility(False)
        self.entry162.set_alignment(0)
        self.entry162.set_width_chars(40)
        table16.attach(
            self.entry162, 1, 2, 1, 2,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)
        #
        label1 = Gtk.Label(_('Network type:'))
        label1.set_alignment(0, .5)
        table16.attach(
            label1, 0, 1, 2, 3,
            xoptions=Gtk.AttachOptions.SHRINK,
            yoptions=Gtk.AttachOptions.SHRINK)
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
        table16.attach(self.combobox163, 1, 2, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        button16 = Gtk.Button(_('Encode'))
        button16.connect('clicked', self.encode, 'wifi')
        table16.attach(
            button16, 0, 2, 3, 4,
            xoptions=Gtk.AttachOptions.FILL,
            yoptions=Gtk.AttachOptions.SHRINK)        #
        #
        #
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
        #
        self.show_all()

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

        menubar.append(self.filem)
        self.filehelp = Gtk.Menu.new()
        self.fileh = Gtk.MenuItem.new_with_label(_('Help'))
        self.fileh.set_submenu(self.get_help_menu())
        #
        menubar.append(self.fileh)

    def on_menu_clicked(self, widget, option):
        if option == 'save-as':
            self.save_encoded()
        elif option == 'load':
            self.load_qrcode()

    def get_help_menu(self):
        help_menu = Gtk.Menu()
        #
        homepage_item = Gtk.MenuItem(label=_(
            'Homepage'))
        homepage_item.connect('activate',
                              lambda x: webbrowser.open('http://www.atareao.es\
/apps/my-weather-indicator-para-ubuntu/'))
        homepage_item.show()
        help_menu.append(homepage_item)
        #
        help_item = Gtk.MenuItem(label=_(
            'Get help online...'))
        help_item.connect('activate',
                          lambda x: webbrowser.open('http://www.atareao.es\
/apps/my-weather-indicator-para-ubuntu/'))
        help_item.show()
        help_menu.append(help_item)
        #
        translate_item = Gtk.MenuItem(label=_(
            'Translate this application...'))
        translate_item.connect('activate',
                               lambda x: webbrowser.open('http://www.atareao.es\
/apps/my-weather-indicator-para-ubuntu/'))
        translate_item.show()
        help_menu.append(translate_item)
        #
        bug_item = Gtk.MenuItem(label=_(
            'Report a bug...'))
        bug_item.connect('activate',
                         lambda x: webbrowser.open('https://github.com/atareao\
/my-weather-indicator/issues'))
        bug_item.show()
        help_menu.append(bug_item)
        #
        separator = Gtk.SeparatorMenuItem()
        separator.show()
        help_menu.append(separator)
        #
        twitter_item = Gtk.MenuItem(label=_(
            'Follow me in Twitter'))
        twitter_item.connect('activate',
                             lambda x: webbrowser.open(
                                'https://twitter.com/atareao'))
        twitter_item.show()
        help_menu.append(twitter_item)
        #
        googleplus_item = Gtk.MenuItem(label=_(
            'Follow me in Google+'))
        googleplus_item.connect('activate',
                                lambda x: webbrowser.open(
                                    'https://plus.google.com/\
118214486317320563625/posts'))
        googleplus_item.show()
        help_menu.append(googleplus_item)
        #
        facebook_item = Gtk.MenuItem(label=_(
            'Follow me in Facebook'))
        facebook_item.connect('activate',
                              lambda x: webbrowser.open(
                                'http://www.facebook.com/elatareao'))
        facebook_item.show()
        help_menu.append(facebook_item)
        #
        about_item = Gtk.MenuItem.new_with_label(_('About'))
        about_item.connect('activate', self.about_action)
        about_item.show()
        separator = Gtk.SeparatorMenuItem()
        separator.show()
        help_menu.append(separator)
        help_menu.append(about_item)
        #
        help_menu.show()
        return help_menu

    def about_action(self, widget):
        ad = Gtk.AboutDialog()
        ad.set_name(comun.APPNAME)
        ad.set_version(comun.VERSION)
        ad.set_copyright('Copyrignt (c) 2011-2016\nLorenzo Carbonell')
        ad.set_comments(_('An application to code and decode') + '\nQRCode')
        ad.set_license(
            """
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
""")
        ad.set_website('http://www.atareao.es')
        ad.set_website_label('http://www.atareao.es')
        ad.set_authors([
            'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_documenters([
            'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_translator_credits("""
Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>\n
""")
        ad.set_logo(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
        ad.set_icon(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
        ad.run()
        ad.destroy()

    def decode(self):
        pixbuf = self.image22.get_pixbuf()
        if pixbuf is not None and self.qrcode_file is not None:
            mtempfile = tempfile.NamedTemporaryFile(mode='w+b',
                                                    prefix='gqrcode',
                                                    delete=True).name
            pixbuf.savev(mtempfile, 'png', [], [])
            command = 'zbarimg %s' % (mtempfile)
            salida = ejecuta(command)
            try:
                utf8Data = salida.decode("ascii")
                salida = utf8Data.split('QR-Code:')[1]
            except UnicodeDecodeError as e:
                print(e)
                utf8Data = salida.decode("utf-8").encode("sjis")
                salida = utf8Data.decode("utf-8").split('QR-Code:')[1]
            if salida.endswith('\n'):
                salida = salida[:-1]
            self.entry22.set_text(salida)
            self.notebook2.set_current_page(1)

    def encode(self, widget, option):
        if option == 'geolocation':
            to_encode = 'geo:%1.4f,%1.4f' % (self.lat, self.lng)
        elif option == 'text':
            to_encode = self.entry12.get_text()
        elif option == 'telephone':
            to_encode = 'TEL:'+self.entry13.get_text()
        elif option == 'email':
            to_encode = 'MAILTO:'+self.entry14.get_text()
        elif option == 'url':
            to_encode = self.entry15.get_text()
            if not to_encode.startswith('http://') and\
                    not to_encode.startswith('https://'):
                if to_encode.startswith('//'):
                    to_encode = 'http:' + to_encode
                elif to_encode.startswith('/'):
                    to_encode = 'http:/' + to_encode
                else:
                    to_encode = 'http://' + to_encode
        elif option == 'wifi':
            ssid = self.entry161.get_text()
            password = self.entry162.get_text()
            network_type = get_selected_value_in_combo(self.combobox163)
            print(ssid, password, network_type)
            to_encode = 'WIFI:T:%s;S:%s;P:%s;;' % (
                network_type, ssid, password)
        else:
            return
        qr = qrcode.QRCode(
                           version=0,
                           error_correction=qrcode.constants.ERROR_CORRECT_L,
                           box_size=100,
                           border=10)
        qr.add_data(to_encode)
        factory = qrcode.image.svg.SvgFillImage
        image = qrcode.make(to_encode, image_factory=factory)
        mtempfile = get_temporary_name()
        f = open(mtempfile, 'wb')
        image.save(f)
        f.close()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(mtempfile, 400, 400)
        self.image21.set_from_pixbuf(pixbuf)
        if os.path.exists(mtempfile):
            os.remove(mtempfile)
        self.notebook2.set_current_page(0)
        self.entry21.set_text(to_encode)

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
        self.decode()

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

    def save_encoded(self):
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

    def close_application(self, widget):
        self.destroy()

    def search_location(self):
        self.set_wait_cursor()
        self.web_send('findme()')
        self.set_normal_cursor()

    '''
    ##########################ENGINE####################################
    '''

    def inicialize(self):
        self.web_send('mlat=%s;' % (self.lat))
        self.web_send('mlon=%s;' % (self.lon))

    def work(self):
        while Gtk.events_pending():
            Gtk.main_iteration()
        msg = self.web_recv()
        print(' **** msg **** ')
        print(msg)
        print(' **** *** **** ')
        if msg:
            try:
                if msg.startswith('lon='):
                    longitude, latitude = msg.split(',')
                    longitude = longitude[4:]
                    latitude = latitude[4:]
                    self.search_location()  # latitude, longitude)
                    print(self.lat, self.lng)
                    print(latitude, longitude)
                    self.lat = float(latitude)
                    self.lng = float(longitude)
                    self.web_send('center(%s, %s)' % (self.lat, self.lng))
            except Exception as e:
                msg = None
                print('Error: %s' % e)
        if msg == 'exit':
            self.close_application(None)

    def on_permission_request(self, widget, frame, geolocationpolicydecision):
        WebKit.geolocation_policy_allow(geolocationpolicydecision)
        return True

    '''
    #########################BROWSER####################################
    '''

    def title_changed(self, widget, frame, title):
        if title != 'null':
            self.message_queue.put(title)
            self.work()

    def web_recv(self):
        if self.message_queue.empty():
            return None
        else:
            msg = self.message_queue.get()
            print('recivied: %s' % (msg))
            return msg

    def web_send(self, msg):
        print('send: %s' % (msg))
        self.viewer.execute_script(msg)

    def set_wait_cursor(self):
        self.get_root_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))
        while Gtk.events_pending():
            Gtk.main_iteration()

    def set_normal_cursor(self):
        self.get_root_window().set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))
        while Gtk.events_pending():
            Gtk.main_iteration()


if __name__ == '__main__':
    gqrcode = GQRCode()
    Gtk.main()
    exit(0)

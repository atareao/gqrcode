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
    gi.require_version('GLib', '2.0')
    gi.require_version('GObject', '2.0')
    gi.require_version('GdkPixbuf', '2.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GdkPixbuf
import webbrowser
from .mainwindow import MainWindow
from . import comun
from .comun import _


class MainApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(
            self,
            application_id='es.atareao.gqrcode',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.license_type = Gtk.License.GPL_3_0

    def do_shutdown(self):
        Gtk.Application.do_shutdown(self)

    def on_quit(self, widget, data):
        self.quit()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        def create_action(name,
                          callback=self.action_clicked,
                          var_type=None,
                          value=None):
            if var_type is None:
                action = Gio.SimpleAction.new(name, None)
            else:
                action = Gio.SimpleAction.new_stateful(
                    name,
                    GLib.VariantType.new(var_type),
                    GLib.Variant(var_type, value)
                )
            action.connect('activate', callback)
            return action

        self.add_action(create_action("quit", callback=lambda *_: self.quit()))

        self.set_accels_for_action('app.add', ['<Ctrl>A'])
        self.set_accels_for_action('app.open', ['<Ctrl>O'])
        self.set_accels_for_action('app.quit', ['<Ctrl>Q'])
        self.set_accels_for_action('app.about', ['<Ctrl>F'])

        self.add_action(create_action(
            'open',
            callback=self.on_headbar_clicked))
        self.add_action(create_action(
            'load',
            callback=self.on_headbar_clicked))
        self.add_action(create_action(
            'reset',
            callback=self.on_headbar_clicked))
        self.add_action(create_action(
            'close',
            callback=self.on_headbar_clicked))
        self.add_action(create_action(
            'save',
            callback=self.on_headbar_clicked))
        self.add_action(create_action(
            'save_as',
            callback=self.on_headbar_clicked))

        self.add_action(create_action(
            'goto_homepage',
            callback=lambda x, y: webbrowser.open(
                'https://www.atareao.es/')))
        self.add_action(create_action(
            'goto_code',
            callback=lambda x, y: webbrowser.open(
                'https://github.com/atareao/gqrcode')))
        self.add_action(create_action(
            'goto_bug',
            callback=lambda x, y: webbrowser.open(
                'https://github.com/atareao/gqrcode/issues')))
        self.add_action(create_action(
            'goto_sugestion',
            callback=lambda x, y: webbrowser.open(
                'https://blueprints.launchpad.net/gqrcode')))
        self.add_action(create_action(
            'goto_translation',
            callback=lambda x, y: webbrowser.open(
                'https://translations.launchpad.net/gqrcode')))
        self.add_action(create_action(
            'goto_questions',
            callback=lambda x, y: webbrowser.open(
                'https://answers.launchpad.net/gqrcode')))
        self.add_action(create_action(
            'goto_twitter',
            callback=lambda x, y: webbrowser.open(
                'https://twitter.com/atareao')))
        self.add_action(create_action(
            'goto_google_plus',
            callback=lambda x, y: webbrowser.open(
                'https://plus.google.com/\
118214486317320563625/posts')))
        self.add_action(create_action(
            'goto_facebook',
            callback=lambda x, y: webbrowser.open(
                'http://www.facebook.com/elatareao')))
        self.add_action(create_action(
            'goto_donate',
            callback=lambda x, y: webbrowser.open(
                'https://www.atareao.es/donar/')))
        self.add_action(create_action(
            'about',
            callback=self.on_about_activate))
        self.add_action(create_action(
            'none',
            callback=self.do_none))
        action_toggle = Gio.SimpleAction.new_stateful(
            "toggle", None, GLib.Variant.new_boolean(False))
        action_toggle.connect("change-state", self.toggle_toggled)
        self.add_action(action_toggle)

        lbl_variant = GLib.Variant.new_string("h3")
        new_action = Gio.SimpleAction.new_stateful("new",
                                                   lbl_variant.get_type(),
                                                   lbl_variant)
        new_action.connect("activate", self.activate_radio)
        new_action.connect("change-state", self.toggle_heading)
        self.add_action(new_action)

        action_heading = Gio.SimpleAction.new_stateful(
            "heading",
            GLib.VariantType.new("s"),
            GLib.Variant("s", "h1"))
        action_heading.connect("activate", self.activate_radio)
        action_heading.connect("change-state", self.toggle_heading)
        self.add_action(action_heading)

    def activate_radio(self, widget, action, parameter=None):
        self.win.menu['lists'].set_label(action.get_string())
        widget.set_state(action)

    def heading(self, action):
        print(action)

    def toggle_heading(self, action, state):
        print(action, state)

    def do_activate(self):
        self.win = MainWindow(self)
        self.add_window(self.win)
        self.win.show()

    def action_clicked(self, action, variant):
        print(action, variant)
        if variant:
            action.set_state(variant)

    def on_headbar_clicked(self, action, optional):
        self.win.on_toolbar_clicked(action, action.get_name())

    def on_preferences_clicked(self, widget, optional):
        pass
        '''
        cm = PreferencesDialog(self.win)
        if cm.run() == Gtk.ResponseType.ACCEPT:
            cm.close_ok()
        cm.destroy()
        '''

    def on_support_clicked(self, widget, optional):
        pass
        '''
        dialog = SupportDialog(self.win)
        dialog.run()
        dialog.destroy()
        '''

    def on_about_activate(self, widget, optional):
        ad = Gtk.AboutDialog(comun.APPNAME, self.win)
        ad.set_name(comun.APPNAME)
        ad.set_version(comun.VERSION)
        ad.set_copyright('Copyrignt (c) 2017\nLorenzo Carbonell')
        ad.set_comments(_('QRCode coder and decoder'))
        ad.set_license('''
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
''')
        ad.set_website('http://www.atareao.es')
        ad.set_website_label('http://www.atareao.es')
        ad.set_authors([
            'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_documenters([
            'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_translator_credits('\
Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>\n')
        ad.set_program_name(comun.APPNAME)
        ad.set_logo(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
        ad.run()
        ad.destroy()

    def do_none(self, *args):
        pass

    def toggle_toggled(self, action, state):
            action.set_state(state)
            Gtk.Settings.get_default().set_property(
                "gtk-application-prefer-dark-theme", state)


def main():
    app = MainApplication()
    app.run('')


if __name__ == "__main__":
    main()

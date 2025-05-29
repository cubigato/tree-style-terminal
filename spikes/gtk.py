#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Vte, GLib

class TerminalWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Meine Terminal-App")
        self.set_default_size(800, 600)

        term = Vte.Terminal()
        term.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            None,
            ["/bin/bash"],
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
        )
        self.add(term)

win = TerminalWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

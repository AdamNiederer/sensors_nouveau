#! /usr/bin/python
# -*- coding: utf-8 -*-

###
### sensor_noveau.py
### Copyright 2015 Adam Niederer
### License: GPLv2+
### 

import signal
import json
import random

import sensors
import gtk
import appindicator

def buildmenu():
    menu = gtk.Menu()

    item_prefs = gtk.MenuItem('Preferences')
    item_quit = gtk.MenuItem('Quit')

    item_prefs.connect('activate', prefs)
    item_quit.connect('activate', quit)

    menu.append(item_prefs)
    menu.append(item_quit)

    menu.show_all()
    indicator.set_menu(menu)
    return menu

def buildwindow():
    prefswindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
    prefswindow.set_title('Preferences')
    prefswindow.set_position(gtk.WIN_POS_CENTER)
    prefswindow.set_resizable(False)
    prefswindow.set_border_width(10)
    tree = gtk.TreeView()
    store = gtk.TreeStore(str, str)
    column_name = gtk.TreeViewColumn('Sensor')
    render_name = gtk.CellRendererText()
    column_name.pack_start(render_name, True)
    column_temp = gtk.TreeViewColumn('Value')
    render_temp = gtk.CellRendererText()
    column_temp.pack_start(render_temp, True)
    tree.append_column(column_name)
    tree.append_column(column_temp)
    column_name.add_attribute(render_name, 'text', 0);
    column_temp.add_attribute(render_temp, 'text', 1);

    for chip in chips:
        it = store.append(None, [chip, ''])
        for feature in chip:
            store.append(it, (feature.label, str(feature.get_value())))

    tree.set_model(store)
    prefswindow.add(tree)
    return prefswindow

# GTK-Bound Methods:

def prefs(_):
    window.show_all()

def quit(_):
    gtk.main_quit()
    sensors.cleanup()

def update(_):
    indicator.set_label(str(int(selected.get_value())) + '°C')
    global chips
    chips = []
    for chip in sensors.iter_detected_chips():
        chips.append(chip)
        for feature in chip:
            print feature.get_value()
    return True
        
# Main()

chips = []
selected = None 
indicator = appindicator.Indicator('sensor-noveau', 'kek.svg', appindicator.CATEGORY_HARDWARE)
indicator.set_status(appindicator.STATUS_ACTIVE)

signal.signal(signal.SIGINT, signal.SIG_DFL)
sensors.init()

for chip in sensors.iter_detected_chips():
    chips.append(chip)
    for feature in chip: # Working around PySensors' incomplete implementation
        selected = feature
        break

menu = buildmenu()
window = buildwindow()

indicator.set_menu(menu)
gtk.timeout_add(500, update, indicator)
gtk.main()

#! /usr/bin/python
# -*- coding: utf-8 -*-

###
### sensor_nouveau.py
### Copyright 2015 Adam Niederer
### License: GPLv2+
### 

import signal
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
	global store
	global tree
	prefswindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
	prefswindow.set_size_request(250, 200)
	prefswindow.set_title('Preferences')
	prefswindow.set_position(gtk.WIN_POS_CENTER)
	prefswindow.set_resizable(False)
	prefswindow.set_border_width(10)
 	prefswindow.connect('delete-event', hide)
	tree = gtk.TreeView()
	tree.set_name("tree")
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

def updatewindow(window):
	global selected
        it = store.get_iter_first()
	for chip in chips:
		itc = store.iter_children(it)
		for feature in chip:
			store.set(itc, 1, str(feature.get_value()))
			itc = store.iter_next(itc)
                it = store.iter_next(it)
	row = tree.get_selection()
	if row != None:
		srow = row.get_selected_rows()[1]
		if srow != [] and len(srow[0]) != 1:
			i = 0
			for feature in chips[srow[0][0]]: # Working around PySensors 
				if i == srow[0][1]:
					selected = feature
				i += 1
	return True


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
	return True
		
def hide(window, event):
	window.hide()
	return True

# Main()

global selected

chips = []
features = {}
selected = None 
indicator = appindicator.Indicator('sensor-nouveau', '/usr/share/unity/icons/panel-shadow.png', appindicator.CATEGORY_HARDWARE)
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
gtk.timeout_add(500, updatewindow, window)
gtk.main()

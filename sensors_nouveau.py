#! /usr/bin/python
# -*- coding: utf-8 -*-

###
### sensor_nouveau.py
### Copyright 2015 Adam Niederer
### License: GPLv2+
### 

import signal
import sensors
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GLib as glib

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
	prefswindow = gtk.Window(gtk.WindowType.TOPLEVEL)
	prefswindow.set_size_request(250, 200)
	prefswindow.set_title('Preferences')
	prefswindow.set_position(gtk.WindowPosition.CENTER)
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
		it = store.append(None, [str(chip), ''])
		for feature in chip:
			store.append(it, (feature.label, str(feature.get_value())))

	tree.set_model(store)

	stack = gtk.Stack()
	stack.set_transition_type(gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
	stack.set_transition_duration(100)

	stackvbox = gtk.VBox.new(False, 0)
	stackhbox = gtk.HBox.new(False, 0)
	prefsvbox = gtk.VBox.new(False, 10)
	farhbox = gtk.HBox.new(False, 0)
	iconhbox = gtk.HBox.new(False, 0)
	prefixhbox = gtk.HBox.new(False, 0)

	farlabel = gtk.Label()
	farlabel.set_markup("Display Fahrenheit");
	farswitch = gtk.Switch()
	farswitch.connect("notify::active", switch_far)
	farswitch.set_active(False)
	farhbox.pack_start(farlabel, False, True, 0)
	farhbox.pack_end(farswitch, False, True, 0)

	iconlabel = gtk.Label()
	iconlabel.set_markup("Use Icon")
	iconbrowse = gtk.Button.new_with_label("Browse...")
	iconhbox.pack_start(iconlabel, False, False, 0)
	iconhbox.pack_end(iconbrowse, False, False, 0)
	iconbrowse.connect("clicked", iconupdate)

	prefixlabel = gtk.Label()
	prefixlabel.set_markup("Prefix")
	prefixentry = gtk.Entry()
	prefixentry.set_width_chars(8)
	prefixentry.set_max_width_chars(8)
	prefixentry.connect('changed', prefixupdate);
	prefixhbox.pack_start(prefixlabel, False, False, 0)
	prefixhbox.pack_end(prefixentry, False, False, 0)

	prefsvbox.pack_start(farhbox, False, True, 0)
	prefsvbox.pack_start(iconhbox, False, True, 0)
	prefsvbox.pack_start(prefixhbox, False, True, 0)
	stack.add_titled(tree, "temps", "Temperature Display")
	stack.add_titled(prefsvbox, "prefs", "Preferences")

	stackswitcher = gtk.StackSwitcher()
	stackswitcher.set_stack(stack)

	stackhbox.set_center_widget(stackswitcher)

	stackvbox.pack_start(stackhbox, False, True, 0)
	stackvbox.pack_start(stack, True, True, 5)

	prefswindow.add(stackvbox)

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

def tempconvert(t):
	if deg == '°C':
		return t
	else:
		return int((t * 1.8) + 32)

# GTK-Bound Methods:

def prefs(_):
	window.show_all()

def quit(_):
	gtk.main_quit()
	sensors.cleanup()

def update(_):
	indicator.set_label(prefix + str(tempconvert(int(selected.get_value()))) + deg, '00°C')
	global chips
	chips = []
	for chip in sensors.iter_detected_chips():
		chips.append(chip)
	return True

def hide(window, event):
	window.hide()
	return True

def switch_far(switch, args):
	global deg
	if switch.get_active():
		deg = '°F'
	else:
		deg = '°C'

def prefixupdate(entry):
	global prefix
	prefix = entry.get_text()

def iconupdate(button):
	global indicator
	iconchooser = gtk.FileChooserDialog("Select an icon", button.get_toplevel(), gtk.FileChooserAction.OPEN, ("Open", gtk.ResponseType.ACCEPT, "Cancel", gtk.ResponseType.CANCEL))
	res = gtk.Dialog.run(iconchooser)
	if res == gtk.ResponseType.ACCEPT:
		indicator.set_icon_full(iconchooser.get_filename(), "Custom Sensor Icon");
	iconchooser.destroy()

# Main()

global selected
global deg
global prefix
global indicator

prefix = ''
deg = '°C'

chips = []
features = {}
selected = None 
indicator = appindicator.Indicator.new('sensor-nouveau', '/usr/share/unity/icons/panel-shadow.png', appindicator.IndicatorCategory.HARDWARE)
indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

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
glib.timeout_add(500, update, indicator)
glib.timeout_add(500, updatewindow, window)
gtk.main()

import gtk
import re
import os
import time
import gobject
import random
from datetime import datetime

basepath = "/home/uovobw/programmi/batmon"
tray = gtk.status_icon_new_from_file(basepath + "/icons/batmon0.png")
loadingtray = gtk.status_icon_new_from_file(basepath + "/icons/charging.png")
delay = 5000
WARNING_LEVEL = 10
okbutton = None
counter = 0

def get_battery(out):
    # stupid hack for resume bug
    try:
        rawValue = re.findall(r'\d+\.\d+\%',out)[0]
    except IndexError:
        rawValue = "0"
    # convert to int
    value = int(float(rawValue.replace("%","")))
    return value

def is_charging(out):
    return out.__contains__(" charging") or out.__contains__(" Charging")

def is_missing(out):
    return out.__contains__("not available")

def check_for_new():
    global loadingtray
    global tray
    global counter
    # get the value from acpitool
    acpiToolOut = os.popen("acpitool -b").read()

    # check for charging status
    if is_charging(acpiToolOut):
        loadingtray.set_visible(True)
    else:
        loadingtray.set_visible(False)

    if is_missing(acpiToolOut):
        return True

    value = get_battery(acpiToolOut)
    if value <= WARNING_LEVEL and not is_charging(acpiToolOut):
        if counter == 10:
            counter = 0
            okdialog = gtk.MessageDialog(type=gtk.MESSAGE_OTHER)
            okbutton = gtk.Button("Information")
            okdialog.add_button("OK", 0)
            okdialog.set_title("Battery critical")
            okdialog.set_markup(str(value) + "% left")
            okdialog.run()
            okdialog.destroy()
        else:
            counter += 1
    # update icon and tooltip
    tray.set_from_file(basepath + "/icons/batmon" + str(value) + ".ico")
    tray.set_tooltip(str(value))
    return True

if __name__ == '__main__':
    gobject.timeout_add(delay, check_for_new)
    gtk.main()


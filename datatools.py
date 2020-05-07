#!/usr/bin/env python3
import os
import subprocess
import time
import gi
import configparser
import re
from datetime import datetime
gi.require_version('Pango', '1.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Pango, Gdk


"""
Budgie ShowData
Author: TJ Thornsberry
"""

# paths
prefspath = os.path.join(
    os.environ["HOME"], ".config", "budgie-extras", "showdata"
)

vnstat_config_file = os.path.join(
    os.environ["HOME"], ".vnstatrc"
)

app_path = os.path.dirname(os.path.abspath(__file__))
user = os.environ["USER"]


try:
    os.makedirs(prefspath)
except FileExistsError:
    pass

try:
    os.makedirs(vnstat_config_file)
    # TODO default config
except FileExistsError:
    pass

# config initialization
config = configparser.ConfigParser()
config_file = os.path.join(prefspath, "user_settings.ini")
data = os.path.join(app_path, "ShowData")
panelrunner = os.path.join(app_path, "bshowdatausage_panelrunner")
vnstat_config = {}


with open(vnstat_config_file) as fp:
    Lines = fp.readlines()
    for line in Lines:
        variable = line.split(" ")
        vnstat_config[variable[0]] = variable[1].strip("\n")


def get_days_in_cycle():
    now = datetime.now()
    delta1 = datetime(now.year, now.month, int("11")-1)
    delta2 = delta1 - now
    if delta2.days < 0:
        delta1 = datetime(now.year, now.month+1, int("11")-1)
    return (delta1 - now).days

def get_interfaces():
    info = subprocess.run(["vnstat", "--iflist"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True).stdout
    info = re.sub("[\(\[].*?[\)\]]", "", info)
    interfaces = info.strip("Available Interfaces: ").strip(" \n").split(" ")
    interfaces = [x for x in interfaces if x]
    return interfaces


def create_config():
    # all settings are the default values of the configuration file.
    config['COLORS'] = {'yesterday': "65535,65535,65535",
                        'today': "65535,65535,65535",
                        'week': "65535,65535,65535",
                        'month': "65535,65535,65535",
                        'shadow': "0,0,0"}
    config['MUTE'] = {'yesterday': False,
                      'today': False,
                      'week': False,
                      'month': False,
                      'shadow': False,
                      'cycle': False}
    config['GENERAL'] = {'position': "900, 50",
                         'custom_position': False,
                         'display': 0,
                         'interface': get_interfaces()[0]}
    with open(config_file, 'w') as cf:
        config.write(cf)


try:
    with open(config_file) as cf:
        config.read_file(cf)
except IOError:
    create_config()


def get(command):
    try:
        return subprocess.check_output(command).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        pass


def get_pid(proc):
    return get(["pgrep", "-f", "-u", user, proc]).splitlines()


def restart_data():
    for proc in [data, panelrunner]:
        try:
            for p in get_pid(proc):
                subprocess.Popen(["kill", p])
        except AttributeError:
            pass
    subprocess.Popen(panelrunner)


def get_area():
    # width of the primary screen.
    dspl = Gdk.Display()
    dsp = dspl.get_default()
    prim = dsp.get_primary_monitor()
    geo = prim.get_geometry()
    return [geo.width, geo.height]


def get_textposition():
    pos = config["GENERAL"]["position"].split(",")
    x = int(pos[0])
    y = int(pos[1])
    custom = config["GENERAL"].getboolean("custom_position")
    return custom, x, y


def hexcolor(rgb):
    rgb = rgb.split(",")
    c = [int((int(n) / 65535) * 255) for n in rgb]
    return '#%02x%02x%02x' % (c[0], c[1], c[2])


def get_font():
    key = ["org.gnome.desktop.wm.preferences", "titlebar-font"]
    fontdata = get(["gsettings", "get", key[0], key[1]]).strip("'")
    fdscr = Pango.FontDescription(fontdata)
    return Pango.FontDescription.get_family(fdscr)

# =================================================================
# =                 Author: Cameron Percival                      =
# =================================================================


import os
import sys
import shutil
import psutil
import datetime
# import time
import subprocess
import threading  # noqa
import gi
# import configparser
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gtk  # noqa

# =====================================================
#               Global Variables
# =====================================================
sudo_username = os.getlogin()
home = "/home/" + str(sudo_username)

# =====================================================
#               Create log file
# =====================================================

log_dir="/var/log/arcolinux/"
aai_log_dir="/var/log/arcolinux/aai/"

def create_log(self):
    print('Making log in /var/log/arcolinux')
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d-%H-%M-%S" )
    destination = aai_log_dir + 'aai-log-' + time
    command = 'sudo pacman -Q > ' + destination
    subprocess.call(command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
    #GLib.idle_add(show_in_app_notification, self, "Log file created")


# =====================================================
#               GLOBAL FUNCTIONS
# =====================================================


def _get_position(lists, value):
    data = [string for string in lists if value in string]
    position = lists.index(data[0])
    return position

# =====================================================
#               PERMISSIONS
# =====================================================

def permissions(dst):
    try:
        groups = subprocess.run(["sh", "-c", "id " +
                                 sudo_username],
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        for x in groups.stdout.decode().split(" "):
            if "gid" in x:
                g = x.split("(")[1]
                group = g.replace(")", "").strip()
        subprocess.call(["chown", "-R",
                         sudo_username + ":" + group, dst], shell=False)

    except Exception as e:
        print(e)

# =====================================================
#               APP INSTALLATION
# =====================================================
def install(package):
    pkg=package.strip("\n")
    inst_str = "pacman -S " + pkg + " --needed --noconfirm"

    subprocess.call(inst_str.split(" "),
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)

# =====================================================
#               APP UNINSTALLATION
# =====================================================
def uninstall(package):
    pkg=package.strip("\n")
    uninst_str = "pacman -Rs " + pkg + " --noconfirm"

    subprocess.call(uninst_str.split(" "),
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
    
# =====================================================
#               APP QUERY
# =====================================================
def query_pkg(package):
    #first we need to strip the new line escape sequence to ensure we don't get incorrect outcome
    pkg=package.strip("\n")
    #create the query
    #We could use pacman for this, but there's two issues; 1) pacman ALWAYS outputs, and 2) it's MUCH slower
    #query_str = "pacman -Qs " + pkg + " --noconfirm"
    query_str = "which " + pkg
    #run the query - using Popen because it actually suits this use case a bit better.
    process = subprocess.Popen(query_str.split(" "),
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    #capture output, if any
    output = process.communicate()[0]
    #With which, if there is an output, it means the package is installed
    if len(output)>0:
        return True
    return False

def cache(package, path):
    #first we need to strip the new line escape sequence to ensure we don't get incorrect outcome
    pkg=package.strip("\n")
    #Determine whether we need to re-create the "cache", or not.

    #create the query
    #We could use pacman for this, but there's two issues; 1) pacman ALWAYS outputs, and 2) it's MUCH slower
    query_str = "pacman -Si " + pkg + " --noconfirm" #This is a bit slower, but seems to return much more consistently.
    #run the query - using Popen because it actually suits this use case a bit better.
    process = subprocess.Popen(query_str.split(" "),
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    #capture output, if any
    output = process.communicate()[0]
    #split the output at line breaks. split 0 = package name/location, split 1 = description.
    split = output.splitlines()
    #print(split)
    #Return description or advise unable to locate

    if len(output)>0:
        desc = str(split[3])
        #Ok, so this is a little fancy: there is formatting from the output which we wish to ignore (ends at 19th character)
        #and there is a remenant of it as the last character - usually a single or double quotation mark, which we also need to ignore
        description = desc[19:-1]
        #writing to a caching file with filename matching the package name
        filename = path+pkg
        file = open(filename, "w")
        file.write(description)
        file.close()
        return description
    return "No Description Found"

def file_lookup(package, path):
    #first we need to strip the new line escape sequence to ensure we don't get incorrect outcome
    pkg=package.strip("\n")
    output = ""
    filename = path+pkg
    file = open(filename, "r")
    output = file.read()
    file.close()
    if len(output)>0:
        return output
    return "No Description Found"

def obtain_pkg_description(package):
    #This is a pretty simple function now, decide how to get the information, then get it.
    #processing variables.
    output = ""
    path = "cache/"
    #First we need to determine whether to pull from cache or pacman.
    if os.path.exists(path+package.strip("\n")):
        output = file_lookup(package, path)
    #file doesn't exist, so create a blank copy
    else:
        output = cache(package, path)
    return output
#######ANYTHING UNDER THIS LINE IS CURRENTLY UNUSED!

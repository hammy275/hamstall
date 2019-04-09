"""hamstall: A package manager for managing archives
    Copyright (C) 2019  hammy3502

    hamstall is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    hamstall is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with hamstall.  If not, see <https://www.gnu.org/licenses/>."""

import re
import sys
import os
from shutil import copyfile, rmtree, move
try:
    import requests
except:
    print('Please install requests! The command "pip3 install requests" or "python3 -m pip install requests" on Linux systems should do the job!')
    sys.exit()

import file
import config
import generic

def manage(program):
    """Manage an already installed program"""
    while True:
        print("Enter an option to manage " + program + ":")
        print("b - Create binlinks for " + program)
        print("p - Add " + program + " to PATH")
        print("u - Uninstall " + program)
        print("r - Remove all binlinks + PATHs for " + program)
        print("E - Exit program management")
        option = generic.get_input("[b/p/u/r/E]", ['b','p','u','r','e'], 'e')
        if option == 'b':
            binlink(program)
        elif option == 'p':
            pathify(program)
        elif option == 'u':
            uninstall(program)
            sys.exit()
        elif option == 'r':
            file.remove_line(program, "~/.hamstall/.bashrc", 'poundword')
        elif option == 'e':
            sys.exit()

def binlink(program_internal_name):
    """Creates an alias to run a program from its directory"""
    while True:
        files = os.listdir(file.full('~/.hamstall/bin/' + program_internal_name + '/'))
        print(' '.join(files))
        file_chosen = 'Cool fact. This line was originally written on line 163.'
        while file_chosen not in files: #Get file to binlink from user
            file_chosen = input('Please enter a file listed above. If you would like to cancel, press CTRL+C: ')
        line_to_add = 'alias ' + file_chosen + "='cd " + file.full('~/.hamstall/bin/') + program_internal_name + '/ && ./' + file_chosen + "' # " + program_internal_name + "\n"
        config.vprint("Adding alias to bashrc")
        file.add_line(line_to_add, "~/.hamstall/.bashrc") #Add an alias to bashrc to cd into the directory of the program and run the specified program
        yn = generic.get_input('Would you like to continue adding files to be run directly? [y/N]', ['y', 'n'], 'n')
        if yn == 'n':
            return

def pathify(program_internal_name):
    """Adds an installed program to PATH"""
    config.vprint('Adding program to PATH')
    line_to_write = "export PATH=$PATH:~/.hamstall/bin/" + program_internal_name + ' # ' + program_internal_name + '\n'
    file.add_line(line_to_write,"~/.hamstall/.bashrc")
    return

def update():
    """Update hamstall after checking for updates"""
    prog_version_internal = config.get_version('prog_internal_version')
    config.vprint("Checking version on GitHub")
    final_version = get_online_version('prog')
    config.vprint('Installed internal version: ' + str(prog_version_internal))
    config.vprint('Version on GitHub: ' + str(final_version))
    if final_version > prog_version_internal:
        print("An update has been found! Installing...")
        config.vprint('Removing old hamstall pys...')
        files = os.listdir()
        for i in files:
            i_num = len(i) - 3
            if i[i_num:len(i)] == '.py':
                os.remove( file.full('~/.hamstall/') + i)
        config.vprint("Downloading new hamstall pys..")
        download_files(['hamstall.py', 'generic.py', 'file.py', 'config.py', 'prog_manage.py'], '~/.hamstall/')
        sys.exit()
        config.vprint("Replacing old hamstall with new version")
    else:
        print("No update found!")
        sys.exit()
    
def erase():
    """Remove hamstall"""
    if not(file.exists(file.full("~/.hamstall/hamstall.py"))):
        print("hamstall not detected so not removed!")
        sys.exit()
    config.vprint('Removing source line from bashrc')
    file.remove_line("~/.hamstall/.bashrc", "~/.bashrc", "word")
    config.vprint('Removing hamstall directory')
    rmtree(file.full('~/.hamstall'))
    print("Hamstall has been removed from your system.")
    print('Please restart your terminal.')
    input('Press return to exit...')
    sys.exit()

def first_time_setup():
    """Create hamstall files in ~/.hamstall"""
    if file.exists(file.full('~/.hamstall/hamstall.py')):
        print('Please don\'t run first time setup on an already installed system!')
        sys.exit()
    print('Installing hamstall to your system...')
    os.mkdir(file.full("~/.hamstall"))
    os.mkdir(file.full("/tmp/hamstall-temp/"))
    os.mkdir(file.full("~/.hamstall/bin"))
    file.create("~/.hamstall/database")
    file.create("~/.hamstall/config")
    file.create("~/.hamstall/.bashrc") #Create directories and files
    file.add_line("Verbose=False\n","~/.hamstall/config") #Write verbosity line to config
    hamstall_file = os.path.realpath(__file__)
    files = os.listdir()
    for i in files:
        i_num = len(i) - 3
        if i[i_num:len(i)] == '.py':
            copyfile(i, file.full('~/.hamstall/') + i)
    version_file = hamstall_file[0:len(hamstall_file) - 14] + 'version'
    copyfile(version_file, file.full('~/.hamstall/version'))
    file.add_line("source ~/.hamstall/.bashrc\n", "~/.bashrc")
    file.add_line("alias hamstall='python3 ~/.hamstall/hamstall.py'\n", "~/.hamstall/.bashrc") #Add bashrc line
    print('First time setup complete!')
    print('Please run the command "source ~/.bashrc" or restart your terminal.')
    print('Afterwards, you may begin using hamstall with the hamstall command!')
    sys.exit()

def verbose_toggle():
    """Toggle verbose mode"""
    config.change_config('Verbose')

def install(program):
    """Install an archive"""
    program_internal_name = file.name(program)
    if file.char_check(program_internal_name):
        print("Error! Archive name contains a space or #!")
        sys.exit()
    config.vprint("Removing old temp directory (if it exists!)")
    try:
        rmtree(file.full("/tmp/hamstall-temp")) #Removes temp directory (used during installs)
    except:
        config.vprint("Temp directory did not exist!")
    config.vprint("Creating new temp directory")
    os.mkdir(file.full("/tmp/hamstall-temp")) #Creates temp directory for extracting archive
    config.vprint("Extracting archive to temp directory")
    file_extension = file.extension(program)
    program = file.spaceify(program)
    if config.vcheck(): #Creates the command to run to extract the archive
        if file_extension == '.tar.gz' or file_extension == '.tar.xz':
            vflag = 'v'
        elif file_extension == '.zip':
            vflag = ''
    else:
        if file_extension == '.tar.gz' or file_extension == '.tar.xz':
            vflag = ''
        elif file_extension == '.zip':
            vflag = '-qq'
    if file_extension == '.tar.gz' or file_extension == '.tar.xz':
        command_to_go = "tar " + vflag + "xf " + program + " -C /tmp/hamstall-temp/"
    elif file_extension == '.zip':
        command_to_go = 'unzip ' + vflag + ' ' + program + ' -d /tmp/hamstall-temp/'
    else:
        print('Error! File type not supported!')
        sys.exit()
    config.vprint('File type detected: ' + file_extension)
    os.system(command_to_go) #Extracts program archive
    config.vprint('Checking for folder in folder')
    if os.path.isdir(file.full('/tmp/hamstall-temp/' + program_internal_name + '/')):
        config.vprint('Folder in folder detected! Using that directory instead...')
        source = file.full('/tmp/hamstall-temp/' + program_internal_name + '/')
        dest = file.full('~/.hamstall/bin/')
    else:
        config.vprint('Folder in folder not detected!')
        source = file.full('/tmp/hamstall-temp')
        dest = file.full('~/.hamstall/bin/' + program_internal_name)
    config.vprint("Moving program to directory")
    move(source,dest)
    config.vprint("Adding program to hamstall list of programs")
    file.add_line(program_internal_name + '\n',"~/.hamstall/database")
    yn = generic.get_input('Would you like to add the program to your PATH? [Y/n]', ['y', 'n'], 'y')
    if yn == 'y':
        pathify(program_internal_name)
    yn = generic.get_input('Would you like to be able to create a binlink? [y/N]', ['y', 'n'], 'n')
    if yn == 'y':
        binlink(program_internal_name)
    config.vprint('Removing old temp directory...')
    try:
        rmtree(file.full("/tmp/hamstall-temp"))
    except:
        config.vprint('Temp folder not found so not deleted!')
    print("Install completed!")
    sys.exit()

def dirinstall(program_path, program_internal_name):
    """Install a directory"""
    config.vprint("Moving folder to hamstall destination")
    move(program_path, file.full("~/.hamstall/bin/"))
    config.vprint("Adding program to hamstall list of programs")
    file.add_line(program_internal_name + '\n',"~/.hamstall/database")
    yn = generic.get_input('Would you like to add the program to your PATH? [Y/n]', ['y', 'n'], 'y')
    if yn == 'y':
        pathify(program_internal_name)
    yn = generic.get_input('Would you like to create a binlink? [y/N]', ['y', 'n'], 'n')
    if yn == 'y':
        binlink(program_internal_name)
    print("Install completed!")
    sys.exit()

def uninstall(program):
    """Uninstall a program"""
    config.vprint("Removing program")
    rmtree(file.full("~/.hamstall/bin/" + program + '/'))
    config.vprint("Removing program from PATH")
    file.remove_line(program,"~/.hamstall/.bashrc", 'poundword')
    config.vprint("Removing program from hamstall list of programs")
    file.remove_line(program,"~/.hamstall/database", 'word')
    print("Uninstall complete!")
    return

def list_programs():
    """List all installed programs"""
    f = open(file.full('~/.hamstall/database'), 'r')
    open_file = f.readlines()
    f.close()
    for l in open_file:
        newl = l.rstrip()
        print(newl)
    sys.exit()

def get_online_version(type):
    """Get current version of hamstall through GitHub
    prog - Program version
    file - .hamstall folder version"""
    version_url = "https://raw.githubusercontent.com/hammy3502/hamstall/master/version"
    version_raw = requests.get(version_url)
    version = version_raw.text
    counter = 0
    for c in version:
        if c == '.':
            spot = counter + 1
            if type == 'file':
                return int(version[0:spot])
            elif type == 'prog':
                return int(version[spot:])
        else:
            counter += 1

def get_file_version(type):
    """Get current version of hamstall from version file
    prog - Program version
    file - .hamstall folder version"""
    f = open(file.full('~/.hamstall/version'), 'r')
    version = f.readlines()
    version = ''.join(version)
    f.close()
    counter = 0
    for c in version:
        if c == '.':
            spot = counter + 1
            if type == 'file':
                return int(version[0:(spot-1)])
            elif type == 'prog':
                return int(version[spot:])
        else:
            counter += 1

def download_files(files, dir):
    """Downloads a list of files and writes them"""
    for i in files:
        r = requests.get("https://raw.githubusercontent.com/hammy3502/hamstall/master/" + i)
        open(file.full(dir + i), 'wb').write(r.content)

verbose = config.vcheck()

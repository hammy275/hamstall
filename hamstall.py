#!/usr/bin/python3

#Hamstall
#A package manager for managing archives
#Written by hammy3502

import os
import argparse
from pathlib import Path
import sys
import re
import getpass
import file
import generic
import prog_manage

###HAMSTALL VERSIONS###

def get_version(type):
    if type == 'prog_internal_version':
        return 2
    elif type == 'file_version':
        return 1
    elif type == 'version':
        return '1.0.0b'


###############Argument Parsing###############

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('-i', "--install", help="Install a .tar.gz, .tar.xz, or .zip")
group.add_argument('-d', "--dirinstall", help="Install a directory")
group.add_argument('-r', "--remove", help="Remove an insatlled program")
group.add_argument('-l', "--list", help="List installed programs", action="store_true")
group.add_argument('-f', "--first", help="Run first time setup", action="store_true")
group.add_argument('-e', "--erase", help="Delete hamstall from your system", action="store_true")
group.add_argument('-v', "--verbose", help="Toggle verbose mode", action="store_true")
group.add_argument('-u', '--update', help="Update hamstall if an update is available", action="store_true")
group.add_argument('-m', '--manage', help="Manage an installed program")
args = parser.parse_args() #Parser stuff

username = getpass.getuser()
if username == 'root':
    print('Note: Running as root user will install programs for the root user to use!')

if not(file.exists('~/.hamstall/hamstall.py')): #hamstall must be installed before doing anything else
    yn = generic.get_input('hamstall is not installed on your system. Would you like to install it? [Y/n]', ['y','n'], 'y')
    if yn == 'y':
        prog_manage.firstTimeSetup()
    else:
        print('hamstall not installed.')
    sys.exit()

file_version = prog_manage.get_file_version('file')
if get_version('file_version') > file_version:
    ##hamstall directory conversion code here##
    sys.exit()

if prog_manage.get_file_version('prog') == 1:
    print('Please manually update hamstall! You can back up your directories in ~/.hamstall !')
    sys.exit()


if args.install != None:
    to_install = args.install #to_install from the argument
    does_archive_exist = file.exists(to_install)
    if does_archive_exist == False:
        print("File to install does not exist!")
        sys.exit()
    program_internal_name = file.name(to_install) #Get the internal name (trim off everything except the file name before the .tar.gz/.tar.xz/.zip
    file_check = file.check_line(program_internal_name, "~/.hamstall/database", 'word') #Checks to see if the file path for the program's uninstall script exists
    if file_check: #Ask to reinstall program
        reinstall = generic.get_input("Application already exists! Would you like to reinstall? [y/N]", ["y", "n"], "n") #Ask to reinstall
        if reinstall == "y":
            prog_manage.uninstall(program_internal_name)
            prog_manage.install(to_install) #Reinstall
        else:
            print("Reinstall cancelled.")
            sys.exit()
    else:
        prog_manage.install(to_install) #No reinstall needed to be asked, install program

if args.dirinstall != None:
    to_install = args.dirinstall
    if os.path.isdir(to_install) == False:
        print("Folder to install does not exist!")
        sys.exit()
    if to_install[len(to_install) - 1] != '/':
        print("Please make sure the directory ends with a / !")
        sys.exit()
    progintnametemp = to_install[0:len(to_install)-1]
    program_internal_name = file.name(progintnametemp + '.tar.gz') #Add .tar.gz to make the original function work (a hackey solution I know)
    file_check = file.check_line(program_internal_name, "~/.hamstall/database", 'word')
    if file_check:
        reinstall = generic.get_input("Application already exists! Would you like to reinstall? [y/N]", ["y", "n"], "n")
        if reinstall == 'y':
            prog_manage.uninstall(program_internal_name)
            prog_manage.dirinstall(to_install, program_internal_name)
        else:
            print("Reinstall cancelled.")
            sys.exit()
    else:
        prog_manage.dirinstall(to_install, program_internal_name)


elif args.remove != None:
    to_uninstall = args.remove
    if file.check_line(to_uninstall, "~/.hamstall/database", 'word'): #If uninstall script exists
        prog_manage.uninstall(to_uninstall) #Uninstall program
    else:
        print("Program does not exist!") #Program doesn't exist
    sys.exit()

elif args.manage != None:
    if file.check_line(args.manage, '~/.hamstall/database', 'word'):
        prog_manage.manage(args.manage)
    else:
        print("Program does not exist!")
    sys.exit()

elif args.list:
    prog_manage.listPrograms() #List programs installed

elif args.first:
    prog_manage.firstTimeSetup() #First time setup

elif args.erase:
    erase_sure = generic.get_input("Are you sure you would like to remove hamstall from your system? [y/N]", ['y', 'n'], 'n')
    if erase_sure == 'y':
        erase_really_sure = generic.get_input('Are you absolutely sure? This will remove all programs installed with hamstall! [y/N]', ['y', 'n'], 'n')
        if erase_really_sure == 'y':
            prog_manage.erase() #Remove hamstall from the system
        else:
            print('Erase cancelled.')
    else:
        print('Erase cancelled.')
    sys.exit()

elif args.verbose: #Verbose toggle
    prog_manage.verboseToggle()

elif args.update:
    prog_manage.update()

else:
    #About hamstall
    print('\nhamstall. A Python based package manager to manage archives.')
    print("Written by: hammy3502\n")
    print('hamstall version: ' + get_version('version'))
    print('Internal version code: ' + str(get_version('file_version')) + "." + str(get_version('prog_internal_version')) + "\n")
    print('For help, type hamstall -h\n') 

#!/usr/bin/python3

"""hamstall
A package manager for managing archives
Written by hammy3502"""

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

import os
import argparse
import sys
import getpass
import shutil
import file
import generic
import prog_manage
import config


"""Argument parsing"""
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('-i', "--install", help="Install a .tar.gz, .tar.xz, or .zip")
group.add_argument('-d', "--dirinstall", help="Install a directory")
group.add_argument('-g', '--gitinstall', help="Install by retrieving a git repository")
group.add_argument('-r', "--remove", help="Remove an insatlled program")
group.add_argument('-l', "--list", help="List installed programs", action="store_true")
group.add_argument('-f', "--first", help="Run first time setup", action="store_true")
group.add_argument('-e', "--erase", help="Delete hamstall from your system", action="store_true")
group.add_argument('-v', "--verbose", help="Toggle verbose mode", action="store_true")
group.add_argument('-u', '--update', help="Update hamstall if an update is available", action="store_true")
group.add_argument('-m', '--manage', help="Manage an installed program")
args = parser.parse_args()  #Parser stuff

username = getpass.getuser()
if username == 'root':
    print('Note: Running as root user will install programs for the root user to use!')

if not(file.exists('~/.hamstall/hamstall.py')):
    """Install hamstall if it doesn't exist"""
    yn = generic.get_input('hamstall is not installed on your system. Would you like to install it? [Y/n]', ['y','n','debug'], 'y')
    if yn == 'y':
        prog_manage.first_time_setup(False)
    elif yn == 'debug':
        prog_manage.first_time_setup(True)
    else:
        print('hamstall not installed.')
    sys.exit()

file_version = prog_manage.get_file_version('file')
if config.get_version('file_version') > file_version:
    ##hamstall directory conversion code here##
    sys.exit()

if prog_manage.get_file_version('prog') == 1: #Online update broke between versions 1 and 2 of hamstall
    print('Please manually update hamstall! You can back up your directories in ~/.hamstall !')
    sys.exit()

if args.install is not None:
    does_archive_exist = file.exists(args.install)
    if not(does_archive_exist):
        print("File to install does not exist!")
        sys.exit()
    program_internal_name = file.name(args.install)  #Get the program name
    file_check = file.check_line(program_internal_name, "~/.hamstall/database", 'word') 
    if file_check:  #Reinstall check
        reinstall = generic.get_input("Application already exists! Would you like to reinstall? [y/N]", ["y", "n"], "n") #Ask to reinstall
        if reinstall == "y":
            prog_manage.uninstall(program_internal_name)
            prog_manage.install(args.install)  #Reinstall
        else:
            print("Reinstall cancelled.")
            sys.exit()
    else:
        prog_manage.install(args.install)  #No reinstall needed to be asked, install program

elif args.gitinstall is not None:
    if shutil.which("git") is None:
        print("git not installed! Please install it before using git install functionality!")
        sys.exit()
    else:
        program_internal_name = file.name(args.gitinstall)
        file_check = file.check_line(program_internal_name, "~/.hamstall/database", 'word') 
        if file_check:
            reinstall = generic.get_input("Application already exists! Would you like to reinstall? [y/N]", ["y", "n"], "n") #Ask to reinstall
            if reinstall == "y":
                prog_manage.uninstall(program_internal_name)
                prog_manage.gitinstall(args.gitinstall, program_internal_name)
            else:
                print("Reinstall cancelled.")
                sys.exit()
        else:
            prog_manage.gitinstall(args.gitinstall, program_internal_name)


elif args.dirinstall is not None:
    if not(os.path.isdir(args.dirinstall)):
        print("Folder to install does not exist!")
        sys.exit()
    if args.dirinstall[len(args.dirinstall) - 1] != '/':
        print("Please make sure the directory ends with a / !")
        sys.exit()
    prog_int_name_temp = args.dirinstall[0:len(args.dirinstall)-1]
    program_internal_name = file.name(prog_int_name_temp + '.tar.gz')  #Add .tar.gz to make the original function work (a hackey solution I know)
    file_check = file.check_line(program_internal_name, "~/.hamstall/database", 'word')
    if file_check:
        reinstall = generic.get_input("Application already exists! Would you like to reinstall? [y/N]", ["y", "n"], "n")
        if reinstall == 'y':
            prog_manage.uninstall(program_internal_name)
            prog_manage.dirinstall(args.dirinstall, program_internal_name)
        else:
            print("Reinstall cancelled.")
            sys.exit()
    else:
        prog_manage.dirinstall(args.dirinstall, program_internal_name)

elif args.remove != None:
    if file.check_line(args.remove, "~/.hamstall/database", 'word'):  #If uninstall script exists
        prog_manage.uninstall(args.remove)  #Uninstall program
    else:
        print("Program does not exist!")  #Program doesn't exist
    sys.exit()

elif args.manage != None:
    if file.check_line(args.manage, '~/.hamstall/database', 'word'):
        prog_manage.manage(args.manage)
    else:
        print("Program does not exist!")
    sys.exit()

elif args.list:
    prog_manage.list_programs()  #List programs installed

elif args.first:
    prog_manage.first_time_setup(False)  #First time setup

elif args.erase:
    erase_sure = generic.get_input("Are you sure you would like to remove hamstall from your system? [y/N]", ['y', 'n'], 'n')
    if erase_sure == 'y':
        erase_really_sure = generic.get_input('Are you absolutely sure? This will remove all programs installed with hamstall! [y/N]', ['y', 'n'], 'n')
        if erase_really_sure == 'y':
            prog_manage.erase()  #Remove hamstall from the system
        else:
            print('Erase cancelled.')
    else:
        print('Erase cancelled.')
    sys.exit()

elif args.verbose:  #Verbose toggle
    prog_manage.verbose_toggle()

elif args.update:
    prog_manage.update()

else:
    #About hamstall
    print("""
hamstall. A Python based package manager to manage archives.
Written by: hammy3502

hamstall Version: {user_version}
Internal Version Code: {file_version}.{prog_version}

For help, type "hamstall -h"
    """.format(user_version=config.get_version("version"), file_version=config.get_version("file_version"), prog_version=config.get_version("prog_internal_version"))
    )

#!/usr/bin/python3

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
group.add_argument('-k', '--remove-lock', help="Remove hamstall lock file (only do this if hamstall isn't already "
                                               "running!", action="store_true")
group.add_argument('-c', '--config', help="Change hamstall options", action="store_true")
args = parser.parse_args()  # Parser stuff

username = getpass.getuser()
if username == 'root':
    print('Note: Running as root user will install programs for the root user to use!')

if config.locked():
    config.vprint("Lock file detected at /tmp/hamstall-lock. " +
                  "Delete this file if you are completely sure no other instances of hamstall are running!")
    if args.remove_lock:
        try:
            os.remove(config.full("/tmp/hamstall-lock"))
            print("Lock removed!")
        except FileNotFoundError:
            print("Lock doesn't exist, so not removed!")
        generic.leave()
    else:
        print("Another instance of hamstall is probably running! Execution halted!")
        sys.exit(2)
else:
    config.lock()

if config.db == {"refresh": True}:
    print("Hang tight! We're finishing up your downgrade...")
    config.create("~/.hamstall/database")
    prog_manage.create_db()
    config.db = config.get_db()
    config.write_db()
    print("We're done! Continuing hamstall execution...")

if not(config.exists('~/.hamstall/hamstall.py')):
    """Install hamstall if it doesn't exist"""
    yn = generic.get_input('hamstall is not installed on your system. Would you like to install it? [Y/n]',
                           ['y', 'n', 'debug'], 'y')
    if yn == 'y':
        prog_manage.first_time_setup(False)
    elif yn == 'debug':
        prog_manage.first_time_setup(True)
    else:
        print('hamstall not installed.')
    generic.leave()

try:
    file_version = prog_manage.get_file_version('file')
except KeyError:
    file_version = 1
while config.get_version('file_version') > file_version:
    if file_version == 1:
        print("Removing database config. This will corrupt which programs are installed!")
        print("If you are using hamstall, please contact hammy3502 for an upgrade process.")
        input("Press ENTER to continue...")
        try:
            config.vprint("Removing old database")
            os.remove(config.full("~/.hamstall/database"))
        except FileNotFoundError:
            pass
        config.vprint("Creating new database")
        config.create("~/.hamstall/database")
        prog_manage.create_db()
        config.vprint("Upgraded from hamstall file version 1 to 2.")
    elif file_version == 2:
        config.vprint("Database needs to have the branch key! Adding...")
        config.db["version"].update({"branch": "master"})
        config.db["version"]["file_version"] = 3
        config.vprint("Upgraded from hamstall file version 2 to 3.")
    elif file_version == 3:
        config.vprint("Database needs to have the shell key! Adding...")
        config.db["options"].update({"ShellFile": config.get_shell_file()})
        config.db["version"]["file_version"] = 4
        config.vprint("Upgraded from hamstall file version 3 to 4.")
    elif file_version == 4:
        config.vprint("file.py merged into config.py; deleting old file.py...")
        try:
            os.remove(config.full("~/.hamstall/file.py"))
            config.vprint("Deleted file.py")
        except FileNotFoundError:
            pass
            config.vprint("file.py not found, so not deleted!")
        config.vprint("Upgraded from hamstall file version 4 to 5.")
    try:
        file_version = prog_manage.get_file_version('file')
    except KeyError:
        file_version = 1
    config.write_db()

if prog_manage.get_file_version('prog') == 1:  # Online update broke between versions 1 and 2 of hamstall
    print('Please manually update hamstall! You can back up your directories in ~/.hamstall !')
    generic.leave()

if config.read_config("AutoInstall"):
    prog_manage.update(True)

if args.remove_lock:
    print("Lock doesn't exist, so not removed!")
    generic.leave()

elif args.install is not None:
    if not config.exists(args.install):
        print("File to install does not exist!")
        generic.leave()
    program_internal_name = config.name(args.install)  # Get the program name
    if program_internal_name in config.db["programs"]:  # Reinstall check
        reinstall = generic.get_input("Application already exists! Would you like to reinstall/overwrite? [r/o/N]",
                                      ["r", "o", "n"], "n")  # Ask to reinstall
        if reinstall == "r":
            prog_manage.uninstall(program_internal_name)
            prog_manage.install(args.install)  # Reinstall
        elif reinstall == "o":
            prog_manage.install(args.install, True)
        else:
            print("Reinstall cancelled.")
            generic.leave()
    else:
        prog_manage.install(args.install)  # No reinstall needed to be asked, install program

elif args.gitinstall is not None:
    if shutil.which("git") is None:
        print("git not installed! Please install it before using git install functionality!")
        generic.leave()
    else:
        program_internal_name = config.name(args.gitinstall)
        if program_internal_name in config.db["programs"]:
            reinstall = generic.get_input("Application already exists! Would you like to reinstall/overwrite? [r/o/N]",
                                          ["r", "o", "n"], "n")  # Ask to reinstall
            if reinstall == "r":
                prog_manage.uninstall(program_internal_name)
                prog_manage.gitinstall(args.gitinstall, program_internal_name)
            elif reinstall == "o":
                prog_manage.gitinstall(args.gitinstall, program_internal_name, True)
            else:
                print("Reinstall cancelled.")
                generic.leave()
        else:
            prog_manage.gitinstall(args.gitinstall, program_internal_name)


elif args.dirinstall is not None:
    if not(os.path.isdir(args.dirinstall)):
        print("Folder to install does not exist!")
        generic.leave()
    if args.dirinstall[len(args.dirinstall) - 1] != '/':
        print("Please make sure the directory ends with a / !")
        generic.leave()
    prog_int_name_temp = args.dirinstall[0:len(args.dirinstall)-1]
    program_internal_name = config.name(prog_int_name_temp + '.tar.gz')  # Add .tar.gz to make the original function work
    if program_internal_name in config.db["programs"]:
        reinstall = generic.get_input("Application already exists! Would you like to reinstall/overwrite? [r/o/N]", ["r", "o", "n"], "n")
        if reinstall == 'r':
            prog_manage.uninstall(program_internal_name)
            prog_manage.dirinstall(args.dirinstall, program_internal_name)
        elif reinstall == 'o':
            prog_manage.dirinstall(args.dirinstall, program_internal_name, True)
        else:
            print("Reinstall cancelled.")
            generic.leave()
    else:
        prog_manage.dirinstall(args.dirinstall, program_internal_name)

elif args.remove is not None:
    if args.remove in config.db["programs"]:  # If uninstall script exists
        prog_manage.uninstall(args.remove)  # Uninstall program
    else:
        print("Program does not exist!")  # Program doesn't exist
    generic.leave()

elif args.manage is not None:
    if args.manage in config.db["programs"]:
        prog_manage.manage(args.manage)
    else:
        print("Program does not exist!")
    generic.leave()

elif args.list:
    prog_manage.list_programs()  # List programs installed

elif args.first:
    prog_manage.first_time_setup(False)  # First time setup

elif args.erase:
    erase_sure = generic.get_input("Are you sure you would like to remove hamstall from your system? [y/N]",
                                   ['y', 'n'], 'n')
    if erase_sure == 'y':
        erase_really_sure = generic.get_input('Are you absolutely sure?' +
                                              'This will remove all programs installed with hamstall! [y/N]',
                                              ['y', 'n'], 'n')
        if erase_really_sure == 'y':
            prog_manage.erase()  # Remove hamstall from the system
        else:
            print('Erase cancelled.')
    else:
        print('Erase cancelled.')
    generic.leave()

elif args.verbose:  # Verbose toggle
    prog_manage.verbose_toggle()

elif args.update:
    prog_manage.update()

elif args.config:
    prog_manage.configure()

else:
    # About hamstall
    print("""
hamstall. A Python based package manager to manage archives.
Written by: hammy3502

hamstall Version: {user_version}
Internal Version Code: {file_version}.{prog_version}

For help, type "hamstall -h"
    """.format(user_version=config.get_version("version"), file_version=config.get_version("file_version"),
               prog_version=config.get_version("prog_internal_version")))

generic.leave()  # Catch all to make sure we unlock at the end of code execution

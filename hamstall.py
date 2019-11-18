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

def parse_args():
    """Argument Parsing.

    Parses arguments and runs hamstall startup.

    """
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
                                                "running)", action="store_true")
    group.add_argument('-c', '--config', help="Change hamstall options", action="store_true")
    args = parser.parse_args()  # Parser stuff

    status = prog_manage.hamstall_startup(start_fts=args.first, del_lock=args.remove_lock)

    if status == "Locked":
        print("Another instance of hamstall is probably running! Execution halted!")
        sys.exit(2)

    elif status == "Not installed":
        yn = generic.get_input('hamstall is not installed on your system. Would you like to install it? [Y/n]',
                                ['y', 'n', 'debug'], 'y')
        if yn == 'y':
            prog_manage.first_time_setup(False)
        elif yn == 'debug':
            prog_manage.first_time_setup(True)
        else:
            print('hamstall not installed.')
            config.unlock()
            sys.exit(0)
        generic.leave()
    
    elif status == "Root":
        print("Don't use sudo unless you want your programs installed for root and only root!")
    
    elif status == "Old":
        print("You are using an extremely outdated version of hamstall, please update manually!")
        sys.exit(1)

    if args.install is not None:
        status = prog_manage.pre_install(args.install)
        if status == "Bad file":
            print("The specified file does not exist!")
            generic.leave(1)
        elif status == "Application exists":
            reinstall = generic.get_input("Application already exists! Would you like to reinstall/overwrite? [r/o/N]",
                                      ["r", "o", "n"], "n")  # Ask to reinstall
            if reinstall == "r":
                prog_manage.pre_install(args.install, False)
            elif reinstall == "o":
                prog_manage.pre_install(args.install, True)
            else:
                print("Reinstall cancelled.")
                generic.leave()

    elif args.gitinstall is not None:
        status = prog_manage.pre_gitinstall(args.gitinstall)
        if status == "No git":
            print("git not installed! Please install it before using this feature!")
            generic.leave(1)
        elif status == "Bad URL":
            print("Invalid URL supplied; make sure it ends in .git!")
            generic.leave(1)
        elif status == "Application exists":
            reinstall = generic.get_input("Application already exists! Would you like to reinstall/overwrite? [r/o/N]",
                                            ["r", "o", "n"], "n")  # Ask to reinstall
            if reinstall == "r":
                prog_manage.pre_gitinstall(args.gitinstall, False)
            elif reinstall == "o":
                prog_manage.pre_gitinstall(args.gitinstall, True)
            else:
                print("Reinstall cancelled.")
                generic.leave()


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
        print("""
hamstall. A Python based package manager to manage archives.
Written by: hammy3502

hamstall Version: {user_version}
Internal Version Code: {file_version}.{prog_version}

For help, type "hamstall -h"
        """.format(user_version=config.get_version("version"), file_version=config.get_version("file_version"),
                prog_version=config.get_version("prog_internal_version")))

    generic.leave()  # Catch all to make sure we unlock at the end of code execution


if __name__ == "__main__":
    parse_args()
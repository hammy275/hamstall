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
from subprocess import call


def branch_wizard():
    """Switch Branches."""
    print("""\n\n
####WARNING####
WARNING: You are changing branches of hamstall!
Changing from master to beta means you may receive updates that contain bugs, some extremely severe!
Changing from beta to master means you will either HAVE ALL OF YOUR HAMSTALL PROGRAMS DELETED
or you will have to STAY ON THE UPDATE YOU CURRENTLY HAVE UNTIL MASTER CATCHES UP!

Switching branches will trigger an immediate update of hamstall!
###############

Select a branch:
m - Master branch. Less bugs, more stable, wait for updates.
b - Beta branch. More bugs, less stable, updates asap.
E - Exit branch wizard and don't change branches.
    """)
    ans = generic.get_input("[m/b/E] ", ['m', 'b', 'e'], 'e')
    if ans == 'e':
        print("Not changing branches!")
        return
    elif ans == 'm' and config.db["version"]["branch"] == "master":
        print("Already on the master branch, not switching!")
        return
    elif ans == 'b' and config.db["version"]["branch"] == "beta":
        print("Already on the beta branch, not switching!")
        return
    else:
        check = input('Type "YES" (without the quotes) to confirm the branch switch! ')
        if check != "YES":
            print("Cancelling branch switch.")
            return
        else:
            if ans == "m":
                branch = "master"
                should_reset = generic.get_input("Would you like to reset hamstall or wait for master to update past where you are? [r/W]",
                ["r", "w"], "w")
            elif ans == "b":
                branch = "beta"
                should_reset = "w"
            status = prog_manage.change_branch(branch, should_reset == "r")
            if status == "Success":
                print("Successfully switched to the beta branch!")
                return
            elif status == "Bad branch":
                print("Invalid branch specified!")
                return
            elif status == "Reset":
                print("Successfully switched to the master branch and reset hamstall!")
                print("Please run hamstall again to finish the downgrade process!")
                return
            elif status == "Waiting":
                print("Successfully switched to the master branch!")
                print("When the master branch is a newer version than the beta one, the next update will bring you up to master.")
                return


def configure():
    """Change hamstall Options."""
    while True:
        print("""
Select an option:
au - Enable/disable the ability to install updates when hamstall is run. Currently {au}.
v - Enable/disable verbose mode, showing more output when hamstall commands are run. Currently {v}.
b - Swap branches in hamstall. Allows you to get updates sooner at the cost of possible bugs. Current branch: {b}.
e - Exit hamstall
        """.format(
            au=generic.endi(config.read_config("AutoInstall")), v=generic.endi(config.read_config("Verbose")),
            b=config.db["version"]["branch"]
        ))
        option = generic.get_input("[au/v/b/E] ", ['au', 'v', 'b', 'e'], 'e')
        if option == 'au':
            if not prog_manage.can_update:
                print("requests isn't installed, so AutoInstall cannot be enabled!")
            else:
                key = "AutoInstall"
        elif option == 'v':
            key = "Verbose"
        elif option == 'b':
            prog_manage.branch_wizard()
            key = None
        elif option == 'e':
            return
        if key is not None:
            new_value = config.change_config(key, "flip")
            print("\n{key} mode {value}!".format(key=key, value=generic.endi(new_value)))


def pathify(program):
    """Pathify CLI Function.

    Args:
        program (str): Name of program to PATHify

    """
    status = prog_manage.pathify(program)
    if status == "Complete":
        print("Program added to PATH!")


def binlink(program):
    """Binlink CLI Function.

    Args:
        program (str): Name of program to create binlinks for

    """
    yn = 'y'
    while yn != 'n':
        files = os.listdir(config.full('~/.hamstall/bin/' + program + '/'))
        print(' '.join(files))
        file_chosen = 'Cool fact. This line was originally written on line 163.'
        while file_chosen not in files:
            file_chosen = input('Please enter a file listed above. If you would like to cancel, type exit: ')
            if file_chosen == "exit":
                return
        prog_manage.add_binlink(file_chosen, program)
        yn = generic.get_input('Would you like to continue adding files to be run directly? [y/N]', ['y', 'n'], 'n')


def desktop_wizard(program):
    """Desktop Creation Wizard.

    Args:
        program (str): Program to create .desktop file of

    """
    files = os.listdir(config.full('~/.hamstall/bin/' + program + '/'))
    print(' '.join(files))
    program_file = '/Placeholder/'
    config.vprint("Getting user inputs")
    while program_file not in files:
        program_file = input('Please enter a file listed above. If you would like to cancel, type exit: ')
        if program_file == "exit":
            return
    comment = "/"
    while not comment.replace(" ", "").isalnum() and comment != "":
        comment = input("Please input a comment for the application: ")
    icon = ";"
    while not icon.replace("-", "").replace("_", "").replace("/", "").isalnum() and icon != "":
        icon = input("Enter the path to an icon, the name of the icon, or press ENTER for no icon! ")
    terminal = generic.get_input("Should this program launch a terminal to run it in? [y/N]", ['y', 'n'], 'n')
    if terminal.lower() == 'y':
        should_terminal = "True"
    else:
        should_terminal = "False"
    name = "/"
    while not name.replace(" ", "").isalnum() and name != "":
        name = input("Please enter a name: ")
    if name == "":
        name = program
    ans = " "
    chosen_categories = []
    categories = ["audio", "video", "development", "education", "game", "graphics", "network", "office",
                    "science",
                    "settings", "system", "utility", "end"]
    while ans.lower() != "end":
        print("Please enter categories, one at a time, from the list of .desktop categories below (defaults to "
                "Utility). Type \"end\" to end category selection. \n")
        print(", ".join(categories))
        ans = generic.get_input("", categories, "Utility")
        if ans.capitalize() in chosen_categories or ans == "end":
            pass
        else:
            ans = ans.capitalize()
            chosen_categories.append(ans)
    status = prog_manage.create_desktop(program, name, program_file, comment, should_terminal,
                                        chosen_categories, icon)
    if status == "Created":
        print(".desktop file successfully created!")
    elif status == "Already exists":
        print(".desktop file already exists!")


def install_wrap_up(program):
    """End of Install.

    Runs at the end of an install to ask users about different "shortcut" creations/PATH creation

    Args:
        program (str): Name of program

    """
    yn = generic.get_input('Would you like to add the program to your PATH? [Y/n]', ['y', 'n'], 'y')
    if yn == 'y':
        pathify(program)
    yn = generic.get_input('Would you like to create a binlink? [y/N]', ['y', 'n'], 'n')
    if yn == 'y':
        binlink(program)
    yn = generic.get_input('Would you like to create a desktop file? [y/N]', ['y', 'n'], 'n')
    if yn == 'y':
        desktop_wizard(program)
    print("Installation complete!")


def manage(program):
    """Manage Installed Program.

    Args:
        program (str): Internal name of program to manage

    """
    if not program in config.db["programs"]:
        print("{} not installed!".format(program))
        sys.exit(1)
    while True:
        print("Enter an option to manage " + program + ":")
        print("b - Create binlinks for " + program)
        print("p - Add " + program + " to PATH")
        print("n - Rename " + program)
        print("u - Uninstall " + program)
        print("r - Remove all binlinks + PATHs for " + program)
        print("d - Create a .desktop file for " + program)
        print("rd - Remove a .desktop file for " + program)
        print("s - Launch a shell inside " + program + "'s directory")
        print("E - Exit program management")
        option = generic.get_input("[b/p/n/u/r/d/rd/s/E]", ['b', 'p', 'n', 'u', 'r', 'd', 'rd', 's', 'e'], 'e')
        if option == 'b':
            binlink(program)
        elif option == 'p':
            pathify(program)
        elif option == 'n':
            new_name = "!"
            while not new_name.replace("_", "").replace("-", "").isalnum():
                new_name = input("Please enter the name you would like to change this program to: ")
                if not new_name.replace("_", "").replace("-", "").isalnum():
                    print("Alphanumeric characters, dashes, and underscores only, please!")
            program = prog_manage.rename(program, new_name)
        elif option == 'u':
            prog_manage.uninstall(program)
            break
        elif option == 'r':
            status = prog_manage.remove_paths_and_binlinks(program)
            if status == "Complete":
                print("Removal of PATHs and binlinks complete!")
        elif option == 'd':
            desktop_wizard(program)
        elif option == 'rd':
            print("Desktops: ")
            for d in config.db["programs"][program]["desktops"]:
                print(d)
            inp = "/ choose desktop"
            while not (inp in config.db["programs"][program]["desktops"]) and inp != "exit":
                inp = input("Please enter the desktop you would like to remove or type \"exit\" to exit: ")
            prog_manage.remove_desktop(program, inp)
        elif option == 's':
            print("When you exit the shell, you will be returned to here.")
            os.chdir(config.full("~/.hamstall/bin/" + program + "/"))
            if config.get_shell_file() == ".zshrc":
                call(["/bin/zsh"])
            else:
                call(["/bin/bash"])
        elif option == 'e':
            break


def fts_status(status):
    if status == "Success":
        print('First time setup complete!')
        print('Please run the command "source ~/{}" or restart your terminal.'.format(config.read_config("ShellFile")))
        print('Afterwards, you may begin using hamstall with the hamstall command!')
        sys.exit(0)

    elif status == "Already installed":
        print("hamstall is already installed on your system! Cancelling installation.")
        sys.exit(1)

    elif status == "Bad copy":
        print("A file was attempting to be copied, but was deleted during the process! Installation halted.")
        sys.exit(1)
    
    else:
        return

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

    fts_status(status)

    if status == "Locked":
        print("Another instance of hamstall is probably running! Execution halted!")
        sys.exit(1)

    elif status == "Unlocked":
        print("hamstall unlocked!")
        sys.exit(0)

    elif status == "Not installed":
        yn = generic.get_input('hamstall is not installed on your system. Would you like to install it? [Y/n]',
                                ['y', 'n', 'debug'], 'y')
        if yn == 'y':
            prog_manage.first_time_setup(False)
            fts_status(status)
        elif yn == 'debug':
            prog_manage.first_time_setup(True)
            fts_status(status)
        else:
            print('hamstall not installed.')
            config.unlock()
    
    elif status == "Root":
        print("Don't use sudo unless you want your programs installed for root and only root!")
    
    elif status == "Old":
        print("You are using an extremely outdated version of hamstall, please update manually!")
        sys.exit(1)
    
    elif status == "Old upgrade":
        print("You are upgrading from a VERY old version of hamstall.")
        print("Press ENTER to continue and wipe your database in the upgrade process!")
        input("")
        prog_manage.hamstall_startup(start_fts=args.first, del_lock=args.remove_lock, old_upgrade=True)

    if args.install is not None:
        status = prog_manage.pre_install(args.install)
        if status == "Bad file":
            print("The specified file does not exist!")
            sys.exit(1)
        elif status == "Application exists":
            reinstall = generic.get_input("Application already exists! Would you like to reinstall/overwrite? [r/o/N]",
                                      ["r", "o", "n"], "n")  # Ask to reinstall
            if reinstall == "r":
                status = prog_manage.pre_install(args.install, False)
            elif reinstall == "o":
                status = prog_manage.pre_install(args.install, True)
            else:
                print("Reinstall cancelled.")
        if status == "Installed":
            install_wrap_up(config.name(args.install))
        elif status.startswith("No"):
            print("{} needs to be installed! Installation halted.".format(status[3:]))
        elif status == "No rsync":
            print("rsync not installed! Please install it!")
            sys.exit(1)
        elif status == "Bad name":
            print("Archive name cannot contain a space or #!")
            sys.exit(1)
        elif status == "Error":
            print("Error occured while extracting archive!")
            sys.exit(1)

    elif args.gitinstall is not None:
        status = prog_manage.pre_gitinstall(args.gitinstall)
        if status == "No git":
            print("git not installed! Please install it before using this feature!")
            sys.exit(1)
        elif status == "Bad URL":
            print("Invalid URL supplied; make sure it ends in .git!")
            sys.exit(1)
        elif status == "Application exists":
            reinstall = generic.get_input("Application already exists! Would you like to reinstall/overwrite? [r/o/N]",
                                            ["r", "o", "n"], "n")  # Ask to reinstall
            if reinstall == "r":
                status = prog_manage.pre_gitinstall(args.gitinstall, False)
            elif reinstall == "o":
                status = prog_manage.pre_gitinstall(args.gitinstall, True)
            else:
                print("Reinstall cancelled.")
        if status == "Installed":
            install_wrap_up(config.name(args.gitinstall))
        elif status == "No rsync":
            print("rsync not installed! Please install it!")
            sys.exit(1)
        elif status == "Error":
            print("An error occured while attempting to git clone!")
            sys.exit(1)


    elif args.dirinstall is not None:
        status = prog_manage.pre_dirinstall(args.dirinstall)
        if status == "Bad folder":
            print("Please specify a valid directory path that ends in a \"/\"!")
            sys.exit(1)
        elif status == "Application exists":
            reinstall = generic.get_input("Application already exists! Would you like to reinstall/overwrite? [r/o/N]", ["r", "o", "n"], "n")
            if reinstall == 'r':
                status = prog_manage.pre_dirinstall(args.dirinstall, False)
            elif reinstall == 'o':
                status = prog_manage.pre_dirinstall(args.dirinstall, True)
            else:
                print("Reinstall cancelled.")
        if status == "Installed":
            install_wrap_up(config.name(args.dirinstall))
        elif status == "No rsync":
            print("rsync not installed! Please install it!")
            sys.exit(1)

    elif args.remove is not None:
        status = prog_manage.uninstall(args.remove)
        if status == "Success":
            print("Successfully uninstalled {}!".format(args.remove))
        elif status == "Not installed":
            print("{} isn't an installed program!".format(args.remove))

    elif args.manage is not None:
        manage(args.manage)

    elif args.list:
        programs = prog_manage.list_programs()
        if programs == []:
            print("No programs installed!")
        else:
            for p in programs:
                print(p)

    elif args.erase:
        erase_sure = generic.get_input("Are you sure you would like to remove hamstall from your system? [y/N]",
                                    ['y', 'n'], 'n')
        if erase_sure == 'y':
            erase_really_sure = generic.get_input('Are you absolutely sure?' +
                                                'This will remove all programs installed with hamstall! [y/N]',
                                                ['y', 'n'], 'n')
            if erase_really_sure == 'y':
                status = prog_manage.erase()
                if status == "Not installed":
                    print("hamstall isn't installed, so not removed!")
                elif status == "Erased":
                    print("hamstall has been removed!")
            else:
                print('Erase cancelled.')
        else:
            print('Erase cancelled.')

    elif args.verbose:
        status = prog_manage.verbose_toggle()
        print("Verbose mode changed to: {}".format(status))

    elif args.update:
        status = prog_manage.update()
        if status == "No requests":
            print("requests isn't installed, please install it!")
        elif status == "Newer version":
            print("The installed version is newer than the one found online!")
        elif status == "No update":
            print("No update was found!")
        elif status == "Updated":
            print("hamstall successfully updated!")
        elif status == "Failed":
            print("hamstall update failed! hamstall is most likely missing its files. Please manually re-install it!")
            sys.exit(1)
        elif status == "No requests":
            print("requests isn't installed, please install it before updating!")
            sys.exit(1)

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

    config.unlock()
    sys.exit(0)


if __name__ == "__main__":
    parse_args()
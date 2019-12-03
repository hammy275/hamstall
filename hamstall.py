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
import config
import generic
import prog_manage
from subprocess import call

mode = config.read_config("Mode")

if mode == "gui":
    try:
        import tkinter
        del tkinter
    except ImportError:
        mode = "cli"
        generic.pprint("Tkinter not installed! Defaulting to cli mode...")
    try:
        import PySimpleGUI as sg
    except ImportError:
        mode = "cli"
        generic.pprint("PySimpleGUI not installed! Defaulting to cli mode...")

def gui_loop():
    to_disable = ["install", "install_browse", "dirinstall", "dirinstall_browse", "gitinstall",
    "gitinstall_browse", "remove", "manage"]
    layout = [
        [sg.Text("Select an option:")],
        [sg.Radio("Install: ", "Todo", default=True, enable_events=True, key="should_install"), sg.InputText(key="install"), sg.FileBrowse(key="install_browse")],
        [sg.Radio("Install Directory: ", "Todo", enable_events=True, key="should_dirinstall"), sg.InputText(key="dirinstall", disabled=True), sg.FolderBrowse(disabled=True, key="dirinstall_browse")],
        [sg.Radio("Gitinstall: ", "Todo", enable_events=True, key="should_gitinstall"), sg.InputText(key="gitinstall", disabled=True), sg.FileBrowse(disabled=True, key="gitinstall_browse")],
        [sg.Radio("Remove: ", "Todo", enable_events=True, key="should_remove"), sg.Combo(prog_manage.list_programs(), key="remove", disabled=True)],
        [sg.Radio("Erase hamstall", "Todo", enable_events=True, key="should_erase")],
        [sg.Radio("Update hamstall", "Todo", enable_events=True, key="should_update")],
        [sg.Radio("Manage: ", "Todo", enable_events=True, key="should_manage"), sg.Combo(prog_manage.list_programs(), key="manage", disabled=True)],
        [sg.Radio("Configure hamstall", "Todo", enable_events=True, key="should_configure")],
        [sg.Radio("Update programs installed with git", "Todo", enable_events=True, key="should_update_git")],
        [sg.Button("Go"), sg.Button("Exit")],
        [sg.ProgressBar(100, key="bar")]
    ]
    window = sg.Window('hamstall', layout=layout)
    while True:
        event, values = window.Read()
        config.install_bar = window.Element("bar")
        config.install_bar.UpdateBar(0)
        if event in (None, "Exit"):
            sys.exit(0)
        elif event == "Go":
            if values["should_install"]:
                status = parse_args(["--install", values["install"]])
            elif values["should_dirinstall"]:
                status = parse_args(["--dirinstall", values["dirinstall"]])
            elif values["should_gitinstall"]:
                status = parse_args(["--gitinstall", values["gitinstall"]])
            elif values["should_remove"]:
                status = parse_args(["--remove", values["remove"]])
            elif values["should_erase"]:
                status = parse_args(["--erase"])
            elif values["should_update"]:
                status = parse_args(["--update"])
            elif values["should_manage"]:
                status = parse_args(["--manage", values["manage"]])
            elif values["should_configure"]:
                status = parse_args(["--config"])
            elif values["should_update_git"]:
                status = parse_args(["--update-gits"])
            if status == "Locked":
                generic.pprint("hamstall is locked! You can unlock it, but if another instance of hamstall is running, things will break!")
                ul = generic.get_input("Would you like to unlock hamstall? Only do this if no other instances of hamstall are running!", ['y', 'n'], 'n',
                ["Yes", "No"])
                if ul == 'y':
                    parse_args(["--remove-lock"])
                    generic.pprint("hamstall unlocked! Please specify what you would like to do again!")
                else:
                    sys.exit(1)
            else:
                config.install_bar.UpdateBar(100)
        else:
            for o in to_disable:
                window.Element(o).Update(disabled=True)
            if event == "should_install":
                window.Element("install").Update(disabled=False)
                window.Element("install_browse").Update(disabled=False)
            elif event == "should_dirinstall":
                window.Element("dirinstall").Update(disabled=False)
                window.Element("dirinstall_browse").Update(disabled=False)
            elif event == "should_gitinstall":
                window.Element("gitinstall").Update(disabled=False)
                window.Element("gitinstall_browse").Update(disabled=False)
            elif event == "should_remove":
                window.Element("remove").Update(disabled=False)
            elif event == "should_manage":
                window.Element("manage").Update(disabled=False)


def git_wizard(program):
    """Extra management for a program installed through git.

    Args:
        program (str): Name of program to manage

    """
    msg = """
Select an option:
u - Update program from currently configured branch
b - Reset repository and change branches (WARNING: This will remove everything inside this program's directory!)
e - Exit Git Wizard.
[u/b/e]"""
    ans = generic.get_input(msg, ['u', 'b', 'e'], 'e', ["Update", "Change branch", "Exit"])
    if ans == 'u':
        status = prog_manage.update_git_program(program)
        if status == "Success":
            generic.pprint("Update successful!")
        elif status == "No git":
            generic.pprint("Git isn't installed, please install it!")
        elif status == "Error updating":
            generic.pprint("An error occured while attempting to update {}.".format(program))
    elif ans == 'b':
        branch = generic.ask("Enter branch to switch to: ")
        status = prog_manage.change_git_branch(program, branch)
        if status == "Success":
            generic.pprint("Branch change successful!")
        elif status == "No git":
            generic.pprint("Git isn't installed, please install it!")
        elif status == "Error changing":
            generic.pprint("An error occured while attempting to change the branches of {}.".format(program))
    elif ans == 'e':
        return



def branch_wizard():
    """Switch Branches."""
    msg = """\n\n
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
[m/b/E]"""
    ans = generic.get_input(msg, ['m', 'b', 'e'], 'e', ["Master", "Beta", "Exit"])
    if ans == 'e':
        generic.pprint("Not changing branches!")
        return
    elif ans == 'm' and config.db["version"]["branch"] == "master":
        generic.pprint("Already on the master branch, not switching!")
        return
    elif ans == 'b' and config.db["version"]["branch"] == "beta":
        generic.pprint("Already on the beta branch, not switching!")
        return
    else:
        check = generic.get_input('Type "YES" (without the quotes) to confirm the branch switch! ',
        ["YES", "NO"], "NO")
        if check != "YES":
            generic.pprint("Cancelling branch switch.")
            return
        else:
            if ans == "m":
                branch = "master"
                should_reset = generic.get_input("Would you like to reset hamstall or wait for master to update past where you are? [r/W]",
                ["r", "w"], "w", ["Reset", "Wait"])
            elif ans == "b":
                branch = "beta"
                should_reset = "w"
            status = prog_manage.change_branch(branch, should_reset == "r")
            if status == "Success":
                generic.pprint("Successfully switched to the beta branch!")
                return
            elif status == "Bad branch":
                generic.pprint("Invalid branch specified!")
                return
            elif status == "Reset":
                generic.pprint("Successfully switched to the master branch and reset hamstall!")
                generic.pprint("Please run hamstall again to finish the downgrade process!")
                return
            elif status == "Waiting":
                generic.pprint("Successfully switched to the master branch!")
                generic.pprint("When the master branch is a newer version than the beta one, the next update will bring you up to master.")
                return


def configure():
    """Change hamstall Options."""
    while True:
        msg = """
Select an option:
au - Enable/disable the ability to install updates when hamstall is run. Currently {au}.
v - Enable/disable verbose mode, showing more output when hamstall commands are run. Currently {v}.
b - Swap branches in hamstall. Allows you to get updates sooner at the cost of possible bugs. Current branch: {b}.
m - Whether or not to use the GUI for hamstall. Currently {gui}.
e - Exit hamstall
[au/v/b/m/E]""".format(
            au=generic.endi(config.read_config("AutoInstall")), v=generic.endi(config.read_config("Verbose")),
            b=config.db["version"]["branch"], gui=generic.endi(config.read_config("Mode") == "gui")
        )
        option = generic.get_input(msg, ['au', 'v', 'b', 'm', 'e'], 'e', 
        ["Autoupdate", "Verbosity", "Change Branches", "Change Interaction Mode", "Exit"])
        if option == 'au':
            if not prog_manage.can_update:
                generic.pprint("requests isn't installed, so AutoInstall cannot be enabled!")
            else:
                key = "AutoInstall"
        elif option == 'v':
            key = "Verbose"
        elif option == 'b':
            branch_wizard()
            key = None
        elif option == 'm':
            if config.read_config("Mode") == "cli":
                config.change_config("Mode", "change", "gui")
                generic.pprint("Changed to GUI mode!")
            else:
                config.change_config("Mode", "change", "cli")
                generic.pprint("Changed to CLI mode!")
            key = None
        elif option == 'e':
            return
        if key is not None:
            new_value = config.change_config(key, "flip")
            generic.pprint("\n{key} mode {value}!".format(key=key, value=generic.endi(new_value)))


def pathify(program):
    """Pathify CLI Function.

    Args:
        program (str): Name of program to PATHify

    """
    status = prog_manage.pathify(program)
    if status == "Complete":
        generic.pprint("Program added to PATH!")


def binlink(program):
    """Binlink CLI Function.

    Args:
        program (str): Name of program to create binlinks for

    """
    yn = 'y'
    while yn != 'n':
        files = os.listdir(config.full('~/.hamstall/bin/' + program + '/'))
        generic.pprint(' '.join(files))
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
    generic.pprint(' '.join(files))
    program_file = '/Placeholder/'
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
        generic.pprint("Please enter categories, one at a time, from the list of .desktop categories below (defaults to "
                "Utility). Type \"end\" to end category selection. \n")
        generic.pprint(", ".join(categories))
        ans = generic.get_input("", categories, "Utility")
        if ans.capitalize() in chosen_categories or ans == "end":
            pass
        else:
            ans = ans.capitalize()
            chosen_categories.append(ans)
    status = prog_manage.create_desktop(program, name, program_file, comment, should_terminal,
                                        chosen_categories, icon)
    if status == "Created":
        generic.pprint(".desktop file successfully created!")
    elif status == "Already exists":
        generic.pprint(".desktop file already exists!")


def install_wrap_up(program):
    """End of Install.

    Runs at the end of an install to ask users about different "shortcut" creations/PATH creation

    Args:
        program (str): Name of program

    """
    yn = generic.get_input('Would you like to add the program to your PATH? [Y/n]', ['y', 'n'], 'y', ["Yes", "No"])
    if yn == 'y':
        pathify(program)
    yn = generic.get_input('Would you like to create a binlink? [y/N]', ['y', 'n'], 'n', ["Yes", "No"])
    if yn == 'y':
        binlink(program)
    yn = generic.get_input('Would you like to create a desktop file? [y/N]', ['y', 'n'], 'n', ["Yes", "No"])
    if yn == 'y':
        desktop_wizard(program)
    generic.pprint("Installation complete!")


def manage(program):
    """Manage Installed Program.

    Args:
        program (str): Internal name of program to manage

    """
    if not program in config.db["programs"]:
        generic.pprint("{} not installed!".format(program))
        return
    options = ['b', 'p', 'n', 'u', 'r', 'd', 'rd', 's', 'e']
    option_strings = ["Create binlinks", "Add to PATH", "Rename", "Uninstall", "Remove all binlinks and PATHs",
        "Create a .desktop file", "Remove a .desktop file", "Launch a shell inside the program's directory",
        "Exit"]
    if config.db["programs"][program]["git_installed"]:
        git_msg = "\ng - Manage git-related settings for {program}"
        g_msg = "g/"
        options.append("g")
        option_strings.append("Manage git settings")
    else:
        git_msg = ""
        g_msg = ""
    while True:
        msg = """
Enter an option to manage program:
b - Create binlinks for {program}
p - Add {program} to PATH
n - Rename {program}
u - Uninstall {program}
r - Remove all binlinks + PATHs for {program}
d - Create a .desktop file for {program}
rd - Remove a .desktop file for {program}
s - Launch a shell inside {program}'s directory{git}
E - Exit program management
[b/p/n/u/r/d/rd/s/{g}E]""".format(program=program, git=git_msg, g=g_msg)
        option = generic.get_input(msg, options, 'e', option_strings)
        if option == 'b':
            binlink(program)
        elif option == 'p':
            pathify(program)
        elif option == 'n':
            new_name = "!"
            while not new_name.replace("_", "").replace("-", "").isalnum():
                new_name = input("Please enter the name you would like to change this program to: ")
                if not new_name.replace("_", "").replace("-", "").isalnum():
                    generic.pprint("Alphanumeric characters, dashes, and underscores only, please!")
            program = prog_manage.rename(program, new_name)
        elif option == 'u':
            prog_manage.uninstall(program)
            break
        elif option == 'r':
            status = prog_manage.remove_paths_and_binlinks(program)
            if status == "Complete":
                generic.pprint("Removal of PATHs and binlinks complete!")
        elif option == 'd':
            desktop_wizard(program)
        elif option == 'rd':
            generic.pprint("Desktops: ")
            for d in config.db["programs"][program]["desktops"]:
                generic.pprint(d)
            inp = "/ choose desktop"
            while not (inp in config.db["programs"][program]["desktops"]) and inp != "exit":
                inp = input("Please enter the desktop you would like to remove or type \"exit\" to exit: ")
            prog_manage.remove_desktop(program, inp)
        elif option == 's':
            generic.pprint("When you exit the shell, you will be returned to here.")
            os.chdir(config.full("~/.hamstall/bin/" + program + "/"))
            if config.get_shell_file() == ".zshrc":
                call(["/bin/zsh"])
            else:
                call(["/bin/bash"])
        elif option == 'g':
            git_wizard(program)
        elif option == 'e':
            break


def fts_status(status):
    """Process First Time Setup Status.

    Args:
        status (str): Status string from first time setup

    Returns:
        int: Exit code to exit hamstall with

    """
    if status == "Success":
        generic.pprint('First time setup complete!')
        generic.pprint('Please run the command "source ~/{}" or restart your terminal.'.format(config.read_config("ShellFile")))
        generic.pprint('Afterwards, you may begin using hamstall with the hamstall command!')
        return 0

    elif status == "Already installed":
        generic.pprint("hamstall is already installed on your system! Cancelling installation.")
        return 1

    elif status == "Bad copy":
        generic.pprint("A file was attempting to be copied, but was deleted during the process! Installation halted.")
        return 1
    
    else:
        return

def parse_args(args=None):
    """Argument Parsing.

    Parses arguments and runs hamstall startup.

    """
    exit_code = 0
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
    group.add_argument('-q', '--update-gits', help="Update programs installed through git", action="store_true")
    if args is None:
        args = parser.parse_args()  # Parser stuff
    else:
        args = parser.parse_args(args)

    status = prog_manage.hamstall_startup(start_fts=args.first, del_lock=args.remove_lock)

    fts_status(status)

    if status == "Locked":
        if config.mode == "cli":
            generic.pprint("Another instance of hamstall is probably running! Execution halted!")
            sys.exit(1)
        elif config.mode == "gui":
            return "Locked"

    elif status == "Unlocked":
        generic.pprint("hamstall unlocked!")
        sys.exit()

    elif status == "Not installed":
        yn = generic.get_input('hamstall is not installed on your system. Would you like to install it? [Y/n]',
                                ['y', 'n', 'debug'], 'y')
        if yn == 'y':
            prog_manage.first_time_setup(False)
            exit_code = fts_status(status)
        elif yn == 'debug':
            prog_manage.first_time_setup(True)
            exit_code = fts_status(status)
        else:
            generic.pprint('hamstall not installed.')
            config.unlock()
    
    elif status == "Root":
        generic.pprint("Don't use sudo unless you want your programs installed for root and only root!")
    
    elif status == "Old":
        generic.pprint("You are using an extremely outdated version of hamstall, please update manually!")
        sys.exit(1)
    
    elif status == "Old upgrade":
        generic.pprint("You are upgrading from a VERY old version of hamstall.")
        generic.pprint("Press ENTER to continue and wipe your database in the upgrade process!")
        input("")
        prog_manage.hamstall_startup(start_fts=args.first, del_lock=args.remove_lock, old_upgrade=True)

    if args.install is not None:
        status = prog_manage.pre_install(args.install)
        if status == "Bad file":
            generic.pprint("The specified file does not exist!")
            exit_code = 1
        elif status == "Application exists":
            reinstall = generic.get_input("Application already exists! Would you like to reinstall/overwrite? [r/o/N]",
                                      ["r", "o", "n"], "n", ["Reinstall", "Overwrite", "Cancel"])  # Ask to reinstall
            if reinstall == "r":
                status = prog_manage.pre_install(args.install, False, True)
            elif reinstall == "o":
                status = prog_manage.pre_install(args.install, True, True)
            else:
                generic.pprint("Reinstall cancelled.")
        elif status == "Installed":
            install_wrap_up(config.name(args.install))
        elif status.startswith("No"):
            generic.pprint("{} needs to be installed! Installation halted.".format(status[3:]))
        elif status == "No rsync":
            generic.pprint("rsync not installed! Please install it!")
            exit_code = 1
        elif status == "Bad name":
            generic.pprint("Archive name cannot contain a space or #!")
            exit_code = 1
        elif status == "Error":
            generic.pprint("Error occured while extracting archive!")
            exit_code = 1

    elif args.gitinstall is not None:
        status = prog_manage.pre_gitinstall(args.gitinstall)
        if status == "No git":
            generic.pprint("git not installed! Please install it before using this feature!")
            exit_code = 1
        elif status == "Bad URL":
            generic.pprint("Invalid URL supplied; make sure it ends in .git!")
            exit_code = 1
        elif status == "Application exists":
            reinstall = generic.get_input("Application already exists! Would you like to reinstall/overwrite? [r/o/N]",
                                            ["r", "o", "n"], "n", ["Reinstall", "Overwrite", "Cancel"])  # Ask to reinstall
            if reinstall == "r":
                status = prog_manage.pre_gitinstall(args.gitinstall, False, True)
            elif reinstall == "o":
                status = prog_manage.pre_gitinstall(args.gitinstall, True, True)
            else:
                generic.pprint("Reinstall cancelled.")
        if status == "Installed":
            install_wrap_up(config.name(args.gitinstall))
        elif status == "No rsync":
            generic.pprint("rsync not installed! Please install it!")
            exit_code = 1
        elif status == "Error":
            generic.pprint("An error occured while attempting to git clone!")
            exit_code = 1


    elif args.dirinstall is not None:
        status = prog_manage.pre_dirinstall(args.dirinstall)
        if status == "Bad folder":
            generic.pprint("Please specify a valid directory path that ends in a \"/\"!")
            exit_code = 1
        elif status == "Application exists":
            reinstall = generic.get_input("Application already exists! Would you like to reinstall/overwrite? [r/o/N]", ["r", "o", "n"], "n", 
            ["Reinstall", "Overwrite", "Cancel"])
            if reinstall == 'r':
                status = prog_manage.pre_dirinstall(args.dirinstall, False, True)
            elif reinstall == 'o':
                status = prog_manage.pre_dirinstall(args.dirinstall, True, True)
            else:
                generic.pprint("Reinstall cancelled.")
        if status == "Installed":
            install_wrap_up(config.dirname(args.dirinstall))
        elif status == "No rsync":
            generic.pprint("rsync not installed! Please install it!")
            exit_code = 1

    elif args.remove is not None:
        status = prog_manage.uninstall(args.remove)
        if status == "Success":
            generic.pprint("Successfully uninstalled {}!".format(args.remove))
        elif status == "Not installed":
            generic.pprint("{} isn't an installed program!".format(args.remove))

    elif args.manage is not None:
        manage(args.manage)

    elif args.list:
        programs = prog_manage.list_programs()
        if programs == []:
            generic.pprint("No programs installed!")
        else:
            for p in programs:
                generic.pprint(p)

    elif args.erase:
        erase_sure = generic.get_input("Are you sure you would like to remove hamstall from your system? [y/N]",
                                    ['y', 'n'], 'n', ["Yes", "No"])
        if erase_sure == 'y':
            erase_really_sure = generic.get_input('Are you absolutely sure?' +
                                                'This will remove all programs installed with hamstall! [y/N]',
                                                ['y', 'n'], 'n', ["Yes", "No"])
            if erase_really_sure == 'y':
                status = prog_manage.erase()
                if status == "Not installed":
                    generic.pprint("hamstall isn't installed, so not removed!")
                elif status == "Erased":
                    generic.pprint("hamstall has been removed!")
            else:
                generic.pprint('Erase cancelled.')
        else:
            generic.pprint('Erase cancelled.')

    elif args.verbose:
        status = prog_manage.verbose_toggle()
        generic.pprint("Verbose mode {}".format(status))

    elif args.update:
        status = prog_manage.update()
        if status == "No requests":
            generic.pprint("requests isn't installed, please install it!")
        elif status == "Newer version":
            generic.pprint("The installed version is newer than the one found online!")
        elif status == "No update":
            generic.pprint("No update was found!")
        elif status == "Updated":
            generic.pprint("hamstall successfully updated!")
        elif status == "Failed":
            generic.pprint("hamstall update failed! hamstall is most likely missing its files. Please manually re-install it!")
            exit_code = 1
        elif status == "No requests":
            generic.pprint("requests isn't installed, please install it before updating!")
            exit_code = 1

    elif args.config:
        configure()
    
    elif args.update_gits:
        status = prog_manage.update_gits()
        if status == "No git":
            generic.pprint("git isn't installed, please install it!")
            exit_code = 1
        else:
            msg = ""
            exit_code = 0
            for p in status.keys():
                if status[p] == "Success":
                    msg += p + " updated successfully!\n"
                elif status[p] == "Error updating":
                    msg += p + " did not update successfully!\n"
                    exit_code = 1
            generic.pprint(msg)


    else:
        generic.pprint("""
hamstall. A Python based package manager to manage archives.
Written by: hammy3502

hamstall Version: {user_version}
Internal Version Code: {file_version}.{prog_version}

For help, type "hamstall -h"
        """.format(user_version=config.get_version("version"), file_version=config.get_version("file_version"),
                prog_version=config.get_version("prog_internal_version")))

    config.unlock()
    if mode == "gui":
        return
    elif mode == "cli":
        sys.exit(exit_code)


if __name__ == "__main__":
    if mode == "cli":
        parse_args()
    elif mode == "gui":
        gui_loop()
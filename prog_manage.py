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
from shutil import copyfile, rmtree, move, which, copy
from subprocess import call
import sys
import re

try:
    import requests
    can_update = True
except ImportError:
    can_update = False
    print("##########WARNING##########")
    print("requests library not installed! Ability to update hamstall")
    print("has been disabled! Use `pip3 install requests` or ")
    print("`python3 -m pip install requests` to install it!")
    print("###########################")

import config
import generic


def create_db():
    """Creates Database."""
    db_template = {
        "options": {
            "Verbose": False,
            "AutoInstall": False,
            "ShellFile": config.get_shell_file()
        },
        "version": {
            "file_version": config.file_version,
            "prog_internal_version": config.prog_internal_version,
            "branch": "master"
        },
        "programs": {
        }
    }
    config.db = db_template
    config.write_db()


def branch_wizard():
    """Switch Branches."""
    print("""\n\n
####WARNING####
WARNING: You are changing branches of hamstall!
Changing from master to beta means you may receive updates that contain bugs, some extremely severe!
Changing from beta to master can lead to extreme problems, as backtracking is not supported!

Switching branches will trigger an immediate update of hamstall!

Select a branch:
m - Master branch. Less bugs, more stable, wait for updates.
b - Beta branch. More bugs, less stable, updates asap.
E - Exit branch wizard and don't change branches.
    """)
    ans = generic.get_input("[m/b/E] ", ['m', 'b', 'e'], 'e')
    if ans == 'e':
        print("Not changing branches!")
        generic.leave()
    elif ans == 'm' and config.db["version"]["branch"] == "master":
        print("Already on the master branch, not switching!")
        generic.leave()
    elif ans == 'b' and config.db["version"]["branch"] == "beta":
        print("Already on the beta branch, not switching!")
        generic.leave()
    else:
        check = input('Type "YES" (without the quotes) to confirm the branch switch!')
        if check != "YES":
            print("Cancelling branch switch.")
            generic.leave()
        if ans == 'm':
            branch = "master"
        elif ans == 'b':
            branch = "beta"
        print("Changing branches and updating hamstall!")
        config.vprint("Switching branch and writing change to file")
        config.db["version"]["branch"] = branch
        config.write_db()
        config.vprint("Updating hamstall...")
        update(True)
        generic.leave(0)


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
            if not can_update:
                print("requests isn't installed, so AutoInstall cannot be enabled!")
            else:
                key = "AutoInstall"
        elif option == 'v':
            key = "Verbose"
        elif option == 'b':
            branch_wizard()
        elif option == 'e':
            generic.leave()
        new_value = config.change_config(key, "flip")
        print("\n{key} mode {value}!".format(key=key, value=generic.endi(new_value)))


def remove_desktop(program):
    """Remove .desktop

    Removes a .desktop file assosciated with a program and its corresponding entry in the database
    This process is walked through with the end-user

    """
    if not config.db["programs"][program]["desktops"]:
        print("Program has no .desktop files!")
    else:
        print("Desktops: ")
        for d in config.db["programs"][program]["desktops"]:
            print(d)
        inp = "/ choose desktop"
        while not (inp in config.db["programs"][program]["desktops"]) and inp != "exit":
            inp = input("Please enter the desktop you would like to remove or type \"exit\" to exit: ")
        try:
            os.remove(config.full("~/.local/share/applications/{}.desktop".format(inp)))
        except FileNotFoundError:
            pass
        config.db["programs"][program]["desktops"].remove(inp)


def finish_install(program_internal_name):
    """End of Install.

    Ran after every program install.

    Args:
        program_internal_name (str): Name of program as stored in the database

    """
    config.vprint("Removing temporary install directory (if it exists)")
    try:
        rmtree("/tmp/hamstall-temp")
    except FileNotFoundError:
        pass
    config.vprint("Adding program to hamstall list of programs")
    config.db["programs"].update({program_internal_name: {"desktops": []}})
    yn = generic.get_input('Would you like to add the program to your PATH? [Y/n]', ['y', 'n'], 'y')
    if yn == 'y':
        pathify(program_internal_name)
    yn = generic.get_input('Would you like to create a binlink? [y/N]', ['y', 'n'], 'n')
    if yn == 'y':
        binlink(program_internal_name)
    yn = generic.get_input('Would you like to create a desktop file? [y/N]', ['y', 'n'], 'n')
    if yn == 'y':
        create_desktop(program_internal_name)
    print("Install complete!")
    generic.leave()


def create_desktop(program_internal_name):
    """Create Desktop.

    Walks the user through creating a .desktop file for a program

    Args:
        program_internal_name (str): Name of program as stored in the database

    """
    files = os.listdir(config.full('~/.hamstall/bin/' + program_internal_name + '/'))
    print(' '.join(files))
    program_file = '/Placeholder/'
    config.vprint("Getting user inputs")
    while program_file not in files:  # Get file to binlink from user
        program_file = input('Please enter a file listed above. If you would like to cancel, type exit: ')
        if program_file == "exit":
            return
    desktop_name = "{}-{}".format(program_file, program_internal_name)
    if config.exists("~/.local/share/applications/{}.desktop".format(desktop_name)):
        print("Desktop file already exists!")
        return
    exec_path = config.full("~/.hamstall/bin/{}/{}".format(program_internal_name, program_file))
    comment = "/"
    while not comment.replace(" ", "").isalnum() and comment != "":
        comment = input("Please input a comment for the application: ")
    if comment == "":
        comment = program_internal_name
    terminal = generic.get_input("Should this program launch a terminal to run it in? [y/N]", ['y', 'n'], 'n')
    if terminal.lower() == 'y':
        should_terminal = "True"
    else:
        should_terminal = "False"
    name = "/"
    while not name.replace(" ", "").isalnum() and name != "":
        name = input("Please enter a name: ")
    if name == "":
        name = program_internal_name
    ans = " "
    chosen_categories = []
    categories = ["audio", "video", "development", "education", "game", "graphics", "network", "office", "science",
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
            if ans in ["Audio", "Video"] and not ("AudioVideo" in chosen_categories):
                chosen_categories.append("AudioVideo")
    if not chosen_categories:
        chosen_categories = ["Utility"]
    cats = ";".join(chosen_categories) + ";"  # Get categories for the .desktop
    to_write = """
[Desktop Entry]
Name={name}
Comment={comment}
Exec={exec_path}
Terminal={should_terminal}
Type=Application
Categories={categories}
""".format(name=name, comment=comment, exec_path=exec_path,
           should_terminal=should_terminal, categories=cats)
    os.chdir(config.full("~/.local/share/applications/"))
    config.create("./{}.desktop".format(desktop_name))
    with open(config.full("./{}.desktop".format(desktop_name)), 'w') as f:
        f.write(to_write)
    config.db["programs"][program_internal_name]["desktops"].append(desktop_name)
    print("\nDesktop file created!")


def gitinstall(git_url, program_internal_name, overwrite=False):
    """Git Install.

    Installs a program from a URL to a Git repository

    Args:
        git_url (str): URL to Git repository
        program_internal_name (str): Name of program to use

    """
    config.vprint("Verifying that the input is a URL...")
    if re.match(r"https://\w.\w", git_url) is None or " " in git_url or "\\" in git_url:
        print("Invalid URL!")
        generic.leave()
    config.vprint("Checking for .git extension")
    if config.extension(git_url) != ".git":
        print("The URL must end in .git!")
        generic.leave(1)
    config.vprint("Downloading git repository")
    if overwrite:
        try:
            rmtree(config.full("/tmp/hamstall-temp"))  # Removes temp directory (used during installs)
        except FileNotFoundError:
            pass
        os.chdir("/tmp/hamstall-temp")
    else:
        os.chdir(config.full("~/.hamstall/bin"))
    err = call(["git", "clone", git_url])
    if err != 0:
        print("Error detected! Installation halted.")
        generic.leave(1)
    if overwrite:
        call(["rsync", "-a", "/tmp/hamstall-temp", config.full("~/.hamstall/bin/{}".format(program_internal_name))])
    finish_install(program_internal_name)


def manage(program):
    """Manage Installed Program.

    Args:
        program (str): Internal name of program to manage

    """
    while True:
        print("Enter an option to manage " + program + ":")
        print("b - Create binlinks for " + program)
        print("p - Add " + program + " to PATH")
        print("u - Uninstall " + program)
        print("r - Remove all binlinks + PATHs for " + program)
        print("d - Create a .desktop file for " + program)
        print("rd - Remove a .desktop file for " + program)
        print("c - Run a command inside " + program + "'s directory")
        print("s - Launch a shell inside " + program + "'s directory")
        print("E - Exit program management")
        option = generic.get_input("[b/p/u/r/d/rd/c/s/E]", ['b', 'p', 'u', 'r', 'd', 'c', 'rd', 's', 'e'], 'e')
        if option == 'b':
            binlink(program)
        elif option == 'p':
            pathify(program)
        elif option == 'u':
            uninstall(program)
            generic.leave()
        elif option == 'r':
            config.remove_line(program, "~/.hamstall/.bashrc", 'poundword')
        elif option == 'd':
            create_desktop(program)
        elif option == 'rd':
            remove_desktop(program)
        elif option == 'c':
            command(program)
        elif option == 's':
            print("When you exit the shell, you will be returned to here.")
            os.chdir(config.full("~/.hamstall/bin/" + program + "/"))
            call(["/bin/bash"])
        elif option == 'e':
            generic.leave()


def binlink(program_internal_name):
    """Link Program

    Creates an alias that cd's into a program directory before running a file in the program

    Args:
        program_internal_name (str): Name of program to create a binlink for

    """
    while True:
        files = os.listdir(config.full('~/.hamstall/bin/' + program_internal_name + '/'))
        print(' '.join(files))
        file_chosen = 'Cool fact. This line was originally written on line 163.'
        while file_chosen not in files:  # Get file to binlink from user
            file_chosen = input('Please enter a file listed above. If you would like to cancel, type exit: ')
            if file_chosen == "exit":
                return
        line_to_add = 'alias ' + file_chosen + "='cd " + config.full('~/.hamstall/bin/' + program_internal_name) + \
                      '/ && ./' + file_chosen + "' # " + program_internal_name + "\n"
        config.vprint("Adding alias to bashrc")
        config.add_line(line_to_add, "~/.hamstall/.bashrc")
        yn = generic.get_input('Would you like to continue adding files to be run directly? [y/N]', ['y', 'n'], 'n')
        if yn == 'n':
            return


def pathify(program_internal_name):
    """Add Program to Path.

    Adds a program to PATH through ~/.hamstall/.bashrc

    Args:
        program_internal_name (str): Name of program to add to PATH

    """
    config.vprint('Adding program to PATH')
    line_to_write = "export PATH=$PATH:~/.hamstall/bin/" + program_internal_name + ' # ' + program_internal_name + '\n'
    config.add_line(line_to_write, "~/.hamstall/.bashrc")
    return


def command(program):
    """Mini-Shell.

    Takes commands and passes them to the user's command interpreter while in the program directory

    Args:
        program (str): Program to run commands on

    """
    run = 'y'
    while run == 'y':
        command = input('Please enter a command: ')
        call(["cd", "~/.hamstall/bin/{}/".format(program), "&&", command])
        run = generic.get_input('Would you like to run another command? [y/N]', ['y', 'n'], 'n')
    return


def update(silent=False):
    """Update Hamstall.

    Checks to see if we should update hamstall, then does so if one is available

    Args:
        silent (bool): Whether or not to not provide user feedback. Defaults to False.

    """
    if not can_update:
        print("requests not found! Can't update!")
        if silent:
            return
        else:
            generic.leave(1)
    """Update hamstall after checking for updates"""
    prog_version_internal = config.get_version('prog_internal_version')
    config.vprint("Checking version on GitHub")
    final_version = get_online_version('prog')
    config.vprint('Installed internal version: ' + str(prog_version_internal))
    config.vprint('Version on GitHub: ' + str(final_version))
    if final_version > prog_version_internal:
        print("An update has been found! Installing...")
        config.vprint('Removing old hamstall pys...')
        os.chdir(config.full("~/.hamstall"))
        files = os.listdir()
        for i in files:
            i_num = len(i) - 3
            if i[i_num:len(i)] == '.py':
                os.remove(config.full('~/.hamstall/' + i))
        config.vprint("Downloading new hamstall pys..")
        download_files(['hamstall.py', 'generic.py', 'config.py', 'config.py', 'prog_manage.py'], '~/.hamstall/')
        config.db["version"]["prog_internal_version"] = final_version
    elif final_version < prog_version_internal:
        if not silent:
            print("hamstall version newer than latest online version! Something might be wrong...")
    else:
        if not silent:
            print("No update found!")


def erase():
    """Remove hamstall."""
    if not (config.exists(config.full("~/.hamstall/hamstall.py"))):
        print("hamstall not detected so not removed!")
        generic.leave()
    config.vprint('Removing source line from bashrc')
    config.remove_line("~/.hamstall/.bashrc", "~/{}".format(config.read_config("ShellFile")), "word")
    config.vprint("Removing .desktop files")
    for prog in config.db["programs"]:
        if config.db["programs"][prog]["desktops"]:
            for d in config.db["programs"][prog]["desktops"]:
                try:
                    os.remove(config.full("~/.local/share/applications/{}.desktop".format(d)))
                except FileNotFoundError:
                    pass
    config.vprint('Removing hamstall directory')
    rmtree(config.full('~/.hamstall'))
    try:
        rmtree("/tmp/hamstall-temp")
    except FileNotFoundError:
        pass
    print("Hamstall has been removed from your system.")
    print('Please restart your terminal.')
    config.unlock()
    sys.exit(0)


def first_time_setup(sym):
    """First Time Setup.

    Sets up hamstall for the first time.

    Args:
        sym (bool): Used for testing. If True, installed py's will be symlinked to originals, not copied.
        False means it will be copied and not symlinked.

    """
    if config.exists(config.full('~/.hamstall/hamstall.py')):
        print('Please don\'t run first time setup on an already installed system!')
        generic.leave()
    print('Installing hamstall to your system...')
    try:
        os.mkdir(config.full("~/.hamstall"))
    except FileExistsError:
        rmtree(config.full("~/.hamstall"))
        os.mkdir(config.full("~/.hamstall"))
    try:
        os.mkdir(config.full("/tmp/hamstall-temp/"))
    except FileExistsError:
        rmtree(config.full("/tmp/hamstall-temp"))
        os.mkdir(config.full("/tmp/hamstall-temp/"))
    os.mkdir(config.full("~/.hamstall/bin"))
    config.create("~/.hamstall/database")
    create_db()
    config.create("~/.hamstall/.bashrc")  # Create directories and files
    files = os.listdir()
    for i in files:
        i_num = len(i) - 3
        if i[i_num:len(i)] == '.py':
            if sym:
                os.symlink(os.getcwd() + "/" + i, config.full("~/.hamstall/" + i))
            else:
                try:
                    copyfile(i, config.full('~/.hamstall/' + i))
                except FileNotFoundError:
                    print("A file is missing that was attempted to be copied! Install halted!")
                    generic.leave(1)
    config.add_line("source ~/.hamstall/.bashrc\n", "~/{}".format(config.read_config("ShellFile")))
    config.add_line("alias hamstall='python3 ~/.hamstall/hamstall.py'\n", "~/.hamstall/.bashrc")  # Add bashrc line
    print('First time setup complete!')
    print('Please run the command "source ~/{}" or restart your terminal.'.format(config.read_config("ShellFile")))
    print('Afterwards, you may begin using hamstall with the hamstall command!')
    generic.leave()


def verbose_toggle():
    """Enable/Disable Verbosity."""
    new_value = config.change_config('Verbose', 'flip')
    print("Verbose mode {}".format(generic.endi(new_value)))


def create_command(file_extension, program, overwrite_files=False):
    """Create Extraction Command.

    Args:
        file_extension (str): File extension of program (including .)
        program (str): Program name
        overwrite_files (bool): Whether or not the command should overwrite files. Defaults to False.

    Returns:
        str: Command to run

    """
    if config.vcheck():  # Creates the command to run to extract the archive
        if file_extension == '.tar.gz' or file_extension == '.tar.xz':
            vflag = 'v'
        elif file_extension == '.zip':
            vflag = ''
        elif file_extension == '.7z':
            vflag = ''
        elif file_extension == '.rar':
            vflag = ''
    else:
        if file_extension == '.tar.gz' or file_extension == '.tar.xz':
            vflag = ''
        elif file_extension == '.zip':
            vflag = '-qq'
        elif file_extension == '.7z':
            vflag = '-bb0 -bso0 -bd '
        elif file_extension == '.rar':
            vflag = '-idcdpq '
    if overwrite_files:
        if file_extension in [".tar.gz", ".tar.xz"]:
            overwrite_flag = "--overwrite "
        elif file_extension == ".zip":
            overwrite_flag = " -o"
        elif file_extension == ".7z":
            overwrite_flag = "-y "
        elif file_extension == ".rar":
            overwrite_flag = "-o+ "
    else:
        overwrite_flag = ""
    if file_extension == '.tar.gz' or file_extension == '.tar.xz':
        command_to_go = "tar " + vflag + "xf " + overwrite_flag + program + " -C /tmp/hamstall-temp/"
        if which("tar") is None:
            print("tar not installed; please install it to install .tar.gz and .tar.xz files!")
            generic.leave()
    elif file_extension == '.zip':
        command_to_go = 'unzip ' + vflag + overwrite_flag + ' ' + program + ' -d /tmp/hamstall-temp/'
        if which("unzip") is None:
            print("unzip not installed; please install it to install ZIP files!")
            generic.leave()
    elif file_extension == '.7z':
        command_to_go = '7z x ' + overwrite_flag + vflag + program + ' -o/tmp/hamstall-temp/'
        if which("7z") is None:
            print("7z not installed; please install it to install 7z files!")
            generic.leave()
    elif file_extension == '.rar':
        command_to_go = 'unrar x ' + overwrite_flag + vflag + program + ' /tmp/hamstall-temp/'
        if which("unrar") is None:
            print("unrar not installed; please install it to install RAR files!")
            generic.leave()
    else:
        print('Error! File type not supported!')
        generic.leave(1)
    config.vprint("Running command: " + command_to_go)
    return command_to_go


def install(program, overwrite=False):
    """Install Archive.

    Takes an archive and installs it.

    Args:
        program (str): Path to archive to install

    """
    program_internal_name = config.name(program)
    if config.char_check(program_internal_name):
        print("Error! Archive name contains a space or #!")
        generic.leave(1)
    config.vprint("Removing old temp directory (if it exists!)")
    try:
        rmtree(config.full("/tmp/hamstall-temp"))  # Removes temp directory (used during installs)
    except FileNotFoundError:
        pass
    config.vprint("Creating new temp directory")
    os.mkdir(config.full("/tmp/hamstall-temp"))  # Creates temp directory for extracting archive
    config.vprint("Extracting archive to temp directory")
    file_extension = config.extension(program)
    program = config.spaceify(program)
    command_to_go = create_command(file_extension, program, overwrite)
    config.vprint('File type detected: ' + file_extension)
    try:
        os.system(command_to_go)  # Extracts program archive
    except:
        print('Failed to run command: ' + command_to_go + "!")
        print("Program installation halted!")
        generic.leave(1)
    config.vprint('Checking for folder in folder')
    if os.path.isdir(config.full('/tmp/hamstall-temp/' + program_internal_name + '/')):
        config.vprint('Folder in folder detected! Using that directory instead...')
        source = config.full('/tmp/hamstall-temp/' + program_internal_name + '/')
        dest = config.full('~/.hamstall/bin/')
    else:
        config.vprint('Folder in folder not detected!')
        source = config.full('/tmp/hamstall-temp')
        dest = config.full('~/.hamstall/bin/' + program_internal_name)
    config.vprint("Moving program to directory")
    move(source, dest)
    config.vprint("Adding program to hamstall list of programs")
    config.vprint('Removing old temp directory...')
    try:
        rmtree(config.full("/tmp/hamstall-temp"))
    except FileNotFoundError:
        config.vprint('Temp folder not found so not deleted!')
    finish_install(program_internal_name)


def dirinstall(program_path, program_internal_name, overwrite=False):
    """Install Directory.

    Installs a directory as a program

    Args:
        program_path (str): Path to directory to install
        program_internal_name (str): Name of program

    """
    config.vprint("Moving folder to hamstall destination")
    if overwrite:
        call(["rsync", "-a", program_path, config.full("~/.hamstall/bin/{}".format(program_internal_name))])
        rmtree(program_path)
    else:
        move(program_path, config.full("~/.hamstall/bin/"))
    finish_install(program_internal_name)


def uninstall(program):
    """Uninstall a Program.

    Args:
        program (str): Name of program to uninstall

    """
    config.vprint("Removing program files")
    rmtree(config.full("~/.hamstall/bin/" + program + '/'))
    config.vprint("Removing program from PATH and any binlinks for the program")
    config.remove_line(program, "~/.hamstall/.bashrc", 'poundword')
    config.vprint("Removing program desktop files")
    if config.db["programs"][program]["desktops"]:
        for d in config.db["programs"][program]["desktops"]:
            try:
                os.remove(config.full("~/.local/share/applications/{}.desktop".format(d)))
            except FileNotFoundError:
                pass
    config.vprint("Removing program from hamstall list of programs")
    del config.db["programs"][program]
    print("Uninstall complete!")
    return


def list_programs():
    """List Installed Programs."""
    for prog in config.db["programs"].keys():
        print(prog)
    generic.leave()


def get_online_version(type_of_replacement):
    """Get hamstall Version from GitHub.

    Args:
        type_of_replacement (str): Type of version to get (file or prog)
    
    Returns:
        int: The specified version
    """
    if not can_update:
        print("requests library not installed! Exiting...")
        generic.leave(1)
    version_url = "https://raw.githubusercontent.com/hammy3502/hamstall/{}/version".format(config.db["version"]["branch"])
    version_raw = requests.get(version_url)
    version = version_raw.text
    spot = version.find(".")
    if type_of_replacement == 'file':
        return int(version[0:spot])
    elif type_of_replacement == 'prog':
        return int(version[spot + 1:])


def get_file_version(version_type):
    """Get Database Versions.

    Gets specified version of hamstall as stored in the database

    Args:
        version_type (str): Type of version to look up (file/prog)

    Returns:
        int: The specified version number

    """
    if version_type == 'file':
        return config.db["version"]["file_version"]
    elif version_type == 'prog':
        return config.db["version"]["prog_internal_version"]


def download_files(files, folder):
    """Download List of Files.
    
    Args:
        files (str[]): List of files to obtain from hamstall repo
        folder (str): Folder to put files in

    """
    if not can_update:
        print("Cannot download files if the request library isn't installed!")
        generic.leave(1)
    for i in files:
        r = requests.get(
            "https://raw.githubusercontent.com/hammy3502/hamstall/{}/".format(config.db["version"]["branch"]) + i)
        open(config.full(folder + i), 'wb').write(r.content)


verbose = config.vcheck()

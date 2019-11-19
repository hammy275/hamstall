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
import getpass

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


def hamstall_startup(start_fts=False, del_lock=False):
    """Run on Startup.

    Runs on hamstall startup to perform any required checks and upgrades.
    This function should always be run before doing anything else with hamstall.

    Args:
        start_fts (bool): Whether or not to start first time setup
        del_lock (bool): Whether or not to remove the lock (if it exists)

    Returns:
        str: One of many different values indicating the status of hamstall. Those include:
        "Not installed", "Locked", "Good" (nothing bad happened), "Root" and "Old" (happens
        when upgrading from hamstall prog_version 1). Can also return a string from
        first_time_setup.

    """
    if config.locked():  # Lock check
        config.vprint("Lock file detected at /tmp/hamstall-lock.")
        if del_lock:
            config.vprint("Deleting the lock and continuing execution!")
            config.unlock()
        else:
            config.vprint("Lock file removal not specified; staying locked.")
            return "Locked"
    else:
        config.lock()

    if config.db == {"refresh": True}:  # Downgrade check
        print("Hang tight! We're finishing up your downgrade...")
        config.create("~/.hamstall/database")
        create_db()
        config.db = config.get_db()
        config.write_db()
        print("We're done! Continuing hamstall execution...")

    if start_fts:  # Check if -f or --first is supplied
        return first_time_setup(False)

    if not(config.exists('~/.hamstall/hamstall.py')):  # Make sure hamstall is installed
        return "Not installed"

    try:  # Lingering upgrades check
        file_version = get_file_version('file')
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
            create_db()
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
            config.db["version"]["file_version"] = 5
            config.vprint("Upgraded from hamstall file version 4 to 5.")
        try:
            file_version = get_file_version('file')
        except KeyError:
            file_version = 1
        config.write_db()

    if get_file_version('prog') == 1:  # Online update broke between prog versions 1 and 2 of hamstall
        return "Old"

    if config.read_config("AutoInstall"):  # Auto-update, if enabled
        update()
    
    username = getpass.getuser()  # Root check
    if username == 'root':
        config.vprint("We're running as root!")
        return "Root"
    
    return "Good"


def pre_install(program, overwrite=None):
    """Pre-Archive Install.

    Preparation before installing an archive.

    Arguments:
        program (str): Path to archive to attempt installation.
        overwrite (bool/None): Whether or not to overwrite the program if it exists.

    Returns:
        str: Status of the installation. Possible returns are: "Bad file", and "Application exists".

    """
    if not config.exists(program):
        return "Bad file"
    program_internal_name = config.name(program)  # Get the program name
    if program_internal_name in config.db["programs"]:  # Reinstall check
        if overwrite is None:
            return "Application exists"
        else:
            if not overwrite:
                uninstall(program_internal_name)
                return install(program)  # Reinstall
            elif overwrite:
                return install(program, True)
    else:
        return install(program)  # No reinstall needed to be asked, install program
    config.write_db()


def pre_gitinstall(program, overwrite=None):
    """Before Git Installs.

    Args:
        program (str): Git URL to install
        overwrite (bool/None): Whether to do an overwrite reinstall. Defaults to None.

    Returns:
        str: Statuses. Includes: 

    """
    if not config.check_bin("git"):
        return "No git"
    elif re.match(r"https://\w.\w", program) is None or " " in program or "\\" in program or config.extension(program) != ".git":
        return "Bad URL"
    else:
        program_internal_name = config.name(program)
        if program_internal_name in config.db["programs"]:
            if overwrite is None:
                return "Application exists"
            else:
                if not overwrite:
                    uninstall(program_internal_name)
                    return gitinstall(program, program_internal_name)
                elif overwrite:
                    return gitinstall(program, program_internal_name, True)
        else:
            return gitinstall(program, program_internal_name)
    config.write_db()


def pre_dirinstall(program, overwrite=None):
    if not(os.path.isdir(config.full(program))) or program[-1:] != '/':
        return "Bad folder"
    prog_int_name_temp = program[0:len(program)-1]
    program_internal_name = config.name(prog_int_name_temp + '.tar.gz')  # Add .tar.gz to make the original function work
    if program_internal_name in config.db["programs"]:
        if overwrite is None:
            return "Application exists"
        elif not overwrite:
            uninstall(program_internal_name)
            return dirinstall(program, program_internal_name)
        elif overwrite:
            return dirinstall(program, program_internal_name, True)
    else:
        return dirinstall(program, program_internal_name)
    config.write_db()


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
        generic.leave()
    elif ans == 'm' and config.db["version"]["branch"] == "master":
        print("Already on the master branch, not switching!")
        generic.leave()
    elif ans == 'b' and config.db["version"]["branch"] == "beta":
        print("Already on the beta branch, not switching!")
        generic.leave()
    else:
        check = input('Type "YES" (without the quotes) to confirm the branch switch! ')
        if check != "YES":
            print("Cancelling branch switch.")
            generic.leave()
        if ans == 'm':
            branch = "master"
            if not config.check_bin("git"):
                print("Git is not installed! Your branch can be switched, but downgrading is impossible! "
                "If you would like to exit here, type \"y\"!")
                if generic.get_input("", ['y','n'], 'n') == 'y':
                    print("Branch has not been changed!")
                    generic.leave(1)
                else:
                    print("Continuing with branch switch.")
        elif ans == 'b':
            branch = "beta"
        print("Changing branches and updating hamstall!")
        config.vprint("Switching branch and writing change to file")
        config.db["version"]["branch"] = branch
        config.write_db()
        if branch == "beta":
            config.vprint("Updating hamstall...")
            update(True)
            generic.leave(0)
        elif branch == "master":
            if get_online_version("prog", "master") <= 18:
                print("Cannot downgrade; staying on this version until master catches up!")
                generic.leave(0)
            print("Would you like to downgrade? If you do, all hamstall programs will be deleted!")
            dr = generic.get_input("If you don't, hamstall will remain at its current version until master is at a newer release! [y/N]",
            ['y', 'n'], 'n')
            if dr == 'y':
                config.vprint("Deleting and re-installing hamstall.")
                os.chdir(config.full("~/.hamstall"))
                config.vprint("Removing old hamstall .pys")
                for i in os.listdir():
                    i_num = len(i) - 3
                    if i[i_num:len(i)] == '.py':
                        try:
                            os.remove(i)
                        except FileNotFoundError:
                            pass
                try:
                    rmtree("/tmp/hamstall-temp")
                except FileNotFoundError:
                    pass
                os.mkdir("/tmp/hamstall-temp")
                os.chdir("/tmp/hamstall-temp")
                config.vprint("Cloning hamstall from the master branch")
                call(["git", "clone", "https://github.com/hammy3502/hamstall.git"])
                os.chdir("/tmp/hamstall-temp/hamstall")
                config.vprint("Adding new hamstall .pys")
                for i in os.listdir():
                    i_num = len(i) - 3
                    if i[i_num:len(i)] == '.py':
                        copyfile(i, config.full('~/.hamstall/' + i))
                config.vprint("Removing old database and programs.")
                try:
                    os.remove(config.full("~/.hamstall/database"))
                except FileNotFoundError:
                    pass
                try:
                    rmtree(config.full("~/.hamstall/bin"))
                except FileNotFoundError:
                    pass
                os.mkdir(config.full("~/.hamstall/bin"))
                print("Please run hamstall again to re-create the database!")
                config.unlock()
                config.db = {"refresh": True}
                config.write_db()
                sys.exit(0)


def remove_desktop(program, desktop):
    """Remove .desktop

    Removes a .desktop file assosciated with a program and its corresponding entry in the database
    This process is walked through with the end-user

    Args:
        program (str): Program to remove
        desktop (str): Name of .desktop to remove

    """
    try:
        os.remove(config.full("~/.local/share/applications/{}.desktop".format(desktop)))
    except FileNotFoundError:
        pass
    config.db["programs"][program]["desktops"].remove(desktop)
    config.write_db()


def remove_paths_and_binlinks(program):
    """Remove PATHs and binlinks for "program"

    Args:
        program (str): Program to remove PATHs and binlinks of

    Returns:
        str: "Complete"

    """
    config.remove_line(program, "~/.hamstall/.bashrc", 'poundword')
    return "Complete"


def rename(program, new_name):
    """Rename Program.

    Args:
        program (str): Name of program to rename

    Returns:
        str: New program name

    """
    for d in config.db["programs"][program]["desktops"]:
        config.replace_in_file("/.hamstall/bin/{}".format(program), "/.hamstall/bin/{}".format(new_name), 
        "~/.local/share/applications/{}.desktop".format(d))
    config.db["programs"][new_name] = config.db["programs"].pop(program)
    config.replace_in_file("export PATH=$PATH:~/.hamstall/bin/" + program, 
    "export PATH=$PATH:~/.hamstall/bin/" + new_name, "~/.hamstall/.bashrc")
    config.replace_in_file("'cd " + config.full('~/.hamstall/bin/' + program),
    "'cd " + config.full('~/.hamstall/bin/' + new_name), "~/.hamstall/.bashrc")
    config.replace_in_file("# " + program, "# " + new_name, "~/.hamstall/.bashrc")
    move(config.full("~/.hamstall/bin/" + program), config.full("~/.hamstall/bin/" + new_name))
    config.write_db()
    return new_name


def finish_install(program_internal_name):
    """End of Install.

    Ran after every program install.

    Args:
        program_internal_name (str): Name of program as stored in the database

    Returns:
        str: "Installed".

    """
    config.vprint("Removing temporary install directory (if it exists)")
    try:
        rmtree("/tmp/hamstall-temp")
    except FileNotFoundError:
        pass
    config.vprint("Adding program to hamstall list of programs")
    config.db["programs"].update({program_internal_name: {"desktops": []}})
    config.write_db()
    return "Installed"


def create_desktop(program_internal_name, name, program_file, comment="", should_terminal="", cats=[], icon=""):
    """Create Desktop.

    Create a desktop file for a program installed through hamstall.

    Args:
         program_internal_name (str): Name of program
         name (str): The name as will be used in the .desktop file
         program_file (str): The file in the program directory to point the .desktop to
         comment (str): The comment as to be displayed in the .desktop file
         should_terminal (str): "True" or "False" as to whether or not a terminal should be shown on program run
         cats (str[]): List of categories to put in .desktop file
         icon (str): The path to a valid icon or a specified icon as would be put in a .desktop file

    Returns:
        str: "Already exists" if the .desktop file already exists or "Created" if the desktop file was
        successfully created.
    """
    exec_path = config.full("~/.hamstall/bin/{}/{}".format(program_internal_name, program_file))
    path = config.full("~/.hamstall/bin/{}/".format(program_internal_name))
    desktop_name = "{}-{}".format(program_file, program_internal_name)
    if config.exists("~/.local/share/applications/{}.desktop".format(desktop_name)):
        print("Desktop file already exists!")
        return "Already exists"
    if "Video" not in cats or "Audio" not in cats and not ("AudioVideo" in cats):
        cats.append("AudioVideo")
    if not cats:
        cats = ["Utility"]
    cats = ";".join(cats) + ";"  # Get categories for the .desktop
    if comment != "":
        comment = "Comment=" + comment
    elif exec_path != "":
        exec_path = "Exec=" + exec_path
    elif icon != "":
        icon = "Icon=" + icon
    to_write = """
[Desktop Entry]
Name={name}
{comment}
Path={path}
{exec_path}
{icon}
Terminal={should_terminal}
Type=Application
Categories={categories}
""".format(name=name, comment=comment, exec_path=exec_path,
           should_terminal=should_terminal, categories=cats,
           icon=icon, path=path)
    os.chdir(config.full("~/.local/share/applications/"))
    config.create("./{}.desktop".format(desktop_name))
    with open(config.full("./{}.desktop".format(desktop_name)), 'w') as f:
        f.write(to_write)
    config.db["programs"][program_internal_name]["desktops"].append(desktop_name)
    config.write_db()
    return "Created"


def gitinstall(git_url, program_internal_name, overwrite=False):
    """Git Install.

    Installs a program from a URL to a Git repository

    Args:
        git_url (str): URL to Git repository
        program_internal_name (str): Name of program to use
        overwrite (bool): Whether or not to assume the program is already installed and to overwite it

    Returns:
       str: A string from finish_install(), "No rsync" or "Error"

    """
    if not config.check_bin("rsync") and overwrite:
        return "No rsync"
    config.vprint("Downloading git repository")
    if overwrite:
        try:
            rmtree(config.full("/tmp/hamstall-temp"))  # Removes temp directory (used during installs)
        except FileNotFoundError:
            pass
        os.mkdir("/tmp/hamstall-temp")
        os.chdir("/tmp/hamstall-temp")
    else:
        os.chdir(config.full("~/.hamstall/bin"))
    err = call(["git", "clone", git_url])
    if err != 0:
        return "Error"
    if overwrite:
        call(["rsync", "-a", "/tmp/hamstall-temp/{}/".format(program_internal_name), config.full("~/.hamstall/bin/{}".format(program_internal_name))])
    finish_install(program_internal_name)


def add_binlink(file_chosen, program_internal_name):
    line_to_add = 'alias ' + file_chosen + "='cd " + config.full('~/.hamstall/bin/' + program_internal_name) + \
    '/ && ./' + file_chosen + "' # " + program_internal_name + "\n"
    config.vprint("Adding alias to bashrc")
    config.add_line(line_to_add, "~/.hamstall/.bashrc")


def pathify(program_internal_name):
    """Add Program to Path.

    Adds a program to PATH through ~/.hamstall/.bashrc

    Args:
        program_internal_name (str): Name of program to add to PATH

    """
    config.vprint('Adding program to PATH')
    line_to_write = "export PATH=$PATH:~/.hamstall/bin/" + program_internal_name + ' # ' + program_internal_name + '\n'
    config.add_line(line_to_write, "~/.hamstall/.bashrc")
    return "Complete"


def update():
    """Update Hamstall.

    Checks to see if we should update hamstall, then does so if one is available

    Returns:
        str: "No requests" if requests isn't installed, "Newer version" if the installed
        version is newer than the one online, "No update" if there is no update, and
        "Updated" upon a successful update.
    """
    if not can_update:
        config.vprint("requests isn't installed.")
        return "No requests"
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
        download_files(['hamstall.py', 'generic.py', 'config.py', 'config.py', 'py'], '~/.hamstall/')
        config.db["version"]["prog_internal_version"] = final_version
        config.write_db()
        return "Updated"
    elif final_version < prog_version_internal:
        return "Newer version"
    else:
        return "No update"


def erase():
    """Remove hamstall.

    Returns:
        str: "Erased" on success or "Not installed" if hamstall isn't installed.

    """
    if not (config.exists(config.full("~/.hamstall/hamstall.py"))):
        return "Not installed"
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
    return "Erased"


def first_time_setup(sym):
    """First Time Setup.

    Sets up hamstall for the first time.

    Args:
        sym (bool): Used for testing. If True, installed py's will be symlinked to originals, not copied.
        False means it will be copied and not symlinked.

    """
    if config.exists(config.full('~/.hamstall/hamstall.py')):
        return "Already installed"
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
                    return "Bad copy"
    config.add_line("source ~/.hamstall/.bashrc\n", "~/{}".format(config.read_config("ShellFile")))
    config.add_line("alias hamstall='python3 ~/.hamstall/hamstall.py'\n", "~/.hamstall/.bashrc")  # Add bashrc line
    return "Success"


def verbose_toggle():
    """Enable/Disable Verbosity.

    Returns:
        str: "enabled"/"disabled", depending on the new state.

    """
    new_value = config.change_config('Verbose', 'flip')
    return generic.endi(new_value)


def create_command(file_extension, program):
    """Create Extraction Command.

    Args:
        file_extension (str): File extension of program (including .)
        program (str): Program name
        overwrite_files (bool): Whether or not the command should overwrite files. Defaults to False.

    Returns:
        str: Command to run, "Bad Filetype", or "No bin_that_is_needed"

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
    if file_extension == '.tar.gz' or file_extension == '.tar.xz':
        command_to_go = "tar " + vflag + "xf " + program + " -C /tmp/hamstall-temp/"
        if which("tar") is None:
            print("tar not installed; please install it to install .tar.gz and .tar.xz files!")
            return "No tar"
    elif file_extension == '.zip':
        command_to_go = 'unzip ' + vflag + ' ' + program + ' -d /tmp/hamstall-temp/'
        if which("unzip") is None:
            print("unzip not installed; please install it to install ZIP files!")
            return "No unzip"
    elif file_extension == '.7z':
        command_to_go = '7z x ' + vflag + program + ' -o/tmp/hamstall-temp/'
        if which("7z") is None:
            return "No 7z"
    elif file_extension == '.rar':
        command_to_go = 'unrar x ' + vflag + program + ' /tmp/hamstall-temp/'
        if which("unrar") is None:
            return "No unrar"
    else:
        print('Error! File type not supported!')
        return "Bad Filetype"
    config.vprint("Running command: " + command_to_go)
    return command_to_go


def install(program, overwrite=False):
    """Install Archive.

    Takes an archive and installs it.

    Args:
        program (str): Path to archive to install
        overwrite (bool): Whether or not to assume the program is already installed and to overwite it

    Returns:
       str: A string from finish_install() a string from create_command(), "No rsync", "Bad name", or "Error"

    """
    if not config.check_bin("rsync") and overwrite:
        return "No rsync"
    program_internal_name = config.name(program)
    if config.char_check(program_internal_name):
        return "Bad name"
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
    command_to_go = create_command(file_extension, program)
    config.vprint('File type detected: ' + file_extension)
    if command_to_go.startswith("No") or command_to_go == "Bad Filetype":
        return command_to_go
    try:
        os.system(command_to_go)  # Extracts program archive
    except:
        print('Failed to run command: ' + command_to_go + "!")
        print("Program installation halted!")
        return "Error"
    config.vprint('Checking for folder in folder')
    if os.path.isdir(config.full('/tmp/hamstall-temp/' + program_internal_name + '/')):
        config.vprint('Folder in folder detected! Using that directory instead...')
        source = config.full('/tmp/hamstall-temp/' + program_internal_name) + '/'
        dest = config.full('~/.hamstall/bin/')
    else:
        config.vprint('Folder in folder not detected!')
        source = config.full('/tmp/hamstall-temp') + '/'
        dest = config.full('~/.hamstall/bin/' + program_internal_name + "/")
    config.vprint("Moving program to directory")
    if overwrite:
        if verbose:
            verbose_flag = "v"
        else:
            verbose_flag = ""
        call(["rsync", "-a{}".format(verbose_flag), source, dest])
    else:
        move(source, dest)
    config.vprint("Adding program to hamstall list of programs")
    config.vprint('Removing old temp directory...')
    try:
        rmtree(config.full("/tmp/hamstall-temp"))
    except FileNotFoundError:
        config.vprint('Temp folder not found so not deleted!')
    return finish_install(program_internal_name)


def dirinstall(program_path, program_internal_name, overwrite=False):
    """Install Directory.

    Installs a directory as a program

    Args:
        program_path (str): Path to directory to install
        program_internal_name (str): Name of program
        overwrite (bool): Whether or not to assume the program is already installed and to overwite it

    Returns:
       str: A string from finish_install() or "No rsync"

    """
    if not config.check_bin("rsync") and overwrite:
        return "No rsync"
    config.vprint("Moving folder to hamstall destination")
    if overwrite:
        call(["rsync", "-a", program_path, config.full("~/.hamstall/bin/{}".format(program_internal_name))])
        rmtree(program_path)
    else:
        move(program_path, config.full("~/.hamstall/bin/"))
    return finish_install(program_internal_name)


def uninstall(program):
    """Uninstall a Program.

    Args:
        program (str): Name of program to uninstall

    Returns:
        str: Status detailing the uninstall. Can be: "Not installed" or "Success".

    """
    if not program in config.db["programs"]:
        return "Not installed"
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
    config.write_db()
    return "Success"


def list_programs():
    """List Installed Programs.

    Returns:
        str[]: List of installed programs by name
    
    """
    return config.db["programs"].keys()


def get_online_version(type_of_replacement, branch=config.branch):
    """Get hamstall Version from GitHub.

    Args:
        type_of_replacement (str): Type of version to get (file or prog)
        branch (str): Branch to check version of (default: User's current branch)
    
    Returns:
        int: The specified version
    """
    if not can_update:
        print("requests library not installed! Exiting...")
        generic.leave(1)
    version_url = "https://raw.githubusercontent.com/hammy3502/hamstall/{}/version".format(branch)
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

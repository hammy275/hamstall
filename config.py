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
import sys
import re
import json
import shutil

###VERSIONS###

version = "1.3.0 beta"
prog_internal_version = 53
file_version = 8

#############


def check_bin(bin):
    """Check for Binary on System.

    Args:
        bin (str): Binary to check for
    
    Returns:
        bool: Whether or not the binary exists.
    """
    return shutil.which(bin) is not None


def get_shell_file():
    """Get Shell File.

    Attempts to automatically obtain the file used by the user's shell for PATH,
    variable exporting, etc.

    Returns:
        str: File name in home directory to store PATHs, variables, etc.

    """
    shell = os.environ["SHELL"]
    if "bash" in shell:
        vprint("Auto-detected bash")
        return ".bashrc"
    elif "zsh" in shell:
        vprint("Auto-detected zsh")
        return ".zshrc"
    else:
        vprint("Couldn't auto-detect shell environment! Defaulting to bash...")
        return ".bashrc"


def read_config(key):
    """Read config value.

    Gets the value stored in ~/.hamstall/config for the given key

    Returns:
        Any type: The value found at the key supplied

"""
    try:
        return db["options"][key]
    except KeyError:
        if key in ["Verbose", "AutoInstall"]:
            return False
        elif key == "ShellFile":
            return get_shell_file()
        elif key == "Mode":
            return "cli"
        else:
            return "Bad Value"

def change_config(key, mode, value=None):
    """Change Config Value.

    Flips a value in the config between true and false

    Args:
        key (str): Key to change the value of
        mode (str): flip or change. Determines the mode to use for changing the key's value.
        value (any): When using change, this is value to change the key to. Defaults to None.

    Returns:
        Any type: Value the key was changed to

    """
    if mode == 'flip':
        try:
            db["options"][key] = not db["options"][key]
            r = db["options"][key]
        except KeyError:  # All config values are False by default, so this should make them True.
            db["options"].update({key: True})
            r = True
    elif mode == 'change':
        try:
            db["options"][key] = value
            r = value
        except KeyError:
            db["options"].update({key: value})
            r = value
    write_db()
    return r


def vcheck():
    """Is Verbose.

    Returns:
        bool: Whether or not we are verbose

    """
    return read_config('Verbose')


def vprint(to_print):
    """Print a message only if we're verbose"""
    global verbose
    if verbose:
        if mode == "cli":
            print(to_print)
        elif mode == "gui":
            try:
                output_area.Update(to_print)
            except AttributeError:
                pass  # GUI hasn't loaded yet


def get_version(version_type):
    """Get Script Version.

    Args:
        version_type (str): prog_internal_version/file_version/version to get the program/file/end-user version

    Returns:
        str/int: Version of the type specified. Int for prog/file and str for version.

    """
    if version_type == 'prog_internal_version':
        return prog_internal_version
    elif version_type == 'file_version':
        return file_version
    elif version_type == 'version':
        return version


def lock():
    """Lock hamstall.

    Lock hamstall to prevent multiple instances of hamstall being used alongside each other

    """
    create("/tmp/hamstall-lock")
    vprint("Lock created!")


def unlock():
    """Remove hamstall lock."""
    try:
        os.remove(full("/tmp/hamstall-lock"))
    except FileNotFoundError:
        pass
    vprint("Lock removed!")


def write_db():
    """Write Database.

    Writes the database to file

    """
    try:
        with open(full("~/.hamstall/database"), "w") as dbf:
            json.dump(db, dbf)
        vprint("Database written!")
    except FileNotFoundError:
        print(json.dumps(db))
        print("The hamstall database could not be written to! Something is very wrong...")
        print("The database has been dumped to the screen; you should keep a copy of it.")
        print("You may be able to restore hamstall to working order by placing the above" +
              " database dump into a file called \"database\" in ~/.hamstall")
        print("Rest in peace if you're not in a CLI app right now...")
        unlock()
        sys.exit(3)


def name(program):
    """Get Program Name.

    Get the name of a program given the path to its archive/folder.

    Args:
        program (str): Path to program archive

    Returns:
        str: Name of program to use internally

    """
    program_internal_name = re.sub(r'.*/', '/', program)
    extension_length = len(extension(program))
    program_internal_name = program_internal_name[1:(len(program_internal_name) - extension_length)]
    return program_internal_name


def dirname(path):
    """Get Program Name for Directory

    Args:
        path (str): Path to program folder

    Returns:
        str: Name of program to user internall

    """
    prog_int_name_temp = path[0:len(path)-1]
    if prog_int_name_temp.startswith('/'):
        program_internal_name = name(prog_int_name_temp + '.tar.gz')
    else:
        program_internal_name = name('/' + prog_int_name_temp + '.tar.gz')
    return program_internal_name


def extension(program):
    """Get Extension of Program.

    Args:
        program (str): File name of program or URL/path to program.

    Returns:
        str: Extension of program

    """
    if program[-3:].lower() == '.7z':
        return program[-3:].lower()
    elif program[-4:].lower() in ['.zip', '.rar', '.git']:
        return program[-4:]
    else:
        # Default to returning the last 7 characters
        return program[-7:]


def exists(file_name):
    """Check if File Exists.

    Args:
        file_name (str): Path to file

    Returns:
        bool: Whether the file exists or not

    """
    try:
        return os.path.isfile(full(file_name))
    except FileNotFoundError:
        return False


def locked():
    """Get Lock State.

    Returns:
        bool: True if hamstall is locked. False otherwise.

    """
    return exists("/tmp/hamstall-lock")


def full(file_name):
    """Full Path.

    Converts ~'s, .'s, and ..'s to their full paths (~ to /home/username)

    Args:
        file_name (str): Path to convert

    Returns:
        str: Converted path

    """
    return os.path.abspath(os.path.expanduser(file_name))


def spaceify(file_name):
    """Add Backslashes.

    Adds backslashes before each space in a path.

    Args:
        file_name (str): Path to add backslashes to
    
    Returns:
        str: The path with backslashes

    """
    return file_name.replace(" ", "\\ ")


def replace_in_file(old, new, file_path):
    """Replace Strings in File.

    Replaces all instances of "old" with "new" in "file".
    
    Args:
        old (str): String to replace
        new (str): String to replace with
        file (str): Path to file to replace strings in

    """
    rewrite = """"""
    file_path = full(file_path)
    f = open(file_path, 'r')
    open_file = f.readlines()
    f.close()
    for l in open_file:
        rewrite += l.replace(old, new)
    written = open(file_path, 'w')
    written.write(str(rewrite))
    written.close()  # Write then close our new copy of the file
    return


def check_line(line, file_path, mode):
    """Check for Line.

    Checks to see if a line is inside of a file. Modes are:
    word: Split all lines into a list of WORDS, and check to see if the word supplied is in that list
    fuzzy: Check if the supplied line is in the file, even if it doesn't make up the whole line.

    Args:
        line (str): Line/word to look for
        file_path (str): Path to file to look for the line/word in
        mode (str): Mode to search with

    Returns:
        bool: Whether or not the line/word is in the file

    """
    f = open(full(file_path), 'r')
    open_file = f.readlines()
    f.close()
    for l in open_file:
        if mode == 'word':
            new_l = l.rstrip()
            new_l = new_l.split()
        elif mode == 'fuzzy':
            new_l = l.rstrip()
        if line in new_l:
            return True
    return False


def create(file_path):
    """Create Empty File.
    
    Args:
        file_path (str): Path to file to create

    """
    f = open(full(file_path), "w+")
    f.close()


def remove_line(line, file_path, mode):
    """Remove Line from File.

    Removes a line from a file. Uses the following modes:
    word: Removes line if supplied word is found in it (words are sets of chars seperated by spaces)
    poundword: Same as word, but line must also contain a #
    fuzzy: Removes line, matching with supplied line, even if the line being removed has more than the supplied line

    Args:
        line (str)): Line/word to remove
        file_path (str): Path to file to remove lines from
        mode (str): Mode to use to find lines to remove

    """
    rewrite = """"""
    file_path = full(file_path)
    f = open(file_path, 'r')
    open_file = f.readlines()
    f.close()
    for l in open_file:
        if mode == 'word' or mode == 'poundword':
            new_l = l.rstrip()
            new_l = new_l.split()
        elif mode == 'fuzzy':
            new_l = l.rstrip()
        if line in new_l:
            if not ('#' in new_l) and mode == 'poundword':
                rewrite += l
            else:
                pass
        else:
            rewrite += l
    written = open(file_path, 'w')
    written.write(str(rewrite))
    written.close()  # Write then close our new copy of the file
    return


def add_line(line, file_path):
    """Adds Line to a File."""
    file_path = full(file_path)
    f = open(file_path, 'a')
    f.write(line)
    f.close()


def char_check(name):
    """Check Chars.

    Checks if a string contains a # or a space.

    Returns:
        bool: True if line contains space or #; False otherwise

    """
    return ' ' in name or '#' in name


"""
Database structure

{
    "options" : {
        "Verbose" : False,
        "AutoInstall" : False
    }
    "version" : {
        "file_version" : file_version,
        "prog_internal_version" : prog_internal_version,
        "branch" : "master"
    }
    "programs" : {
        "package" : {
            "git_installed": False,
            "post_upgrade_script": None,
            "desktops" : [
                "desktop_file_name"
            ]
        }
    }
}
"""


def get_db(db_check=""):
    """Get Database.

    Returns:
        dict: Database. {} if database fails to be read or found on disk.

    """
    try:
        with open(full("~/.hamstall/database")) as f:
            db = json.load(f)
    except FileNotFoundError:
        db = {}
    except json.decoder.JSONDecodeError:
        db = {}
        print("We're upgrading from an extremely old version of hamstall!")
        print("Using empty database file...")
    return db


db = get_db()
verbose = vcheck()
mode = read_config("Mode")

install_bar = None  # Holds a progress bar if we're in a GUI
output_area = None  # Holds a text area if we're in a GUI (for displaying status messages)

if db != {}:
    vprint("Database loaded successfully!")

try:
    branch = db["version"]["branch"]
except KeyError:
    branch = "master"
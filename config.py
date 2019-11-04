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

###VERSIONS###

version = "1.2.0 beta"
prog_internal_version = 15
file_version = 5

#############


def get_shell_file():
    vprint("Auto-detecting shell")
    shell = os.environ["SHELL"]
    if "bash" in shell:
        return ".bashrc"
    elif "zsh" in shell:
        return ".zshrc"
    else:
        vprint("Couldn't auto-detect shell environment! Defaulting to bash...")
        return ".bashrc"


def read_config(key):
    """Gets the value stored in ~/.hamstall/config for the given key"""
    try:
        return db["options"][key]
    except KeyError:
        if key in ["Verbose", "AutoInstall"]:
            return False
        elif key == "ShellFile":
            return get_shell_file()
        else:
            print("Attempted to read a config value that doesn't exist!")
            sys.exit(2)


def change_config(key, mode, value=None):
    """Flips a value in the config between true and false"""
    if mode == 'flip':
        try:
            db["options"][key] = not (db["options"][key])
            return db["options"][key]
        except KeyError:  # All config values are False by default, so this should make them True.
            db["options"].update({key: True})
            return True
    elif mode == 'change':
        try:
            db["options"][key] = value
            return value
        except KeyError:
            db["options"].update({key: value})
            return value
    write_db()


def vcheck():
    """Returns if Verbose=True in the config"""
    return read_config('Verbose')


def vprint(to_print):
    """Print a message only if Verbose=True"""
    global verbose
    if verbose:
        print(to_print)


def get_version(version_type):
    """Return version numbers of scripts
    prog_internal_version - Version as used by GitHub for updating
    file_version - Version that should match with the .hamstall directory
    version - Version displayed to end user.
    """
    if version_type == 'prog_internal_version':
        return prog_internal_version
    elif version_type == 'file_version':
        return file_version
    elif version_type == 'version':
        return version


def lock():
    create("/tmp/hamstall-lock")
    vprint("Lock created!")


def unlock():
    try:
        os.remove(full("/tmp/hamstall-lock"))
    except FileNotFoundError:
        pass
    vprint("Lock removed!")


def locked():
    return os.path.isfile(full("/tmp/hamstall-lock"))


def write_db():
    try:
        with open(full("~/.hamstall/database"), "w") as dbf:
            json.dump(db, dbf)
    except FileNotFoundError:
        print(json.dumps(db))
        print("The hamstall database could not be written to! Something is very wrong...")
        print("The database has been dumped to the screen; you should keep a copy of it.")
        print("You may be able to restore hamstall to working order by placing the above" +
              " database dump into a file called \"database\" in ~/.hamstall")
        sys.exit(3)


def name(program):
    """Returns name of program"""
    program_internal_name = re.sub(r'.*/', '/', program)
    extension_length = len(extension(program))  # Get extension length
    program_internal_name = program_internal_name[1:(len(program_internal_name) - extension_length)]
    return program_internal_name


def extension(program):
    """Returns program extension"""
    if program[-3:].lower() == '.7z':
        return program[-3:].lower()
    elif program[-4:].lower() in ['.zip', '.rar', '.git']:
        return program[-4:]
    else:
        # Default to returning the last 7 characters
        return program[-7:]


def exists(file_name):
    """Returns if file exists"""
    try:
        return os.path.isfile(full(file_name))
    except FileNotFoundError:
        return False


def full(file_name):
    """Returns program with corrected ~ to /home/user"""
    return os.path.abspath(os.path.expanduser(file_name))


def spaceify(file_name):
    """Adds a backslash before every space for bash"""
    char_list = []
    for c in file_name:
        if c == ' ':
            char_list.append('\\')
        char_list.append(c)
    return_string = ''
    for i in char_list:
        return_string = return_string + i
    return return_string


def check_line(line, file_path, mode):
    """Returns if a line exists in a file
    word - Turns each line into a list where each item is separated by
    spaces, then checks each list to see if it finds the word.
    fuzzy - Checks if the provided string is in the line anywhere."""
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
    """Creates an empty file"""
    f = open(full(file_path), "w+")
    f.close()


def remove_line(line, file_path, mode):
    """Removes a line from a file
    word - Turns each line into a list where each item is separated by
    spaces, then checks each list to see if it finds the word.
    poundword - Same as word but also checks if there is a #.
    fuzzy - Checks if the provided string is in the line anywhere."""
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
    """Adds a line to a file"""
    file_path = full(file_path)
    f = open(file_path, 'a')
    f.write(line)
    f.close()
    return


def char_check(name):
    """Returns if the provided string contains a space or #"""
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
            "desktops" : [
                "desktop_file_name"
            ]
        }
    }
}
"""


def get_db():
    try:
        with open(full("~/.hamstall/database")) as f:
            db = json.load(f)
    except FileNotFoundError:
        db = {}
    except json.decoder.JSONDecodeError:
        db_check = ""
        while not (db_check in ['y', 'n']):
            db_check = input("Database is corrupt, unreadable, or in a bad format! "
                            "Are you upgrading from a version of hamstall earlier than 1.1.0? [y/n]")
        if db_check == 'y':
            db = {}
        else:
            print("Please check your database! Something is horrendously wrong...")
            sys.exit(1)
    return db


db = get_db()
verbose = vcheck()

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

import file

###VERSIONS###

version = "1.1.0"
prog_internal_version = 5
file_version = 2

#############


def read_config(key):
    """Gets the value stored in ~/.hamstall/config for the given key"""
    try:
        return file.db["options"][key]
    except KeyError:
        if key == "Verbose":
            return False
        else:
            print("Attempted to read a config value that doesn't exist!")
            sys.exit(2)


def change_config(key, mode, value=None):
    """Flips a value in the config between true and false"""
    if mode == 'flip':
        file.db["options"][key] = not (file.db["options"][key])
    elif mode == 'change':
        file.db["options"][key] = value
    file.write_db()


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
    file.create("/tmp/hamstall-lock")
    vprint("Lock created!")


def unlock():
    try:
        os.remove(file.full("/tmp/hamstall-lock"))
    except FileNotFoundError:
        pass
    vprint("Lock removed!")


def locked():
    return os.path.isfile(file.full("/tmp/hamstall-lock"))


verbose = vcheck()

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

import re

import file


def read_config(key):
    """Gets the value stored in ~/.hamstall/config for the given key"""
    try:
        f = open(file.full('~/.hamstall/config'), 'r')
    except FileNotFoundError:
        return False
    open_file = f.readlines()
    f.close()
    line_num = 0
    for l in open_file:
        if key in l:
            open_line = open_file[line_num]
            open_line = re.sub(r'.*=', '=', open_line)
            if 'False' in open_line:
                return False
            elif 'True' in open_line:
                return True
            else:
                to_return = str(open_line[1:])
                return to_return.rstrip()
        else:
            line_num += 1


def change_config(key, mode, value):
    """Flips a value in the config between true and false"""
    original = read_config(key)
    if mode == 'flip':
        to_remove = key + '=' + str(original)
        to_add = key + '=' + str(not(original)) + '\n'
        file.remove_line(to_remove, "~/.hamstall/config", 'fuzzy')
        file.add_line(to_add, '~/.hamstall/config')
    elif mode == 'change':
        file.remove_line(key, "~/.hamstall.config", 'fuzzy')
        file.add_line(key + '=' + value, "~/.hamstall/config")


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
        return 5
    elif version_type == 'file_version':
        return 1
    elif version_type == 'version':
        return '1.1.0'


verbose = vcheck()
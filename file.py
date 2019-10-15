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
import os


def name(program):
    """Returns name of program"""
    program_internal_name = re.sub(r'.*/', '/', program)
    extension_length = len(extension(program)) #Get extension length
    program_internal_name = program_internal_name[1:(len(program_internal_name)-extension_length)]
    return program_internal_name


def extension(program):
    """Returns program extension"""
    if program[((len(program))-3):len(program)].lower() == '.7z':
        return program[((len(program))-3):len(program)].lower()
    elif program[((len(program))-4):len(program)].lower() == '.zip' or program[((len(program))-4):len(program)].lower() == '.rar':
        return program[((len(program))-4):len(program)]
    else:
        # Returns the last 7 characters of the provided file name.
        return program[((len(program))-7):len(program)]


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
            if not('#' in new_l) and mode == 'poundword':
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
    for c in name:
        if c == ' ' or c == '#':
            return True
    return False

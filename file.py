import re
import os

def name(program):  # Get name of program as it's stored
    # Remove a lot of stuff (I'm going to pretend I know how re.sub works, but this gives you "/filename.extension"
    program_internal_name = re.sub(r'.*/', '/', program)
    # Get length of our extension
    extension_length = len(extension(program))
    # Some Python formatting that turns the path into "archive name"
    program_internal_name = program_internal_name[1:(len(program_internal_name)-extension_length)]
    return program_internal_name  # Return internal name (name of archive)

def extension(program):
    # Only supported 4 char file extension
    if program[((len(program))-4):len(program)].lower() == '.zip':
        return program[((len(program))-4):len(program)]
    else:
        # Returns the last 7 characters of the provided file name.
        return program[((len(program))-7):len(program)]

def exists(file_name):
    try:
        # Returns True if the given file exists. Otherwise false.
        return os.path.isfile(full(file_name))
    except FileNotFoundError:
        return False

def full(file_name):
    # Returns path specified with ~ corrected to /home/USERNAME
    return os.path.expanduser(file_name)

# Adds \ before every space because bash doesn't like spaces in file names
def spaceify(file_name):
    char_list = []
    for c in file_name:
        if c == ' ':
            char_list.append('\\')
        char_list.append(c)
    return_string = ''
    for i in char_list:
        return_string = return_string + i
    return return_string

def check_line(line, file_path, mode):  # Checks to see if a line exists in a file
    f = open(full(file_path), 'r')
    open_file = f.readlines()
    f.close()
    for l in open_file:
        if mode == 'word':
            new_l = l.rstrip()
            # Turns each line into a list of "words" (groups of characters seperated by spaces)
            new_l = new_l.split()
        elif mode == 'fuzzy':
            new_l = l.rstrip()  # Removes \n from each line
        if line in new_l:
            return True
    return False

def create(file_path):
    f = open(full(file_path), "w+")
    f.close()  # Creates a file

def remove_line(line, file_path, mode):  # Removes a line from a file
    rewrite = ''''''
    file_path = full(file_path)
    f = open(file_path, 'r')  # Open file
    open_file = f.readlines()  # Copy file to program
    f.close()  # Close file
    for l in open_file:
        if mode == 'word' or mode == 'poundword':
            new_l = l.rstrip()
            new_l = new_l.split()
        elif mode == 'fuzzy':
            new_l = l.rstrip()
        if line in new_l:
            if not(mode == 'poundword' and '#' in new_l) and not(mode == 'fuzzy' or mode == 'word'):
                rewrite += l
        else:
            rewrite += l  # Loop that removes line that needs removal from the copy of the file
    written = open(file_path, 'w')
    written.write(str(rewrite))
    written.close()  # Write then close our new copy of the file
    return

def add_line(line, file_path):  # Add a line to a file
    file_path = full(file_path)
    f = open(file_path, 'a')
    f.write(line)
    f.close()
    return

def char_check(name):  # Checks if there is a space in the name of something
    for c in name:
        if c == ' ' or c == '#':
            return True
    return False
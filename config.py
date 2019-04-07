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

def change_config(key):
    """Flips a value in the config between true and false"""
    original = read_config(key)
    to_remove = key + '=' + str(original)
    to_add = key + '=' + str(not(original)) + '\n'
    file.remove_line(to_remove, "~/.hamstall/config", 'fuzzy')
    file.add_line(to_add, '~/.hamstall/config')

def vcheck():
    """Returns if Verbose=True in the config"""
    return(read_config('Verbose'))

def vprint(to_print):
    """Print a message only if Verbose=True"""
    global verbose
    if verbose:
        print(to_print)

def get_version(type):
    """Return version numbers of scripts
    prog_internal_version - Version as used by GitHub for updating
    file_version - Version that should match with the .hamstall directory
    version - Version displayed to end user.
    """
    if type == 'prog_internal_version':
        return 3
    elif type == 'file_version':
        return 1
    elif type == 'version':
        return '1.0.0c'

verbose = vcheck()
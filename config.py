import file
import re

def readConfig(key):  # Read a specified value in the full config.
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

def changeConfig(key):  # Flip a value in the config between true and false
    original = readConfig(key)
    to_remove = key + '=' + str(original)
    to_add = key + '=' + str(not(original)) + '\n'
    file.remove_line(to_remove, "~/.hamstall/config", 'fuzzy')
    file.add_line(to_add, '~/.hamstall/config')

def vcheck():
    return(readConfig('Verbose'))

def vprint(to_print): #If we're verbose, print the supplied message
    global verbose
    if verbose:
        print(to_print)

verbose = vcheck()
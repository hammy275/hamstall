#!/usr/bin/python3

#Hamstall
#Should be ready for an actual environment pretty soon. Will still be in beta so I have an excuse to make changes without worrying about backwards compatability though.

import os
import argparse
from pathlib import Path
import sys
import re
import getpass
from shutil import copyfile
from shutil import rmtree #Imports
from shutil import move
try:
    import requests
except:
    print('Please install requests! The command "pip3 install requests" or "python3 -m pip install requests" on Linux systems should do the job!')
    sys.exit()

###HAMSTALL VERSIONS###
prog_version_internal = 1
file_version = 1 #These are used internally for updating and for converting older hamstalls up.
version = "0.9" #String in case I ever decide to add letters. Will only be displayed to end users.



def get_input(question, options, default): #Like input but with some checking
    answer = "This is a string. There are many others like it, but this one is mine." #Set answer to something
    while answer not in options and answer != "":
        answer = input(question)
        answer = answer.lower() #Loop ask question while the answer is invalid or not blank
    if answer == "":
        return default #If answer is blank return default answer
    else:
        return answer #Return answer if it isn't the default answer


def vprint(to_print): #If we're verbose, print the supplied message
    if config.vcheck():
        print(to_print)

class config:
    def readConfig(key): #Read a specified value in the config.
        f = open(file.full('~/.hamstall/config'), 'r')
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
    
    def changeConfig(key): #Flip a value in the config between true and false
        original = config.readConfig(key)
        to_remove = key + '=' + str(original)
        to_add = key + '=' + str(not(original)) + '\n'
        file.remove_line(to_remove,"~/.hamstall/config", 'fuzzy')
        file.add_line(to_add, '~/.hamstall/config')

    def vcheck():
        return(config.readConfig('Verbose'))
    

class file:
    def name(program): #Get name of program as it's stored
        program_internal_name = re.sub(r'.*/', '/', program) #Remove a lot of stuff (I'm going to pretend I know how re.sub works, but this gives you "/filename.extension"
        extension_length = len(file.extension(program)) #Get length of our extension
        program_internal_name = program_internal_name[1:(len(program_internal_name)-extension_length)] #Some Python formatting that turns the path into "archive name"
        return program_internal_name #Return internal name (name of archive)

    def extension(program):
        if program[((len(program))-4):len(program)].lower() == '.zip': #Only supported 4 char file extension
            return program[((len(program))-4):len(program)]
        else:
            return program[((len(program))-7):len(program)] #Returns the last 7 characters of the provided file name.

    def exists(file_name):
        try:
            return os.path.isfile(file.full(file_name)) #Returns True if the given file exists. Otherwise false.
        except FileNotFoundError:
            return False
    def full(file_name):
        return os.path.expanduser(file_name) #Returns path specified with ~ corrected to /home/USERNAME
    
    def spaceify(file_name): #Adds \ before every space (for command purposes)
        char_list = []
        for c in file_name:
            if c == ' ':
                char_list.append('\\')
            char_list.append(c)
        return_string = ''
        for i in char_list:
            return_string = return_string + i
        return return_string
    
    def check_line(line,file_path, mode): #Checks to see if a line exists in a file
        f = open(file.full(file_path), 'r')
        open_file = f.readlines()
        f.close()
        line_num = 0
        for l in open_file:
            if mode == 'word':
                new_l = l.rstrip()
                new_l = new_l.split()
            elif mode == 'fuzzy':
                new_l = l.rstrip()
            if line in new_l:
                return True
            else:
                line_num += 1
        return False
        

    def create(file_path):
        f=open(file.full(file_path), "w+")
        f.close() #Creates a file

    def remove_line(line, file_path, mode): #Removes a line from a file
        file_path = file.full(file_path)
        f = open(file_path, 'r') #Open file
        open_file = f.readlines() #Copy file to program
        f.close() #Close file

        rewrite = ''''''

        for l in open_file:
            if mode == 'word':
                new_l = l.rstrip()
                new_l = new_l.split()
            elif mode == 'fuzzy':
                new_l = l.rstrip()
            if line in new_l:
                vprint('Line removed!')
            else:
                rewrite += l #Loop that removes line that needs removal from the copy of the file
        written = open(file_path, 'w')
        written.write(str(rewrite))
        written.close() #Write then close our new copy of the file
        return
        
    def add_line(line, file_path): #Add a line to a file
        file_path = file.full(file_path)
        f = open(file_path, 'a')
        f.write(line)
        f.close()
        return

    def space_check(name): #Checks if there is a space in the name of something
        for c in name:
            if c == ' ':
                return True
        return False


class hamstall:
    def binlink(program_internal_name):
        yn = get_input('Would you like to be able to run certain files in the installed archive directly from its directory? [y/N]?', ['y', 'n'], 'n')
        while yn == 'y':
            files = os.listdir(file.full('~/.hamstall/bin/' + program_internal_name + '/'))
            print(' '.join(files))
            file_chosen = 'Cool fact. This line was originally written on line 163.'
            while file_chosen not in files:
                file_chosen = input('Please enter a file listed above. If you would like to cancel, press CTRL+C: ')
            vprint("Adding alias to hamstall database")
            file.add_line(file_chosen + ' # ' + program_internal_name + '\n', '~/.hamstall/database') #Files in ext4 can't have a / in them (because directories) so we can exploit that here
            line_to_add = 'alias ' + file_chosen + "='cd " + file.full('~/.hamstall/bin/') + program_internal_name + '/ && ./' + file_chosen + "' # " + program_internal_name + "\n"
            vprint("Adding alias to bashrc")
            file.add_line(line_to_add, '~/.bashrc')
            yn = get_input('Would you like to continue adding files to be run directly? [y/N]', ['y', 'n'], 'n')
        else:
            sys.exit()

    def update():
        global prog_version_internal
        vprint("Checking version on GitHub")
        version_url = "https://raw.githubusercontent.com/hammy3502/hamstall/master/version"
        version_raw = requests.get(version_url)
        version = version_raw.text
        counter = 0
        for c in version:
            if c == '.':
                spot = counter + 1
            else:
                counter += 1
        final_version = int(version[spot:])
        vprint('Installed internal version: ' + str(prog_version_internal))
        vprint('Version on GitHub: ' + str(final_version))
        if final_version > prog_version_internal:
            print("An update has been found! Installing...")
            vprint("Downloading new hamstall...")
            r = requests.get("https://raw.githubusercontent.com/hammy3502/hamstall/master/hamstall.py")
            vprint("Replacing old hamstall with new version")
            os.remove(file.full("~/.hamstall/hamstall.py"))
            os.remove(file.full("~/.hamstall/version"))
            open(file.full("~/.hamstall/hamstall.py"), 'wb').write(r.content)
            open(file.full('~/.hamstall/version'), 'wb').write(version_raw.content)
            ###hamstall directory conversion code here when needed###
            sys.exit()
        else:
            print("No update found!")
            sys.exit()
        

    def erase():
        if not(file.exists(file.full("~/.hamstall/hamstall.py"))):
            print("hamstall not detected so not removed!")
            sys.exit()
        vprint('Removing added lines from bashrc')
        file_to_open = file.full("~/.hamstall/database")
        f = open(file_to_open, 'r')
        for l in f:
            to_remove = l.rstrip()
            file.remove_line(to_remove, '~/.bashrc', 'word')
        vprint('Removing hamstall command alias')
        to_be_removed = "alias hamstall='python3 ~/.hamstall/hamstall.py'"
        file.remove_line(to_be_removed, '~/.bashrc', 'fuzzy')
        vprint('Removing hamstall directory')
        rmtree(file.full('~/.hamstall'))
        print("Hamstall has been removed from your system.")
        print('Please restart your terminal.')
        input('Press return to exit...')

    def firstTimeSetup():
        global prog_version_internal
        global file_version #Yes globals aren't the best, but this just makes life easier
        if file.exists(file.full('~/.hamstall/hamstall.py')):
            print('Please don\'t run first time setup on an already installed system!')
            sys.exit()
        print('Installing hamstall to your system...')
        os.mkdir(file.full("~/.hamstall"))
        os.mkdir(file.full("~/.hamstall/temp"))
        os.mkdir(file.full("~/.hamstall/bin"))
        file.create("~/.hamstall/database")
        file.create("~/.hamstall/config")
        file.add_line("Verbose=False\n","~/.hamstall/config") #Write verbosity line to config
        copyfile(os.path.realpath(__file__), file.full('~/.hamstall/hamstall.py')) #Copy hamstall to hamstall directory
        file.add_line("alias hamstall='python3 ~/.hamstall/hamstall.py'\n", "~/.bashrc")
        print('First time setup complete!')
        print('Please run the command "source ~/.bashrc" or restart your terminal.')
        print('Afterwards, you may begin using hamstall with the hamstall command!')

    def verboseToggle():
        config.changeConfig('Verbose')

    def install(program):
        program_internal_name = file.name(program)
        if file.space_check(program_internal_name):
            print("Error! Archive name contains a space!")
            sys.exit()
        vprint("Removing old temp directory (if it exists!)")
        try:
            rmtree(file.full("~/.hamstall/temp/")) #Removes temp directory (used during installs)
        except:
            vprint("Temp directory did not exist!")
        vprint("Creating new temp directory")
        os.mkdir(file.full("~/.hamstall/temp")) #Creates temp directory for extracting archive
        vprint("Extracting archive to temp directory")
        file_extension = file.extension(program)
        program = file.spaceify(program)
        if config.vcheck():
            if file_extension == '.tar.gz' or file_extension == '.tar.xz':
                vflag = 'v'
            elif file_extension == '.zip':
                vflag = ''
        else:
            if file_extension == '.tar.gz' or file_extension == '.tar.xz':
                vflag = ''
            elif file_extension == '.zip':
                vflag = '-qq'
        if file_extension == '.tar.gz' or file_extension == '.tar.xz':
            command_to_go = "tar " + vflag + "xf " + program + " -C ~/.hamstall/temp/"
        elif file_extension == '.zip':
            command_to_go = 'unzip ' + vflag + ' ' + program + ' -d ~/.hamstall/temp/'
        else:
            print('Error! File type not supported!')
            sys.exit() #Creates the command to run to extract the archive
        vprint('File type detected: ' + file_extension)
        os.system(command_to_go) #Extracts program archive
        vprint('Checking for folder in folder')
        if os.path.isdir(file.full('~/.hamstall/temp/' + program_internal_name + '/')):
            vprint('Folder in folder detected! Using that directory instead...')
            source = file.full('~/.hamstall/temp/' + program_internal_name + '/')
            dest = file.full('~/.hamstall/bin/')
        else:
            vprint('Folder in folder not detected!')
            source_r = file.full("~/.hamstall/temp")
            dest_r = file.full("~/.hamstall/" + program_internal_name)
            os.rename(source_r, dest_r) #Renames temp folder to program name before move
            source = file.full('~/.hamstall/' + program_internal_name)
            dest = file.full('~/.hamstall/bin/')
        vprint("Moving program to directory")
        move(source,dest)
        vprint("Adding program to hamstall list of programs")
        file.add_line(program_internal_name + '\n',"~/.hamstall/database")
        ###PATH CODE###
        yn = get_input('Would you like to add the program to your PATH? [Y/n]', ['y', 'n'], 'y')
        if yn == 'y':
            vprint('Adding program to PATH')
            line_to_write = "export PATH=$PATH:~/.hamstall/bin/" + program_internal_name + ' # ' + program_internal_name + '\n'
            file.add_line(line_to_write,"~/.bashrc")
        hamstall.binlink(program_internal_name)
        print("Install completed!")
        sys.exit()
    
    def dirinstall(program_path, program_internal_name):
        vprint("Moving folder to hamstall destination")
        move(program_path, file.full("~/.hamstall/bin/"))
        vprint("Adding program to hamstall list of programs")
        file.add_line(program_internal_name + '\n',"~/.hamstall/database")
        yn = get_input('Would you like to add the program to your PATH? [Y/n]', ['y', 'n'], 'y')
        if yn == y:
            vprint("Adding program to PATH")
            line_to_write = "export PATH=$PATH:~/.hamstall/bin/" + program_internal_name + ' # ' + program_internal_name + '\n'
            file.add_line(line_to_write,"~/.bashrc")
        hamstall.binlink(program_internal_name)
        print("Install completed!")
        sys.exit()

    def uninstall(program):
        vprint("Removing program")
        rmtree(file.full("~/.hamstall/bin/" + program + '/')) #Removes program
        vprint("Removing program from PATH")
        file.remove_line(program,"~/.bashrc", 'word')
        vprint("Removing program from hamstall list of programs")
        file.remove_line(program,"~/.hamstall/database", 'word')
        print("Uninstall complete!")

    def listPrograms():
        f = open(file.full('~/.hamstall/database'), 'r')
        open_file = f.readlines()
        f.close()
        for l in open_file:
            newl = l.rstrip()
            print(newl)
        sys.exit()



###############Argument Parsing###############

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('-i', "--install", help="Install a .tar.gz, .tar.xz, or .zip")
group.add_argument('-d', "--dirinstall", help="Install a directory")
group.add_argument('-r', "--remove", help="Remove an insatlled program")
group.add_argument('-l', "--list", help="List installed programs", action="store_true")
group.add_argument('-f', "--first", help="Run first time setup", action="store_true")
group.add_argument('-e', "--erase", help="Delete hamstall from your system", action="store_true")
group.add_argument('-v', "--verbose", help="Toggle verbose mode", action="store_true")
group.add_argument('-u', '--update', help="Update hamstall if an update is available", action="store_true")
args = parser.parse_args() #Parser stuff

username = getpass.getuser()
if username == 'root':
    print('Note: Running as root user will install programs for the root user to use!')

if args.install != None:
    to_install = args.install #to_install from the argument
    does_archive_exist = file.exists(to_install)
    if does_archive_exist == False:
        print("File to install does not exist!")
        sys.exit()
    program_internal_name = file.name(to_install) #Get the internal name (trim off everything except the file name before the .tar.gz/.tar.xz/.zip
    file_check = file.check_line(program_internal_name, "~/.hamstall/database", 'word') #Checks to see if the file path for the program's uninstall script exists
    if file_check: #Ask to reinstall program
        reinstall = get_input("Application already exists! Would you like to reinstall? [y/N]", ["y", "n"], "n") #Ask to reinstall
        if reinstall == "y":
            hamstall.uninstall(program_internal_name)
            hamstall.install(to_install) #Reinstall
        else:
            print("Reinstall cancelled.")
            sys.exit()
    else:
        hamstall.install(to_install) #No reinstall needed to be asked, install program

if args.dirinstall != None:
    to_install = args.dirinstall
    if os.path.isdir(to_install) == False:
        print("Folder to install does not exist!")
        sys.exit()
    if to_install[len(to_install) - 1] != '/':
        print("Please make sure the directory ends with a / !")
        sys.exit()
    progintnametemp = to_install[0:len(to_install)-1]
    program_internal_name = file.name(progintnametemp + '.tar.gz') #Add .tar.gz to make the original function work (a hackey solution I know)
    file_check = file.check_line(program_internal_name, "~/.hamstall/database", 'word')
    if file_check:
        reinstall = get_input("Application already exists! Would you like to reinstall? [y/N]", ["y", "n"], "n")
        if reinstall == 'y':
            hamstall.uninstall(program_internal_name)
            hamstall.dirinstall(to_install, program_internal_name)
        else:
            print("Reinstall cancelled.")
            sys.exit()
    else:
        hamstall.dirinstall(to_install, program_internal_name)


elif args.remove != None:
    to_uninstall = args.remove
    if file.check_line(to_uninstall, "~/.hamstall/database", 'word'): #If uninstall script exists
        hamstall.uninstall(to_uninstall) #Uninstall program
    else:
        print("Program does not exist!") #Program doesn't exist
    sys.exit()

elif args.list:
    hamstall.listPrograms() #List programs installed
    sys.exit()

elif args.first:
    hamstall.firstTimeSetup() #First time setup
    sys.exit()

elif args.erase:
    erase_sure = get_input("Are you sure you would like to remove hamstall from your system? [y/N]", ['y', 'n'], 'n')
    if erase_sure == 'y':
        erase_really_sure = get_input('Are you absolutely sure? This will remove all programs installed with hamstall! [y/N]', ['y', 'n'], 'n')
        if erase_really_sure == 'y':
            hamstall.erase() #Remove hamstall from the system
        else:
            print('Erase cancelled.')
    else:
        print('Erase cancelled.')
    sys.exit()

elif args.verbose: #Verbose toggle
    hamstall.verboseToggle()

elif args.update:
    hamstall.update()

else:
    #About hamstall
    print('\nhamstall. A Python package manager to manage archives.')
    print("Written by: hammy3502\n")
    print('hamstall version: ' + version)
    print('Internal version code: ' + str(file_version) + "." + str(prog_version_internal) + "\n")
    if file.exists('~/.hamstall/hamstall.py'):
        print('For help, type hamstall -h\n')
    else:
        yn = get_input('hamstall is not installed on your system. Would you like to install it? [Y/n]', ['y','n'], 'y')
        if yn == 'y':
            hamstall.firstTimeSetup()
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
                line_num += 1 
    
    def changeConfig(key): #Flip a value in the config between true and false
        original = config.readConfig(key)
        to_remove = key + '=' + str(original)
        to_add = key + '=' + str(not(original)) + '\n'
        file.remove_line(to_remove,"~/.hamstall/config")
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
    
    def check_line(line,file_path): #Checks to see if a line exists in a file
        f = open(file.full(file_path), 'r')
        open_file = f.readlines()
        f.close()
        line_num = 0
        for l in open_file:
            if line in l:
                open_line = open_file[line_num]
                open_line = re.sub(r'.*=', '=', open_line)
                return True
            else:
                line_num += 1
        return False
        

    def create(file_path):
        f=open(file.full(file_path), "w+")
        f.close() #Creates a file

    def remove_line(line, file_path): #Removes a line from a file
        file_path = file.full(file_path)
        f = open(file_path, 'r') #Open file
        open_file = f.readlines() #Copy file to program
        f.close() #Close file

        rewrite = ''''''

        for l in open_file:
            if l.rstrip() == line or line in l:
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
    def erase():
        if not(file.exists(file.full("~/.hamstall/hamstall.py"))):
            print("hamstall not detected so not removed!")
            sys.exit()
        vprint('Removing PATH lines from bashrc')
        file_to_open = file.full("~/.hamstall/database")
        f = open(file_to_open, 'r')
        for l in f:
            to_be_removed = ("export PATH=$PATH:~/.hamstall/bin/" + l).rstrip() #Line to be removed
            file.remove_line(to_be_removed, '~/.bashrc') #Remove all programs from bashrc
        vprint('Removing hamstall command alias')
        to_be_removed = "alias hamstall='python3 ~/.hamstall/hamstall.py'"
        file.remove_line(to_be_removed, '~/.bashrc')
        vprint('Removing hamstall directory')
        rmtree(file.full('~/.hamstall'))
        print("Hamstall has been removed from your system.")
        print('Please restart your terminal.')
        input('Press return to exit...')

    def firstTimeSetup():
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
        #os.remove(os.path.realpath(__file__))
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
            print('Error! File type ' + file_extension + ' not supported!')
            return #Creates the command to run to extract the archive
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
        vprint('Adding program to PATH')
        line_to_write = "export PATH=$PATH:~/.hamstall/bin/" + file.spaceify(program_internal_name) + '\n'
        file.add_line(line_to_write,"~/.bashrc")
        ###/PATH CODE###
        print("Install Completed!")

    def uninstall(program):
        vprint("Removing program")
        rmtree(file.full("~/.hamstall/bin/" + program + '/')) #Removes program
        vprint("Removing program from PATH")
        to_be_removed = "export PATH=$PATH:~/.hamstall/bin/" + program
        file.remove_line(to_be_removed,"~/.bashrc")
        vprint("Removing program from hamstall list of programs")
        file.remove_line(program,"~/.hamstall/database")
        print("Uninstall complete!")

    def listPrograms():
        f = open(file.full('~/.hamstall/database'), 'r')
        open_file = f.readlines()
        f.close()
        for l in open_file:
            newl = l.rstrip()
            print(newl)
        sys.exit()



###############Argument Parsing Below###############

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('-i', "--install", help="Install a .tar.gz, .tar.xz, or .zip")
group.add_argument('-r', "--remove", help="Remove an insatlled program")
group.add_argument('-l', "--list", help="List installed programs", action="store_true")
group.add_argument('-f', "--first", help="Run first time setup", action="store_true")
group.add_argument('-e', "--erase", help="Delete hamstall from your system", action="store_true")
group.add_argument('-v', "--verbose", help="Toggle verbose mode", action="store_true")
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
    file_check = file.exists("~/.hamstall/uninstall_scripts/" + program_internal_name) #Checks to see if the file path for the program's uninstall script exists
    if file_check == True: #Uninstall script exists, ask to reinstall program
        reinstall = get_input("Application already exists! Would you like to reinstall? [y/N]", ["y", "n"], "n") #Ask to reinstall
        if reinstall == "y":
            hamstall.uninstall(program_internal_name)
            hamstall.install(to_install) #Reinstall
        else:
            print("Reinstall cancelled.")
    else:
        hamstall.install(to_install) #No reinstall needed to be asked, install program

elif args.remove != None:
    to_uninstall = args.remove
    if file.check_line(to_uninstall, "~/.hamstall/database"): #If uninstall script exists
        hamstall.uninstall(to_uninstall) #Uninstall program
    else:
        print("Program does not exist!") #Program doesn't exist

elif args.list:
    hamstall.listPrograms() #List programs installed

elif args.first:
    hamstall.firstTimeSetup() #First time setup

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

elif args.verbose: #Verbose toggle
    hamstall.verboseToggle()


else:
    username = getpass.getuser()
    if file.exists('/home/' + username + '/.hamstall/hamstall.py'):
        print('No flag specified! Use -h or --help for help!')
    else:
        yn = get_input('hamstall is not on your system. Would you like to install it? [Y/n]', ['y','n'], 'y')
        if yn == 'y':
            hamstall.firstTimeSetup()
#!/usr/bin/python3

#Hamstall
#Should be ready for an actual environment pretty soon. Will still be in beta so I have an excuse to make changes without worrying about backwards compatability though.

import os
import argparse
from pathlib import Path
import sys
import re #Importing time

def get_input(question, options, default): #Like input but with some checking
    answer = "-1" #Set answer to something
    while answer not in options and answer != "":
        answer = input(question)
        answer = answer.lower() #Loop ask question while the answer is invalid or not blank
    if answer == "":
        return default #If answer is blank return default answer
    else:
        return answer #Return answer if it isn't the default answer

def vcheck(): #Check if we're verbose
    f = open(file.full('~/.hamstall/verbose'), 'r')
    open_file = f.readlines()
    f.close()
    if 'True' in open_file[0]: #Are we verbose?
        return True
    else:
        return False

def vprint(to_print): #If we're verbose, print the supplied message
    if vcheck():
        print(to_print)



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
        return os.path.isfile(file.full(file_name)) #Returns True if the given file exists. Otherwise false.

    def full(file_name):
        return os.path.expanduser(file_name)


class hamstall:
    def erase():
        vprint('Removing PATH lines from bashrc')
        for program in os.listdir(file.full('~/.hamstall/uninstall_scripts/')):
            hamstall.removeFromPath(program) #Remove all programs from bashrc
        os.system('rm -rf ~/.hamstall')
        print("Hamstall has been removed from your system.")
        print('If you would like to use hamstall again, please use the Python file.')
        print('Otherwise, you may remove this python script from your system.')
        input('Press return to exit...')

    def firstTimeSetup():
        print('Installing hamstall to your system...')
        os.system("mkdir ~/.hamstall")
        os.system("mkdir ~/.hamstall/temp")
        os.system("mkdir ~/.hamstall/bin")
        os.system("mkdir ~/.hamstall/uninstall_scripts") #Create some directories
        os.system("echo False >> ~/.hamstall/verbose")
        print('First time setup complete!')

    def install(program):
        program_internal_name = file.name(program)
        vprint("Removing old temp directory (if it exists!)")
        os.system("rm -rf ~/.hamstall/temp") #Removes temp directory (used during installs)
        vprint("Creating new temp directory")
        os.system("mkdir ~/.hamstall/temp") #Creates temp directory for extracting archive
        vprint("Extracting archive to temp directory")
        file_extension = file.extension(program)
        if vcheck():
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
            return
        vprint('File type detected: ' + file_extension)
        os.system(command_to_go) #Extracts program archive
        vprint("Moving program to directory")
        os.system("mkdir ~/.hamstall/bin/" + program_internal_name) #Makes directory for program
        os.system("mv ~/.hamstall/temp/* ~/.hamstall/bin/" + program_internal_name ) #Moves program files
        vprint("Adding program to hamstall list of programs")
        os.system('echo "rm -rf ~/.hamstall/bin/' + program_internal_name + '" > ~/.hamstall/uninstall_scripts/' + program_internal_name) #Creates uninstall script
        os.system('chmod +x ~/.hamstall/uninstall_scripts/' + program_internal_name) #Adds line to uninstall script to remove it
        ###PATH CODE###
        vprint('Adding program to PATH')
        file_path = file.full("~/.bashrc")
        line_to_write = "export PATH=$PATH:~/.hamstall/bin/" + program_internal_name + '\n'
        with open(file_path, 'a') as bashrc:
            bashrc.write(line_to_write)
        ###/PATH CODE###
        print("Install Completed!")

    def uninstall(program):
        vprint("Removing program files")
        os.system("~/.hamstall/uninstall_scripts/" + program) #Runs uninstall script
        vprint("Removing uninstall script")
        os.system("rm -rf ~/.hamstall/uninstall_scripts/" + program) #Removes uninstall script
        hamstall.removeFromPath(program)
        print("Uninstall complete!")

    def removeFromPath(program):
        vprint('Removing ' + program + ' from PATH through bashrc.')
        to_be_removed = "export PATH=$PATH:~/.hamstall/bin/" + program + '\n' #Line to be removed
        file_path = file.full('~/.bashrc') #Set file path to bashrc
        f = open(file_path, 'r') #Open bashrc
        open_file = f.readlines() #Copy bashrc to program
        f.close() #Close bashrc

        rewrite = ''''''

        for line in open_file:
            if line == to_be_removed:
                vprint('Line removed!')
            else:
                rewrite += line #Loop that removes line that needs removal from the copy of bashrc
        written = open(file_path, 'w')
        written.write(str(rewrite))
        written.close() #Write then close our new bashrc
        vprint('Removal from PATH complete!')
        return

    def listPrograms():
        os.system("ls ~/.hamstall/uninstall_scripts")
        #This actually works pretty well. May make something better sooner or later.



###############Argument Parsing Below###############



parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('-i', "--install", help="Install a .tar.gz, .tar.xz, or .zip")
group.add_argument('-u', "--uninstall", help="Uninstall an insatlled program")
group.add_argument('-l', "--list", help="List installed programs", action="store_true")
group.add_argument('-f', "--first", help="Run first time setup", action="store_true")
group.add_argument('-e', "--erase", help="Delete hamstall from your system", action="store_true")
group.add_argument('-v', "--verbose", help="Toggle verbose mode", action="store_true")
args = parser.parse_args() #Parser stuff


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

elif args.uninstall != None:
    to_uninstall = args.uninstall
    file_check = file.exists("~/.hamstall/uninstall_scripts/" + to_uninstall) #Checks to see if the file path for the program's uninstall script exists
    if file_check == True: #If uninstall script exists
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
    f = open(file.full('~/.hamstall/verbose'), 'r')
    open_file = f.readlines()
    f.close() #Open file and read contents
    os.system('rm -rf ~/.hamstall/verbose') #Remvoe old verbose file
    if 'False' in open_file[0]:
        to_put = 'True'
    else:
        to_put = 'False' #Toggle
    os.system('echo ' + to_put + ' >> ~/.hamstall/verbose') #Change verbose mode
    print('Verbose mode changed to ' + to_put + '!')

else:
    print('No flag specified! Use -h or --help for help!')

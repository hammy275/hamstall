#!/usr/bin/python3

#Hamstall
#Please don't use this in an actual environment. It doesn't have much sanity checking, and I update it a lot, breaking compatability with older versions.

import os
import argparse
from pathlib import Path
import sys
import re #Imports that are needed

class file:
    def name(program): #Get name of program as it's stored
        program_internal_name = re.sub(r'.*/', '/', program) #Remove a lot of stuff (I'm going to pretend I know how re.sub works, but this gives you "/filename.tar.gz"
        program_internal_name = program_internal_name[1:(len(program_internal_name)-7)] #Some Python formatting that turns the path into "tarname"
        return program_internal_name #Return internal name (tarname)

    def extension(program):
        return program[((len(program))-7):len(program)] #Returns the last 7 characters of the provided file name.

    def exists(file_name):
        return os.path.isfile(os.path.expanduser(file_name)) #Returns True if the given file exists. Otherwise false.

def Install(program):
    program_internal_name = file.name(program)
    print("Removing old temp directory (if it exists!)")
    os.system("rm -rf ~/.hamstall/temp") #Removes temp directory (used during installs)
    print("Creating new temp directory")
    os.system("mkdir ~/.hamstall/temp") #Creates temp directory for extracting tar
    print("Extracting tar to temp directory")
    file_extension = file.extension(program)
    if file_extension == '.tar.gz':
        command_to_go = "tar xf " + program + " -C ~/.hamstall/temp/"
    elif file_extension == '.tar.xz':
        command_to_go = "tar xf " + program + " -C ~/.hamstall/temp/"
    os.system(command_to_go) #Extracts program tar
    print("Moving program to directory")
    os.system("mkdir ~/.hamstall/bin/" + program_internal_name) #Makes directory for program
    os.system("mv ~/.hamstall/temp/" + program_internal_name + " ~/.hamstall/bin/" ) #Moves program files
    print("Adding program to hamstall list of programs")
    os.system('echo "rm -rf ~/.hamstall/bin/' + program_internal_name + '" > ~/.hamstall/uninstall_scripts/' + program_internal_name) #Creates uninstall script
    os.system('chmod +x ~/.hamstall/uninstall_scripts/' + program_internal_name) #adds line to uninstall script to remove it
    #Here is where I should add stuff to PATH.
    print("Install Completed!")

def Uninstall(program):
    print("Removing program files")
    os.system("~/.hamstall/uninstall_scripts/" + program) #Runs uninstall script
    print("Removing uninstall script")
    os.system("rm -rf ~/.hamstall/uninstall_scripts/" + program) #Removes uninstall script
    print("Uninstall complete!")

def ListPrograms():
    os.system("ls ~/.hamstall/uninstall_scripts")
    #This actually works pretty well. May make something better sooner or later.

def FirstTimeSetup():
    print("Creating directories")
    os.system("mkdir ~/.hamstall")
    os.system("mkdir ~/.hamstall/temp")
    os.system("mkdir ~/.hamstall/bin")
    os.system("mkdir ~/.hamstall/uninstall_scripts") #Create some directories
    print('First time setup complete!')

def get_input(question, options, default): #Like input but with some checking
    answer = "-1" #Set answer to something
    while answer not in options and answer != "":
        answer = input(question)
        answer = answer.lower() #Loop ask question while the answer is invalid or not blank
    if answer == "":
        return default #If answer is blank return default answer
    else:
        return answer #Return answer if it isn't the default answer

###############Argument Parsing Below###############


parser = argparse.ArgumentParser()
parser.add_argument("-install", help="Install a .tar.gz or .tar.xz")
parser.add_argument("-uninstall", help="Uninstall an insatlled program")
parser.add_argument("-list", help="List installed programs")
parser.add_argument("-first", help="Run first time setup")
args = parser.parse_args() #Parser stuff
if args.install != None:
    to_install = args.install #to_install from the argument
    does_tar_exist = file.exists(to_install)
    if does_tar_exist == False:
        print("File to install does not exist!")
        sys.exit()
    program_internal_name = file.name(to_install) #Get the internal name (trim off everything except the file name before the .tar.gz
    file_check = file.exists("~/.hamstall/uninstall_scripts/" + program_internal_name) #Checks to see if the file path for the program's uninstall script exists
    if file_check == True: #Uninstall script exists, ask to reinstall program
        reinstall = get_input("Application already exists! Would you like to reinstall? [y/N]", ["y", "n"], "n") #Ask to reinstall
        if reinstall == "y":
            Uninstall(program_internal_name)
            Install(to_install) #Reinstall
        else:
            print("Reinstall cancelled.")
    else:
        Install(to_install) #No reinstall needed to be asked, install program

elif args.uninstall != None:
    to_uninstall = args.uninstall
    file_check = file.exists("~/.hamstall/uninstall_scripts/" + to_uninstall) #Checks to see if the file path for the program's uninstall script exists
    if file_check == True: #If uninstall script exists
        Uninstall(to_uninstall) #Uninstall program
    else:
        print("Program does not exist!") #Program doesn't exist

elif args.list != None:
    ListPrograms() #List programs installed

elif args.first != None:
    FirstTimeSetup() #First time setup

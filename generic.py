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

import sys
import file
import config

def get_input(question, options, default):
    """input() but supports a default answer and
    makes sure input is acceptable"""
    answer = "This is a string. There are many others like it, but this one is mine." #Set answer to something
    while answer not in options and answer != "":
        answer = input(question)
        answer = answer.lower()  #Loop ask question while the answer is invalid or not blank
    if answer == "":
        return default  #If answer is blank return default answer
    else:
        return answer  #Return answer if it isn't the default answer

def leave(exit_code=0):
    config.unlock()
    sys.exit(exit_code)
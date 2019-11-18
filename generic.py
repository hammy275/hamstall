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
import config


def get_input(question, options, default):
    """Get User Input.

    Get user input, except make sure the input provided matches one of the options we're looking for

    Args:
        question (str): Question to ask the user
        options (str[]): List of options the user can choose from
        default (str): Default option (used when user enters nothing)

    Returns:
        str: Option the user chose

    """
    answer = "This is a string. There are many others like it, but this one is mine."  # Set answer to something
    while answer not in options and answer != "":
        answer = input(question)
        answer = answer.lower()  # Loop ask question while the answer is invalid or not blank
    if answer == "":
        return default  # If answer is blank return default answer
    else:
        return answer  # Return answer if it isn't the default answer


def endi(state):
    """Bool to String.

    Args:
        state (bool): Bool to convert

    Returns:
        str: "enabled" if True, "disabled" if False

    """
    if state:
        return "enabled"
    else:
        return "disabled"


def leave(exit_code=0):
    #Will be removed soon in favor of config.save()
    config.write_db()
    config.unlock()
    sys.exit(exit_code)
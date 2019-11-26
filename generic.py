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

try:
    import PySimpleGUI as sg
except ImportError:
    pass

if config.mode == "gui":
    try:
        import PySimpleGUI as sg
    except ImportError:
        pass  # This will be caught by hamstall.py, let's not worry about it here.

def get_input(question, options, default, gui_labels=[]):
    """Get User Input.

    Get user input, except make sure the input provided matches one of the options we're looking for

    Args:
        question (str): Question to ask the user
        options (str[]): List of options the user can choose from
        default (str): Default option (used when user enters nothing)
        gui_labels (str[]): Labels to use for GUI buttons/dropdown menus (optional)

    Returns:
        str: Option the user chose

    """
    if config.mode == "cli":
        answer = "This is a string. There are many others like it, but this one is mine."  # Set answer to something
        while answer not in options and answer != "":
            answer = input(question)
            answer = answer.lower()  # Loop ask question while the answer is invalid or not blank
        if answer == "":
            return default  # If answer is blank return default answer
        else:
            return answer  # Return answer if it isn't the default answer
    elif config.mode == "gui":
        if gui_labels == []:
            gui_labels = options
        if len(options) <= 5:
            button_list = []
            for o in gui_labels:
                button_list.append(sg.Button(o))
            layout = [
                [sg.Text(question)],
                button_list
            ]
            window = sg.Window("hamstall-gui", layout, disable_close=True)
            while True:
                event, values = window.read()
                if event in gui_labels:
                    window.Close()
                    return options[gui_labels.index(event)]
        else:
            layout = [
                [sg.Text(question)],
                [sg.Combo(gui_labels, key="option"), sg.Button("Submit")]
            ]
            window = sg.Window("hamstall-gui", layout, disable_close=True)
            while True:
                event, values = window.read()
                if event == "Submit":
                    window.Close()
                    return options[gui_labels.index(values["option"])]



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


def pprint(st):
    if config.mode == "gui":
        sg.Popup(st)
    else:
        print(st)


def progress(val):
    """Update Progress of Operation.

    Updates a progress bar (if we have a GUI) as hamstall processes run

    Args:
        val (int): Value to update the progress bar to.

    """
    if config.mode == "gui":
        if config.install_bar is not None:
            config.install_bar.UpdateBar(val)
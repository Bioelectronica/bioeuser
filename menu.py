#!/usr/bin/python
import urwid
import subprocess as sp
import time
import pdb
import os
import json
from set_threshold import set_threshold_interactive
import configure as cfg

# Constants
exp_data_dir = '/data'     # Where data resides on master nuc (constant)
user_settings_file = '/data/default_settings/user_settings.json'

# Global UI state variables
keep_running = True        # Only way to exit the menu is to set this to false
exp_running = False        # True if an experiment is currently running on instrument

expdirs = None    # List of directories in exp_data_dir
user_settings = {'neg_ctrl_dir': None,
                 'pos_ctrl_dir': None,
                 'particlecriteria': {'Radius': [0,0],
                                      'Differential Grayscale Mean': [0,0]}
                }

"""
neg_ctrl_dir = 'None'      # Directory containing the negative control experiment
pos_ctrl_dir = 'None'      # Direcotry containing postive control experiment
thresholds = [[0,0],[0,0]] # Radius and DGM selected by user
expdirs = None             # List of experiment directories in the master
"""

def menu_button(caption, callback):
    """Returns AtttrMap-decorated button, with a click callback"""
    button = urwid.Button(caption)
    urwid.connect_signal(button, 'click', callback)
    return urwid.AttrMap(button, None, focus_map='reversed')

def sub_menu(caption, choices):
    """Returns a menu button and a closure that will open the
    menu when the button is clicked"""
    contents = menu(caption, choices)
    def open_menu(button):
        return top.open_box(contents)
    return menu_button([caption, u'...'], open_menu)

def menu(title, choices):
    """ builds a list box with a title and a sequence of widgets """
    body = [urwid.Text(title), urwid.Divider()]
    body.extend(choices)
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def item_chosen(button):
    """ displays the user's choice """
    global keep_running
    keep_running = False
    response = urwid.Text([button.label,'\n'])
    done = menu_button('Ok', exit_menus)
    top.open_box(urwid.Filler(urwid.Pile([response, done])))

def toast(message):
    """Displays a popup showing the message """
    txt_widget = urwid.Text([message,'\n'])
    done = menu_button('Ok', exit_menus)
    top.open_box(urwid.Filler(urwid.Pile([txt_widget, done])))


def exit_menus(button):
    raise urwid.ExitMainLoop()

class CascadingBoxes(urwid.WidgetPlaceholder):
    """ A widget that provides an open_box method, that displays a box on 
    top of previous content. Each successive box shifted to the right and down.
    Pressing ESC removes the current box and shows the previous one """

    max_box_levels = 4
    def __init__(self, box):
        super(CascadingBoxes, self).__init__(urwid.SolidFill(u'/'))
        self.box_level = 0
        self.open_box(box)
    def open_box(self, box):
        self.original_widget = urwid.Overlay(urwid.LineBox(box),
            self.original_widget,
            align='center', width=('relative', 80),
            valign='middle', height=('relative', 80),
            min_width=24, min_height=8,
            left=self.box_level * 3,
            right=(self.max_box_levels - self.box_level - 1) * 3,
            top=self.box_level * 2,
            bottom=(self.max_box_levels - self.box_level - 1) * 2)
        self.box_level += 1
    def keypress(self, size, key):
        if key == 'esc' and self.box_level > 1:
            self.original_widget = self.original_widget[0]
            self.box_level -= 1
        else:
            return super(CascadingBoxes, self).keypress(size, key)

#
# BUTTON EVENT HANDLER FUNCTIONS
#

def get_master_dirs():
    """returns a list of directories in the master /data directory"""
    # SSH to master and get the list of data directories
    dirs = [f.path for f in os.scandir(exp_data_dir) if f.is_dir()]
    dirs = [d[6:] for d in dirs]
    return dirs

def handle_refresh_data_dir(button):
    global expdirs
    """Refreshes list of data directories on master"""
    expdirs = ['None'] + get_master_dirs()
    raise urwid.ExitMainLoop()

def handle_choose_neg_ctrl(button):
    """Select directory on master containing negative control"""
    global user_settings
    user_settings['neg_ctrl_dir'] = None if button.label=='None' else button.label
    raise urwid.ExitMainLoop()

def handle_choose_pos_ctrl(button):
    """Select directory on master containing negative control"""
    global user_settings
    user_settings['pos_ctrl_dir'] = None if button.label=='None' else button.label
    raise urwid.ExitMainLoop()

def handle_quit(button):
    """ Quit the menu system """
    global keep_running
    keep_running = False
    raise urwid.ExitMainLoop()

def handle_set_threshold(button):
    """ Change selection criteria""" 
    global user_settings

    # Allow user to select thresholds graphically
    # Update the jsons in the master based on the selected threshold
    # A negative control experiment directory must be selected, positive one is optional
    if user_settings['neg_ctrl_dir'] is None:
        toast('\nNegative control directory required for threshold adjustment')
    else:
        if user_settings['pos_ctrl_dir'] is None:
            positive_dir = None
        else:
            positive_dir = exp_data_dir + '/' + user_settings['pos_ctrl_dir']
        negative_dir = exp_data_dir + '/' + user_settings['neg_ctrl_dir']

        # Interactively create a json file containing criteria
        new_thresholds = set_threshold_interactive(negative_dir, positive_dir)

        user_settings['particlecriteria'] = new_thresholds

        # Update the hypercell configuration with the new threshold values
        cfg.update_hypercell_cfg(new_thresholds)
        handle_view_threshold(button)
        #raise urwid.ExitMainLoop()


def handle_view_threshold(button):
    """view current thresholds"""
    info = 'Hypercell Sorting Thresholds\n\n' + \
        'Radius: {:0.2f} to {:0.2f}'.format( \
        user_settings['particlecriteria']['Radius'][0], \
        user_settings['particlecriteria']['Radius'][1]) + \
        '\n\nDifferential Grayscale Mean: {:0.0f} to {:0.0f}\n'.format(\
        user_settings['particlecriteria']['Differential Grayscale Mean'][0], \
        user_settings['particlecriteria']['Differential Grayscale Mean'][1])
    toast(info)


def experiment_state_label():
    """Returns a text label for menu reflecting experiment state.
    Depends on whether exp is running or stopped"""
    if exp_running:
        return "Stop Experiment 完成实验"
    else:
        return "Run Experiment 开始实验"

def make_menus(expdirs):
    """ Creates a hierarchy of menus, used to create the CascadingBoxes widget

    Args:
        expdirs(list):  list of experimental directories to show in menu

    Returns:
        obj: A urwid menu object
    """

    """
    # Start or stop experiment
    menu_items = [sub_menu(experiment_state_label(), [
                menu_button("Confirm 确认 " + experiment_state_label(), handle_experiment),
                menu_button("Cancel 取消", exit_menus),
                ])]
    """
    if not(exp_running):
        menu_items = [
           sub_menu("Change Selection Criteria", [
                menu_button("Refresh data directories", handle_refresh_data_dir),
                sub_menu("Select negative control",
                    [menu_button(d, handle_choose_neg_ctrl) for d in expdirs]),
                sub_menu("Select positive control",
                    [menu_button(d, handle_choose_pos_ctrl) for d in expdirs]),
                menu_button("Set threshold", handle_set_threshold),
                menu_button("View current threshold", handle_view_threshold),
                menu_button("Cancel 取消", exit_menus),
                ]),
           menu_button("Exit", handle_quit)
        ]
    return menu("Bioelectronica Hypercell Configuration", menu_items)


def load_menu_state():
    """Initializes the menu and the UI state variables from the user
    settings file """
    global user_settings
    global user_settings_file
    global expdirs
    if os.path.exists(user_settings_file):
        with open(user_settings_file) as f:
            user_settings = json.load(f)

    # Load the data directories from master
    expdirs = ['None'] + get_master_dirs()


def save_menu_state():
    """Saves the UI settings to the user settings file"""
    global user_settings
    global user_settings_file
    with open(user_settings_file, 'w+') as f:
        json.dump(user_settings, f)


# Start the UI loop
load_menu_state()
while keep_running:
    # Create and show the menus
    top = CascadingBoxes(make_menus(expdirs))
    urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()
save_menu_state()


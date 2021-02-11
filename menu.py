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
default_settings_dir = '/data/default_settings'
current_exp_dir = '/data/current_experiment'

# Global UI variables
keep_running = True              # Only way to exit the menu is to set this to false
expdirs = None                   # List of directories in exp_data_dir
neg_ctrl_dir =  None             # Directory containing the negative control experiment
pos_ctrl_dir =  None             # Directory containing the positive control experiment
radius_threshold = [None, None]  # Radius criteria selected by user
dgm_threshold = [None, None]     # Differential grayscale mean criteria selected by user


#
# URWID CASCADING MENUS
#
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

def bigtext(button):
    """ NOT CURRENTLY USED Displays a popup showing the message """
    txt1 = urwid.BigText('Bioelectronica', urwid.HalfBlock5x4Font())
    #pdb.set_trace()
    bt1 = urwid.Padding(txt1, width='clip', min_width=200)
    txt2 = urwid.BigText('Hypercell', urwid.HalfBlock5x4Font())
    #pdb.set_trace()
    bt2 = urwid.Padding(txt2, width='clip', min_width=200)
    done = menu_button('Ok', exit_menus)
    top.open_box(urwid.Filler(urwid.Pile([bt1, bt2, done])))
    #top.open_box(urwid.Filler(urwid.Pile([bt, done])))


def exit_menus(button):
    """Exits the current menu, go back to the main menu"""
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
# HELPER FUNCTIONS
#
def get_master_dirs():
    """returns a list of directories in the master /data directory"""
    # SSH to master and get the list of data directories
    dirs = [f.path for f in os.scandir(exp_data_dir) if f.is_dir()]
    dirs = [os.path.basename(d) for d in dirs]  # d[6:]
    return dirs

def set_threshold(ddir):
    """ set radius and dgm threshold based on typed user input 
    Args:
        ddir: which directory to modify json files
    """
    class ConversationListBox(urwid.ListBox):
        def __init__(self, questionlist, ddir):
            editlist = [urwid.Edit(q + "\n") for q in questionlist]
            body = urwid.SimpleFocusListWalker(editlist)
            super(ConversationListBox, self).__init__(body)
            self.ddir = ddir

        def keypress(self, size, key):
            # terrible to use global variables, but urwid widgets cannot
            # return values, so I don't see a good way to set
            # the thresholds without using globals
            global radius_threshold
            global dgm_threshold

            key = super(ConversationListBox, self).keypress(size, key)
            if key != 'enter':
                return key

            # If the user hits enter in the last entry position
            # exit the menu
            if self.focus_position == 3:
                def parse_input(string):
                    if string.strip() in ['', 'null', 'Null', 'none', 'None']:
                        return None
                    else:
                        return float(string)

                # Save all the values
                radius_threshold[0] = parse_input(self.body[0].edit_text)
                radius_threshold[1] = parse_input(self.body[1].edit_text)
                dgm_threshold[0] = parse_input(self.body[2].edit_text)
                dgm_threshold[1] = parse_input(self.body[3].edit_text)

                # Update the hypercell configuration with the new threshold values
                new_thresholds = {'particlecriteria': 
                                  {'Radius': \
                                   [radius_threshold[0], radius_threshold[1]],
                                   'Differential Grayscale Mean': \
                                   [dgm_threshold[0], dgm_threshold[1]]}}
                cfg.update_hypercell_cfg(new_thresholds, ddir = self.ddir)

                # Exit to main menu
                raise urwid.ExitMainLoop()
            else:
                self.focus_position += 1

    questionlist = ['Enter Radius lower threshold (or leave blank):',
                    'Enter Radius upper threshold (or leave blank):',
                    'Enter Differential Grayscale Mean lower threshold (or leave blank):',
                    'Enter Differential Grayscale Mean upper threshold (or leave blank):']
    #title = urwid.Text(['Set Hypercell Thresholds', '\n'])
    top.open_box(ConversationListBox(questionlist, ddir))
    #p = urwid.Filler(urwid.Pile([title, ConversationListBox(questionlist)]))
    #top.open_box(p)

# 
# HELPER FUNCTIONS
# 
def read_threshold(ddir):
    """ Reads a hypercell settings in ddir, returns the particle and dgm thresholds
    Args:
        ddir(str): data directory from which to read the json settings

    Returns:
        list: radius_threshold (2 element), dgm_threshold (2 element)
    """
    settings = cfg.get_hypercell_cfg(ddir)
    return (settings['particlecriteria']['Radius'],
            settings['particlecriteria']['Differential Grayscale Mean'])


def get_master_dirs():
    """returns a list of directories in the master /data directory"""
    # SSH to master and get the list of data directories
    dirs = [f.path for f in os.scandir(exp_data_dir) if f.is_dir()]
    dirs = [os.path.basename(d) for d in dirs] 
    return dirs

def set_threshold(ddir):
    """ set radius and dgm threshold based on typed user input 
    Args:
        ddir: which directory to modify json files
    """
    class ConversationListBox(urwid.ListBox):
        def __init__(self, questionlist, ddir):
            editlist = [urwid.Edit(q + "\n") for q in questionlist]
            body = urwid.SimpleFocusListWalker(editlist)
            super(ConversationListBox, self).__init__(body)
            self.ddir = ddir

        def keypress(self, size, key):
            # terrible to use global variables, but urwid widgets cannot
            # return values, so I don't see a good way to set
            # the thresholds without using globals
            global radius_threshold
            global dgm_threshold

            key = super(ConversationListBox, self).keypress(size, key)
            if key != 'enter':
                return key

            # If the user hits enter in the last entry position
            # exit the menu
            if self.focus_position == 3:
                def parse_input(string):
                    if string.strip() in ['', 'null', 'Null', 'none', 'None']:
                        return None
                    else:
                        return float(string)

                # Save all the values
                radius_threshold[0] = parse_input(self.body[0].edit_text)
                radius_threshold[1] = parse_input(self.body[1].edit_text)
                dgm_threshold[0] = parse_input(self.body[2].edit_text)
                dgm_threshold[1] = parse_input(self.body[3].edit_text)

                # Update the hypercell configuration with the new threshold values
                new_thresholds = {'particlecriteria': 
                                  {'Radius': \
                                   [radius_threshold[0], radius_threshold[1]],
                                   'Differential Grayscale Mean': \
                                   [dgm_threshold[0], dgm_threshold[1]]}}
                cfg.update_hypercell_cfg(new_thresholds, ddir = self.ddir)

                # Exit to main menu
                raise urwid.ExitMainLoop()
            else:
                self.focus_position += 1

    questionlist = ['Enter Radius lower threshold (or leave blank):',
                    'Enter Radius upper threshold (or leave blank):',
                    'Enter Differential Grayscale Mean lower threshold (or leave blank):',
                    'Enter Differential Grayscale Mean upper threshold (or leave blank):']
    #title = urwid.Text(['Set Hypercell Thresholds', '\n'])
    top.open_box(ConversationListBox(questionlist, ddir))
    #p = urwid.Filler(urwid.Pile([title, ConversationListBox(questionlist)]))
    #top.open_box(p)


def read_threshold(ddir):
    """ Reads a json settings in ddir, returns the particle and dgm thresholds
    Args:
        ddir(str): data directory from which to read the json settings

    Returns:
        list: radius_threshold (2 element), dgm_threshold (2 element)
    """
    with open(ddir + '/rta_settings_merge1.json') as f:
        settings = json.load(f)
    return (settings['particlecriteria']['Radius'],
            settings['particlecriteria']['Differential Grayscale Mean'])


def view_threshold(radius_threshold, dgm_threshold):
    """ show the radius and dgm threshold in a toast message
    Args:
        radius_threshold: 2 element list of radius criteria
        dgm_threshold: 2 element list of dgm criteria
    """
    info = 'Hypercell Sorting Thresholds\n\n' + \
           'Radius\nLower limit: {}\nUpper limit: {}\n\n'.format(
           radius_threshold[0], radius_threshold[1]) + \
           'Differential Grayscale Mean\nLower limit: {}\nUpper limit: {}\n'.format(
           dgm_threshold[0], dgm_threshold[1])
    toast(info)


#
# BUTTON EVENT HANDLER FUNCTIONS
#

def handle_choose_neg_ctrl(button):
    """Select directory on master containing negative control"""
    global neg_ctrl_dir
    neg_ctrl_dir = None if button.label=='None' else button.label
    raise urwid.ExitMainLoop()

def handle_choose_pos_ctrl(button):
    """Select directory on master containing negative control"""
    global pos_ctrl_dir
    pos_ctrl_dir = None if button.label=='None' else button.label
    raise urwid.ExitMainLoop()

def handle_quit(button):
    """ Quit the menu system """
    global keep_running
    keep_running = False
    raise urwid.ExitMainLoop()


def handle_plot(button):
    """ Plot radius and DGM """
    global neg_ctrl_dir
    global pos_ctrl_dir
    global radius_threshold
    global dgm_threshold

    # Allow user to select thresholds graphically
    # Update the jsons in the master based on the selected threshold
    # A negative control experiment directory must be selected, positive one is optional
    if neg_ctrl_dir is None:
        toast('\nNegative control directory required for plot')
    else:
        if pos_ctrl_dir is None:
            positive_dir = None
        else:
            positive_dir = exp_data_dir + '/' + pos_ctrl_dir
        negative_dir = exp_data_dir + '/' + neg_ctrl_dir

        # Allow user to draw thresholds on a plot
        new_thresholds = set_threshold_interactive(negative_dir, positive_dir)
        radius_threshold = new_thresholds['particlecriteria']['Radius']
        dgm_threshold = new_thresholds['particlecriteria']['Differential Grayscale Mean']

        # print out the thresholds drawn on plot
        view_threshold(radius_threshold, dgm_threshold)

def handle_view_threshold_default(button):
    global default_settings_dir
    radius_threshold, dgm_threshold = read_threshold(default_settings_dir)
    view_threshold(radius_threshold, dgm_threshold)


def handle_view_threshold_current(button):
    global current_exp_dir
    radius_threshold, dgm_threshold = read_threshold(current_exp_dir)
    view_threshold(radius_threshold, dgm_threshold)


def handle_set_threshold_default(button):
    global default_settings_dir
    set_threshold(default_settings_dir)


def handle_set_threshold_current(button):
    global current_exp_dir
    set_threshold(current_exp_dir)


def make_menus(expdirs):
    """ Creates a hierarchy of menus, used to create the CascadingBoxes widget

    Args:
        expdirs(list):  list of experimental directories to show in the first 2 submenus

    Returns:
        obj: A urwid menu object
    """

    menu_items = [
        sub_menu("Select negative control directory",
                 [menu_button(d, handle_choose_neg_ctrl) for d in expdirs]),
        sub_menu("Select positive control directory",
                [menu_button(d, handle_choose_pos_ctrl) for d in expdirs]),
        menu_button("Plot particle DGM vs. particle radius", handle_plot),
        menu_button("Set default threshold", handle_set_threshold_default),
        menu_button("View default threshold", handle_view_threshold_default),
        menu_button("Set current experiment threshold", handle_set_threshold_current),
        menu_button("View current experiment threshold", handle_view_threshold_current),
        menu_button("Exit", handle_quit)
    ]
    return menu("Bioelectronica Hypercell Configuration", menu_items)


def load_menu_state():
    """Initializes the menu and the UI state variables from the user
    settings file """
    global expdirs

    # Load the data directories from master
    expdirs = ['None'] + get_master_dirs()


# Start the UI loop
load_menu_state()
while keep_running:
    # Create and show the menus
    top = CascadingBoxes(make_menus(expdirs))
    urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()


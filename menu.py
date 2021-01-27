#!/usr/bin/python
import urwid
import subprocess as sp
import time
import pdb
#from scatter_threshold import scatter_threshold
import os
import json
from set_threshold import set_threshold_interactive


# Global UI state variables
keep_running = True      # Only way to exit the menu is to set this to false
exp_running = False      # True if an experiment is currently running on instrument
neg_ctrl_dir = 'None'    # Directory containing the negative control experiment
pos_ctrl_dir = 'None'    # Direcotry containing postive control experiment
exp_data_dir = '/data/data7'   # Where data resides on master nuc (constant)
thresholds = [0,0]       # Radius and DGM selected by user
expdirs = None           # List of experiment directories in the master


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

def handle_experiment(button):
    """Called to start or stop the experiment"""
    global exp_running
    """
    if exp_running:
        client('stop')
    else:
        client('start')
    exp_running = not(exp_running)
    """
    raise urwid.ExitMainLoop()

def handle_hw_test(button):
    """Runs hardware test"""
    """
    client('hwtest')
    """
    raise urwid.ExitMainLoop()

def get_master_dirs():
    """returns a list of directories in the master /data directory"""
    # SSH to master and get the list of data directories
    """
    dirs = sp.check_output(["ls","-d", exp_data_dir + "/*/", 
                           shell=False, text=True).split('\n') 
    """
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
    global neg_ctrl_dir 
    neg_ctrl_dir = button.label 
    raise urwid.ExitMainLoop()

def handle_choose_pos_ctrl(button):
    """Select directory on master containing negative control"""
    global pos_ctrl_dir 
    pos_ctrl_dir = button.label 
    raise urwid.ExitMainLoop()

def handle_hello(button):
    """Say hello to instrument"""
    """
    client('hello')
    time.sleep(4)
    """
    raise urwid.ExitMainLoop()

def handle_shutdown(button):
    """Shutdown the instrument"""
    """
    client('shutdown')
    time.sleep(2)
    """
    raise urwid.ExitMainLoop()

def handle_quit(button):
    """ Quit the menu system """
    global keep_running
    keep_running = False
    raise urwid.ExitMainLoop()

def handle_set_threshold(button):
    """ Change selection criteria""" 
    global pos_ctrl_dir
    global neg_ctrl_dir
    global exp_data_dir
    global thresholds

    # Allow user to select thresholds graphically
    # Update the jsons in the master based on the selected threshold
    # A negative control experiment directory must be selected, positive one is optional
    if neg_ctrl_dir != 'None':
        if pos_ctrl_dir != 'None':
            positive_dir = exp_data_dir + '/' + pos_ctrl_dir[:-1]
        else:
            positive_dir = None
        negative_dir = exp_data_dir + '/' + neg_ctrl_dir[:-1]

        # Interactively create a json file containing criteria
        crtjson = scatter_threshold(negative_dir, positive_dir)
        thresholds[0] = crtjson['particlecriteria']['Radius'][0]
        thresholds[1] = crtjson['particlecriteria']['Differential Grayscale Mean'][0]

        json_file = '/tmp/newcriteria.json'
        with open(json_file, 'w') as f:
            json.dump(crtjson, f)

        # Update all the merge and sample jsons with the user selected value
        masterjsons = ['/data/default_settings/rta_settings_' + cam + '.json'
                for cam in ['merge1', 'merge2', 'merge5', 'merge6',
                    'sample4', 'sample8', 'waste3', 'waste7']]
        for mj in masterjsons:
            with open(mj, 'r') as f:
                js = json.load(f)
            update_dict(js, crtjson)
            with open(mj[:-5] + '_new.json', 'w') as nf:
                json.dump(js, nf, indent=4)
    else:
        print('\nNegative control directory required for threshold adjustment')
        time.sleep(4)
    raise urwid.ExitMainLoop()

def handle_view_threshold(button):
    """view current thresholds"""
    response = urwid.Text([button.label,'\n'])
    done = menu_button('Ok', exit_menus)
    top.open_box(urwid.Filler(urwid.Pile([response, done])))
    time.sleep(4)

    #print('\nRadius: {:0.2f}, Differential Grayscale Mean {:0.0f}'.format(
    #    thresholds[0], thresholds[1]))
    #time.sleep(4)
    raise urwid.ExitMainLoop()

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
    # Run hardware test
    sub_menu("Run Hardware Test", [
        menu_button("Confirm 确认", handle_hw_test),
        menu_button("Cancel 取消", exit_menus),
        ]), 
    menu_button("Check connection to instrument", handle_hello),
    menu_button("Shutdown instrument", handle_shutdown),
    """
    if not(exp_running):
        menu_items = [
           sub_menu("Change Selection Criteria", [
                menu_button("Refresh data directories", handle_refresh_data_dir),
                sub_menu("Select negative control", 
                    [menu_button(d, handle_choose_neg_ctrl) for d in expdirs]),
                sub_menu("Select positive control", 
                    [menu_button(d, handle_choose_pos_ctrl) for d in expdirs]),
                menu_button("Define threshold", handle_set_threshold),
                menu_button("View current threshold", handle_view_threshold),
                menu_button("Cancel 取消", exit_menus),
                ]),
           menu_button("Exit", handle_quit)
        ]
    return menu("Bioelectronica Hypercell Configuration", menu_items)

# Load the data directories from master
expdirs = ['None'] + get_master_dirs()


# Start the UI loop
while keep_running:
    # Create and show the menus
    top = CascadingBoxes(make_menus(expdirs))
    urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()

#!/usr/bin/python
import urwid
import subprocess
from client import client
import time
import pdb

keep_running = True
exp_running = False

def menu_button(caption, callback):
    button = urwid.Button(caption)
    urwid.connect_signal(button, 'click', callback)
    return urwid.AttrMap(button, None, focus_map='reversed')

def sub_menu(caption, choices):
    contents = menu(caption, choices)
    def open_menu(button):
        return top.open_box(contents)
    return menu_button([caption, u'...'], open_menu)

def menu(title, choices):
    body = [urwid.Text(title), urwid.Divider()]
    body.extend(choices)
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def item_chosen(button):
    global keep_running
    keep_running = False
    response = urwid.Text([button.label,'\n'])
    done = menu_button(u'Ok', exit_menus)
    top.open_box(urwid.Filler(urwid.Pile([response, done])))

def exit_menus(button):
    raise urwid.ExitMainLoop()

class CascadingBoxes(urwid.WidgetPlaceholder):
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

def handle_experiment(button):
    global exp_running
    if exp_running:
        client('stop')
    else:
        client('start')
    exp_running = not(exp_running)
    raise urwid.ExitMainLoop()

def run_experiment(button):
    subprocess.run(["mkdir","re"])
    raise urwid.ExitMainLoop()

def hw_test(button):
    client('hwtest')
    raise urwid.ExitMainLoop()

def hello(button):
    client('hello')
    time.sleep(4)
    raise urwid.ExitMainLoop()

def change_selection_criteria(button):
    client('json', ['pathtomasterjson', 'pathtoclientjson'])
    time.sleep(4)
    raise urwid.ExitMainLoop()

def experiment_state_label():
    """Label for menu changes depending on if exp is running or stopped"""
    if exp_running:
        return "Stop Experiment 完成实验"
    else:
        return "Run Experiment 开始实验"

def make_menus():
    
    
    menu_items = [sub_menu(experiment_state_label(), [
                menu_button("Confirm 确认 " + experiment_state_label(), handle_experiment),
                menu_button("Cancel 取消", exit_menus),
                ])]
    if not(exp_running):
        menu_items = menu_items + [
            sub_menu("Run Hardware Test", [
                menu_button("Confirm 确认", hw_test),
                menu_button("Cancel 取消", exit_menus),
                ]),
            sub_menu("Change Selection Criteria", [
                menu_button("Confirm 确认", change_selection_criteria),
                menu_button("Cancel 取消", exit_menus),
                ]),
            menu_button("Hello", hello)]
    return menu("Bioelectronica Hypercell", menu_items)
    '''
    if True: 
        m = menu("Bioelectronica Hypercell", [
            sub_menu(experiment_state_label(), [
                menu_button("Confirm 确认 " + experiment_state_label(), handle_experiment),
                menu_button("Cancel 取消", exit_menus),
                ]),
            sub_menu("Run Hardware Test", [
                menu_button("Confirm 确认", hw_test),
                menu_button("Cancel 取消", exit_menus),
                ]),
            sub_menu("Change Selection Criteria", [
                menu_button("Confirm 确认", change_selection_criteria),
                menu_button("Cancel 取消", exit_menus),
                ]),
            menu_button("Hello", hello)
        ])
    
    return m
    '''

while keep_running:
    top = CascadingBoxes(make_menus())
    urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()

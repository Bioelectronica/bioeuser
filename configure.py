import json
import pdb
import subprocess as sp



""" This file contains functions to update the configuration of the Hypercell system

TODO 
Things to test:
- can't find files in directory - should throw exception
- newsettings does not match existing settings
- newsettings defines empty 'particlecriteria' key
- no connection to slave

"""

#
# Constants
#

# directory on master and slave NUCS where settings are found
default_settings_dir = '/data/default_settings'
current_exp_dir = '/data/current_experiment'

# list of hypercell cameras which map to folder names in data directories
cameras = ['merge1', 'merge2', 'merge5', 'merge6',
    'sample4', 'sample8', 'waste3', 'waste7']

# list of settings jsons, eg rta_settings_merge1.json, rta_settings_merge2.json, ..
settings_json = ['rta_settings_' + c + '.json' for c in cameras]
slave_url = 'slave'


#
# Main functions
#

def update_hypercell_cfg(newsettings, ddir = default_settings_dir):
    """ Updates hypercell settings in both master and slave nuc
    This function is intended to be run on the master nuc, and changes
    are copied over to the slave NUC

    Example:
        newsettings = {'particlecriteria': {
                        'Radius': [12, None],
                        'Differential Grayscale Mean': [65, None]}
                        }
        update_hypercell_cfg(newsettings)

    Args:
        newsettings(dict): settings to change.  Only keys in this dict will be updated
        ddir(str): Which directory to change settings. default is the default_settings directory
    """
    global settings_json

    # Update the merge, sample, waste jsons with the user selected value
    # (Reminder: this is done on the master NUC)
    json_files = [ddir + '/' + f for f in settings_json]
    [update_json_nested(f, newsettings) for f in json_files]
    copy_files_to_slave(json_files, ddir)


#
# Helper functions
#

def update_dict(d1, d2):
    """Update dictionary d1 with values in dictionary d2.
    This is similar to the python dict update function, except it updates
    only the lowest level key value pairs.
    Example:
        For example, if d2 is
            {'particlecriteria': {
                'Radius': [12, None],
                'Differential Grayscale Mean': [65, None]}
            }
        and d1 is
            {'particlecriteria': {
                'Radius': [8, None],
                'Differential Grayscale Mean': [60, None],
                'Grayscale Range': [0, 130]}
            }
        performing update_dict(d1,d2) will change d1 to the following
            {'particlecriteria': {
                'Radius': [2, None],
                'Differential Grayscale Mean': [65, None],
                'Grayscale Range': [0, 130]}
            }
        Note that Grayscale Range will not change
    """
    for k, v, in d2.items():
        if type(v) == dict:
            update_dict(d1[k], d2[k])
        else:
            d1[k] = v


def update_json_nested(path, d):
    """Update the json file contained in path with settings in dict d
        Only the keys listed in dict will be updated
    Args:
        path(str): full path to json file to update
        d(dict): dictionary of keys to udpate
    """
    with open(path,'r') as f:
        js=json.load(f)
    update_dict(js, d)
    with open(path,'w') as nf:
        json.dump(js,nf,indent=4)


def copy_files_to_slave(files, ddir):
    """ Copy the list of files to slave via SCP

    Args:
        files(list): list of files to copy
        ddir(str): directory on slave to copy files

    """
    # Now copy these file to the slave, so it has the same settings
    command ="scp {} slave:{}".format(' '.join(settings_json), ddir)
    sp.run([command], shell=True)

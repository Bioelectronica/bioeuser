import json
import pdb
import subprocess as sp



""" This file contains code to update the configuration of the Hypercell system 
"""

# Constants
data_dir = '/data/default_settings'
cameras = ['merge1', 'merge2', 'merge5', 'merge6',
    'sample4', 'sample8', 'waste3', 'waste7']
settings_json = [data_dir + '/rta_settings_' + c + '.json' 
        for c in cameras]
slave_url = 'slave'
 
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


def update_json(path,d,jl):
    """ NOT USED CURRENTLY 
    Updates a json file with a new dict

    Args:
        path(str): name of json file to update
        d(dict): dictionary with updated keys
        jl(str): if provided, update only the given key

    """
    with open(path,'r') as f:
        js=json.load(f)
    for k in d.keys():
        if jl=='':
            js.update({k:d[k]})
        else:
            js[jl].update({k:d[k]})
    with open(path,'w') as nf:
        json.dump(js,nf,indent=4)


def update_hypercell_cfg(newsettings):
    """ Updates hypercell default settings in both master and slave nuc
    This function is intended to be run on the master nuc, and changes
    are copied over to the slave NUC

    Args:
        newsettings(dict): updated newsettings.  Only keys in this will be updated
    """
    global settings_json

    # Update the merge, sample, waste jsons with the user selected value
    # (Reminder: this is done on the master NUC)
    [update_json_nested(f, newsettings) for f in settings_json]

    copy_cfg_to_slave()

def copy_cfg_to_slave():
    """ Copies all configuration files to slave """
    # Now copy these file to the slave, so it has the same settings
    command ="scp {} slave:{}".format(' '.join(settings_json), data_dir) 
    sp.run([command], shell=True)

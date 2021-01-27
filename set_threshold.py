import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv
import argparse
import subprocess
import os
import json
from matplotlib.backend_bases import MouseButton
import pdb
import pathlib
from RectBuilder import RectBuilder
import matplotlib.patches as patches

def parse_args():
    """ Parses command line arguments

    Returns:
        dict: contains all the keyword arguments passed to the function
    """

    # Create parser object
    parser = argparse.ArgumentParser(description='Input to the function 2 '
             'directories (positive and negative control). Function returns 2 '
             'dataframes with particle data for the + and - control.')

    # Add arguments
    parser.add_argument("-n", "--negative_dir", type=str, default=None,
                        help='Negative control directory')
    parser.add_argument("-p", "--positive_dir", type=str, default=None,
                        help='Positive control directory')

    # Parse and return arguments
    args = parser.parse_args()
    return vars(args)



def get_exp_data(negative_dir, positive_dir = None, location='local'):
    """ Grabs and aggregates experimental data from master in negative and postive
    control experiments

    Args:
        negative_dir: directory where negative control experiment
        positive_dir: directory containing positive control experiment
        location: 'master' to scp to master, or 'local' to copy local data

    Returns;
        list: 2 element list of dataframe containing particles from
              negative and positive experiments

    """

    tmp_dir = '/tmp'

    # Read all the csv files from the negative control experiment
    file_list = ["{}/opa_data_merge{:0d}/particles.csv".format(negative_dir, i)
                 for i in [1,2,5,6]]
    if location=='master':
        # Copy the data files from the master nuc.
        # This script runs on the client (laptop), so it does not have direct access
        # to the master nuc
        # Make temporary directories for negative and positive control data
        neg_dir = tmp_dir + '/neg'
        pathlib.Path(neg_dir).mkdir(parents=True, exist_ok=True)
        for f in file_list:
            subprocess.run(["scp -r master:{} {}/".format(f,neg_dir)],
                shell=True)
        mprt_datan = [pd.read_csv(neg_dir + '/' + f) for f in file_list]
    else:
        mprt_datan = [pd.read_csv(f) for f in file_list]
    # Combine the negative particle files into a single aggregate
    combined_mprtn = pd.concat(mprt_datan, ignore_index=True)

    # Now do the same for the positive directory, if it was specified
    if positive_dir is not None:
        file_list = ["{}/opa_data_merge{:0d}/particles.csv".format(positive_dir, i)
                 for i in [1,2,5,6]]
        if location=='master':
            pos_dir = tmp_dir + '/pos'
            pathlib.Path(pos_dir).mkdir(parents=True, exist_ok=True)
            for f in file_list:
                subprocess.run(["scp -r master:{} {}/".format(f,pos_dir)],
                    shell=True)
            mprt_datap = [pd.read_csv(pos_dir + '/' + f) for f in file_list]
        else:
            mprt_datap = [pd.read_csv(f) for f in file_list]
        combined_mprtp = pd.concat(mprt_datap, ignore_index=True)
    else:
        combined_mprtp = None

    return [combined_mprtn, combined_mprtp]


def set_threshold(negative_dir, positive_dir = None,  interactive = True,
                  verbose = False):
    """ NOT YET COMPLETE! Sets the threshold based on the user input chosen interactively 
    or passed into the function

    Args:
        negative_dir(str): The full path to the directory the negative control run
                           (run with no secreting cells)
        positive_dir(str): It is the directory name of the positive control run
                           (run with secreting cells)
    Returns:
        dict: Dictionary of new particle criteria
    """
    pass



def set_threshold_interactive(negative_dir, positive_dir = None, verbose=False):
    """Interactive (GUI) method to set the sorting thresholds

    Args:
        negative_dir(str): The full path to the directory the negative control run
                           (run with no secreting cells)
        positive_dir(str): It is the directory name of the positive control run
                           (run with secreting cells)
    Returns:
        dict: Dictionary of new particle criteria
    """

    # Get the combined data files for particles in the negative and positive 
    # control experiment
    if verbose: print('Reading data files')

    prtn, prtp = get_exp_data(negative_dir, positive_dir,
            location='local')

    # Plot and display the figure
    fig = plt.figure(figsize=(16,9))
    ax = fig.add_subplot(111)
    legend = []
    if prtp is not None:
        plt.scatter(prtp['Radius'], prtp['Differential Grayscale Mean'],
            alpha=0.3, s=3)
        legend.append('Positive Control Run')
    ax.scatter(prtn['Radius'], prtn['Differential Grayscale Mean'],
            alpha=0.3, s=3)
    legend.append('Negative Control Run')
    plt.legend(legend, loc="upper right")
    plt.xlabel('Radius', fontsize = 14)
    plt.ylabel('Differential Grayscale Mean(DGM)', fontsize = 14)
    plt.suptitle('Hypercell Sorting Criteria Selection\n', fontsize=18)
    ax.set_title('Using the mouse, draw a box representing selection criteria, ' + \
                 'and press q when finished', fontsize=12)
    plt.subplots_adjust(top=0.92)

    # Allow the user to draw a rectangle representing sorting thresholds
    rect = patches.Rectangle((0,0),0,0, edgecolor='b', facecolor='g', alpha=0.3)
    ax.add_patch(rect)
    rectbuilder = RectBuilder(rect)
    rectbuilder.connect()
    plt.show()

    # Return the criteria selected by the user
    xmin, xmax, ymin, ymax = rectbuilder.get_bounds()
    return {"particlecriteria": {
        "Radius": [xmin, xmax],
        "Differential Grayscale Mean": [int(ymin), int(ymax)]}}


def main():
    # Parse arguments
    kwargs = parse_args()

    # Call the main function
    criteria = set_threshold_interactive(**kwargs)
    print('New sorting criteria:\n', criteria)

if __name__ == "__main__":
    main()	

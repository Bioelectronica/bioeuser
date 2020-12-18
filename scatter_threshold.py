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

def parse_args():

    """ Parses command line arguments
        Returns:
            dict: contains all the keyword arguments passed to the function
    """

    # Create parser object
    parser = argparse.ArgumentParser(description='Input to the function 2 directories (positive and negative control). Function returns 2 dataframes with particle data for the + and - control.')


    # Add arguments
    parser.add_argument("-n", "--negative_dir", type=str, default=None,
                        help='Negative control directory')
                        
    # Add arguments
    parser.add_argument("-p", "--positive_dir", type=str, default=None,
                        help='Positive control directory')


    # Parse and return arguments
    args = parser.parse_args()
    return vars(args)

def scatter_threshold(negative_dir, positive_dir = None):
    """This function concatenates merge region particle info from negtive control and positive control so that 
    Args: 
        negative_dir(str): It is the directory name of the negative control run ( run with no secreting cells)
        positive_dir(str): It is the directory name of the positive control run (run with secreting cells)
    """
    #Read from the negative control directory
    mprt1n = pd.read_csv(negative_dir + '/' + 'opa_data_merge1' + '/' + 'particles.csv')
    mprt2n = pd.read_csv(negative_dir + '/' + 'opa_data_merge2' + '/' + 'particles.csv')
    mprt5n = pd.read_csv(negative_dir + '/' + 'opa_data_merge5' + '/' + 'particles.csv')
    mprt6n = pd.read_csv(negative_dir + '/' + 'opa_data_merge6' + '/' + 'particles.csv')

    mprt_datan = [mprt1n, mprt2n, mprt5n, mprt6n]
    combined_mprtn = pd.concat(mprt_datan, ignore_index=True)
    
    if (positive_dir is not None):
        #Read from the positive control directory
        mprt1p = pd.read_csv(positive_dir + '/' + 'opa_data_merge1' + '/' + 'particles.csv')
        mprt2p = pd.read_csv(positive_dir + '/' + 'opa_data_merge2' + '/' + 'particles.csv')
        mprt5p = pd.read_csv(positive_dir + '/' + 'opa_data_merge5' + '/' + 'particles.csv')
        mprt6p = pd.read_csv(positive_dir + '/' + 'opa_data_merge6' + '/' + 'particles.csv')

        mprt_datap = [mprt1p, mprt2p, mprt5p, mprt6p]
        combined_mprtp = pd.concat(mprt_datap, ignore_index=True)
        
        
        #Plot and display the figure
        
        plt.figure(figsize=(16,9))
        plt.scatter(combined_mprtp['Radius'], combined_mprtp['Differential Grayscale Mean'], alpha=0.5, s=3)
        plt.scatter(combined_mprtn['Radius'], combined_mprtn['Differential Grayscale Mean'], alpha=0.5, s=3)
        plt.legend(('cell Run', 'Negative Control Run')) 
        plt.xlabel('Radius', fontsize = 14)
        plt.ylabel('Differential Grayscale Mean(DGM)', fontsize = 14)
        plt.suptitle('Differential Grayscale Mean(DGM) vs Radius', fontsize = 18) 
        plt.subplots_adjust(top=0.94)
        
        #pdb.set_trace()
        clicks=plt.ginput(n=1,show_clicks=True,mouse_add=MouseButton.LEFT)
        print(clicks)
        threshold = int(clicks[0][0]), int(clicks[0][1])
        plt.show()
        #pdb.set_trace()
        plt.figure(figsize=(16,9))
        plt.scatter(combined_mprtp['Radius'], combined_mprtp['Differential Grayscale Mean'], alpha=0.5, s=3,label='Cell Run')
        plt.scatter(combined_mprtn['Radius'], combined_mprtn['Differential Grayscale Mean'], alpha=0.5, s=3,label='Negative Control Run')
        plt.xlabel('Radius', fontsize = 14)
        plt.ylabel('Differential Grayscale Mean(DGM)', fontsize = 14)
        plt.suptitle('Differential Grayscale Mean(DGM) vs Radius', fontsize = 18) 
        plt.subplots_adjust(top=0.94)
        
        radius_max = combined_mprtn['Radius'].max() if combined_mprtn['Radius'].max() > combined_mprtp['Radius'].max() else combined_mprtp['Radius'].max()
        dgm_max = combined_mprtn['Differential Grayscale Mean'].max() if combined_mprtn['Differential Grayscale Mean'].max() > combined_mprtp['Differential Grayscale Mean'].max() else combined_mprtp['Differential Grayscale Mean'].max()
        
        plt.hlines(threshold[1], threshold[0], radius_max, colors = "red", label = "Radius Threhold")
        plt.vlines(threshold[0], threshold[1], dgm_max, colors = "green", label = "DGM Threshold")
        plt.legend(loc="upper right")
        plt.show()
        
    if (positive_dir is None):       
        plt.figure(figsize=(16,9))
        plt.scatter(combined_mprtn['Radius'], combined_mprtn['Differential Grayscale Mean'], alpha=0.5, s=3)
        plt.legend(('Negative Control Run')) 
        plt.xlabel('Radius', fontsize = 14)
        plt.ylabel('Differential Grayscale Mean(DGM)', fontsize = 14)
        plt.suptitle('Differential Grayscale Mean(DGM) vs Radius', fontsize = 18) 
        plt.subplots_adjust(top=0.94)
        
        #pdb.set_trace()
        clicks=plt.ginput(n=1,show_clicks=True,mouse_add=MouseButton.LEFT)
        print(clicks)
        threshold = int(clicks[0][0]), int(clicks[0][1])
        plt.show()
        #pdb.set_trace()
        plt.figure(figsize=(16,9))
        plt.scatter(combined_mprtn['Radius'], combined_mprtn['Differential Grayscale Mean'], alpha=0.5, s=3,label='Negative Control Run')
        plt.xlabel('Radius', fontsize = 14)
        plt.ylabel('Differential Grayscale Mean(DGM)', fontsize = 14)
        plt.suptitle('Differential Grayscale Mean(DGM) vs Radius', fontsize = 18) 
        plt.subplots_adjust(top=0.94)
        
        radius_max = combined_mprtn['Radius'].max() 
        dgm_max = combined_mprtn['Differential Grayscale Mean'].max() 
        plt.hlines(threshold[1], threshold[0], radius_max, colors = "red", label = "Radius Threhold")
        plt.vlines(threshold[0], threshold[1], dgm_max, colors = "green", label = "DGM Threshold")
        plt.legend(loc="upper right")
        plt.show()
    
    #pdb.set_trace()
    Radius, DGM = threshold[0], threshold[1]
    

    with open('/home/saveguest/git-repos/OpticalPodAnalyzer/rta_settings_main.json', 'r') as f:
            data_json = json.load(f)
            #print("It is inside")
            
    data_json['particlecriteria']['Radius'][0] = Radius
    data_json['particlecriteria']['Differential Grayscale Mean'][0] = DGM

    #pdb.set_trace()

    with open('/home/saveguest/git-repos/OpticalPodAnalyzer/rta_settings_main.json', 'w') as f:
	    json.dump(data_json, f)
	    
    with open('/home/saveguest/git-repos/OpticalPodAnalyzer/rta_settings_main.json', 'r') as f:
            data_json = json.load(f)
    #pdb.set_trace()
    os.chdir('/home/saveguest/git-repos/OpticalPodAnalyzer')
    subprocess.run(["python /home/saveguest/git-repos/OpticalPodAnalyzer/generatertajson.py"],shell=True)	
        #data_json['particlecriteria']['Radius'][0] = Radius
    #return combined_mprtn, combined_mprtp
    """
    data_json['particlecriteria']['Radius'][0] = Radius
    data_json['particlecriteria']['Differential Grayscale Mean'][0] = DGM

    with open('~/git-repos/OpticalPodAnalyzer/rta_settings_main.json', 'w') as f:
    json.dump(data_json, f)

    subprocess.run(["python ~/git-repos/OpticalPodAnalyzer/generatertajson.py"],shell=True)
    """

	
	
	
				 
	



def main(): 
    # Parse arguments
    kwargs = parse_args()

    # Call the main function
    scatter_threshold(**kwargs)

if __name__ == "__main__":
    main()	

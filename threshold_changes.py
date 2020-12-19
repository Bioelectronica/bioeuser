import json
import pdb
import argparse
import os



def parse_args():

    """ Parses command line arguments
        Returns:
            dict: contains all the keyword arguments passed to the function
    """

    # Create parser object
    parser = argparse.ArgumentParser(description='Takes radius and DGM as input and makes the changes in all the json files')


    # Add arguments
    parser.add_argument("-r", "--Radius", type=str, default=None,
                        help='Radius')
                        
    # Add arguments
    parser.add_argument("-d", "--DGM", type=str, default=None,
                        help='Differential grayscale mean')


    # Parse and return arguments
    args = parser.parse_args()
    return vars(args)

# Copy settings
def threshold_changes(Radius, DGM):
    with open('/home/saveguest/git-repos/OpticalPodAnalyzer/rta_settings_main.json', 'r') as f:
        data_json = json.load(f)
    data_json['particlecriteria']['Radius'][0] = Radius
    data_json['particlecriteria']['Differential Grayscale Mean'][0] = DGM
    
    print("The radius and dgm values are", Radius, DGM)

    #pdb.set_trace()

    with open('/home/saveguest/git-repos/OpticalPodAnalyzer/rta_settings_main.json', 'w') as f:
	    json.dump(data_json, f)
	    
    with open('/home/saveguest/git-repos/OpticalPodAnalyzer/rta_settings_main.json', 'r') as f:
        data_json = json.load(f)
            
    #pdb.set_trace()
    #os.chdir('/home/saveguest/git-repos/OpticalPodAnalyzer')
    #subprocess.run(["python /home/saveguest/git-repos/OpticalPodAnalyzer/generatertajson.py"],shell=True)
    
    # Filenames
    main_json = '/data/default_settings/rta_settings_main.json'
    merge_json = '/data/default_settings/rta_settings_merge.json'
    sample_json = '/data/default_settings/rta_settings_sample.json'
    waste_json = '/data/default_settings/rta_settings_waste.json'
    roi_json = '/data/default_settings/rta_settings_roi.json'

    # Camera numbers
    merge_cams = ['merge{:0d}'.format(i) for i in [1,2,5,6]]
    waste_cams = ['waste{:0d}'.format(i) for i in [3,7]]
    sample_cams = ['sample{:0d}'.format(i) for i in [4,8]]

    # Read the main (parent) settings
    with open(main_json, 'r') as f:
        main_settings = json.load(f)

    # Read the ROI settings
    with open(roi_json, 'r') as f:
        roi_settings = json.load(f)

    # Write the merge files
    with open(merge_json, 'r') as f:
        merge_settings = json.load(f)
    for cam in merge_cams + waste_cams + sample_cams:
        settings = main_settings
        if 'merge' in cam:
            settings.update(json.load(open(merge_json,'r')))
        elif 'waste' in cam:
            settings.update(json.load(open(waste_json,'r')))
        elif 'sample' in cam:
            settings.update(json.load(open(sample_json, 'r')))
        settings.update(roi_settings[cam])
        settings['bg'] = './bg_{}.tiff'.format(cam)
        settings['dataout'] = './opa_data_{}'.format(cam)
        with open('/data/default_settings/rta_settings_{}.json'.format(cam), 'w') as f:
            json.dump(settings, f, indent=4)
            
            
            
def main(): 
    # Parse arguments
    kwargs = parse_args()

    # Call the main function
    threshold_changes(**kwargs)

if __name__ == "__main__":
    main()	


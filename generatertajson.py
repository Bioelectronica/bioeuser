import json
import pdb


# Copy settings

# Filenames
main_json = 'rta_settings_main.json'
merge_json = 'rta_settings_merge.json'
sample_json = 'rta_settings_sample.json'
waste_json = 'rta_settings_waste.json'
roi_json = 'rta_settings_roi.json'

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
    with open('rta_settings_{}.json'.format(cam), 'w') as f:
        json.dump(settings, f, indent=4)


import mne

# file load/manip packages 
import sys 
import os 
import json

def get_montage(cap_json):
    """Function to find proper montage file from json file of meta-data 
    
    @ throws: 
        - "Exception" exception if "cap_json" does not contain "CapManufacturersModelName"
    @ returns: montage file whose channel name set are a superset of the "raw" dataset's channel name set
    """
    try:
        # Get cap manufacturer model name
        model_name = cap_json["CapManufacturersModelName"]
        # Standardize montage file name
        model_name =  model_name.lower().replace("-", "").replace("_", "").replace(" ", "")
    except Exception:
        print("\"cap_json\" data must contain cap model details. Exiting")
        sys.exit(1)

    # Get set of standard montage files provided by mne
    montage_dir = os.path.join(os.path.dirname(mne.__file__), 'channels', 'data', 'montages')
    montage_files = os.listdir(montage_dir)
    
    # default to "standard_1020" if no exact file found 
    handle = "standard_1020"
    for file in montage_files:
        # Standardize standard montage file names 
        orig_name = file 
        montage_match = file[:-3].lower().replace("-", "").replace("_", "").replace(" ", "")
        
        # if found exact match, select this and break
        if montage_match == model_name:
            handle = orig_name
            break 
    return mne.channels.make_standard_montage(handle) 

with open("task-matchingpennies_eeg.json", encoding="utf8") as file:
        cap_json = json.load(file)
montage = get_montage(cap_json) 
print(montage)
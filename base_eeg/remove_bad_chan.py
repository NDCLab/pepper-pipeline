import matplotlib
import pathlib
import mne
import mne_bids
import autoreject as ar 

import logging
import sys
import os 
import json 

def main(): 
    # import raw data 
    # bids_root = pathlib.Path('raw_data/eegmatchingpennies')
    # bids_path = mne_bids.BIDSPath(subject='05', task='matchingpennies', datatype='eeg', root=bids_root)
    # raw = mne_bids.read_raw_bids(bids_path)

    # Find and set_montage 
    with open("raw_data/task-matchingpennies_eeg.json", encoding="utf8") as file:
        cap_json = json.load(file)
    montage = get_montage(cap_json) 
    print(montage.)
    # raw.set_montage(montage)

    # Mark and list bad channels 
    # remove_bad_channels(epochs, raw)

def remove_bad_channels(epochs: mne.Epochs, raw: mne.io.Raw) -> None:
    """Automatically detect bad channels and mark to ignore during analysis 

    @ modifies: raw 
    @ throws: 
        - "Exception" exception if "raw" is not an instance of "mne.io.Raw"
    @ postconditions: bad channels are annotated as such within "raw" dataset 
    """
    try:
        raw.load_data()
    except Exception:
        print("\"raw\" data must be an instance of mne.io.Raw. exiting")
        sys.exit(1)

    # Init logging file to record warnings and errors
    logging.basicConfig(filename='output.log', filemode='a', level=logging.NOTSET)

    reject = ar.AutoReject()
    reject.fit(epochs)
    reject_log = reject.get_reject_log(epochs)

    names = reject_log.ch_names
    print("rejection log:", names)

    for label in names:
        raw.drop_channels(label)

def get_montage(cap_json: dict) -> mne.channels.DigMontage:
    """Function to find proper montage file from json file of meta-data 
    
    @ throws: 
        - "Exception" exception if "cap_json" is not an instance of "dict" that contains "CapManufacturersModelName"
    @ returns: montage file whose channel name set are a superset of the "raw" dataset's channel name set
    """
    try:
        # Get cap manufacturer model name
        model_name = cap_json["CapManufacturersModelName"]
        # Standardize montage file name
        model_name =  model_name.lower().replace("-", "").replace("_", "").replace(" ", "")
        print("model name is", model_name)
    except Exception:
        print("\"cap_json\" data must be dict that contains cap model details. Exiting")
        sys.exit(1)

    # Get set of standard montage files:
    montage_dir = os.path.join(os.path.dirname(mne.__file__), 'channels', 'data', 'montages')
    montage_files = os.listdir(montage_dir)

    handle = "standard_1020"
    for file in montage_files:
        # Standardize standard montage file names 
        orig_name = file 
        montage_match = file[:-3].lower().replace("-", "").replace("_", "").replace(" ", "")

        print("checking", orig_name)

        if montage_match == model_name:
            handle = orig_name
            break 
    return mne.channels.make_standard_montage(handle) 

if __name__ == "__main__":
    main()

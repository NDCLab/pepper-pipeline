import mne
import pathlib
import json
import autoreject as ar
from find_montage import get_montage
from mne_bids import BIDSPath, read_raw_bids
import finalRej as fr
    
def main():
    # import raw data 
    bids_root = pathlib.Path('BIDS')
    bids_path = BIDSPath(subject='NDARAB793GL3',
        session='01',
        task='ContrastChangeBlock1',
        run='01',
        datatype='eeg', root=bids_root)
    raw = read_raw_bids(bids_path)
    # Generate events to segment data into epochs 
    events, event_id = mne.events_from_annotations(raw)
    epochs = mne.Epochs(raw, events, event_id=event_id, preload=True)
    #get montage
    with open("BIDS/sub-NDARAB793GL3/ses-01/eeg/sub-NDARAB793GL3_ses-01_task-ContrastChangeBlock1_run-01_eeg.json", mode='r') as f:
        cap_json = json.load(f)
        montage_found = get_montage(cap_json)
    # Set montage
    easy_montage = mne.channels.make_standard_montage(montage_found)
    epochs.set_montage(easy_montage)

    #Sample user parameter 
    user_params={'tmin':-0.2,'tmax':0.5}
    output_dict_finalRej=fr.final_reject_epoch(user_params, epochs, raw)
    print('this is the the output dictionary ---> ',output_dict_finalRej)

if __name__=='__main__':
    main()


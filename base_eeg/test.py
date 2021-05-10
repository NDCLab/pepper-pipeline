import mne
import pathlib
import autoreject as ar
from mne_bids import BIDSPath, read_raw_bids
import finalRej as fr
    
def main():
    # import raw data 
    bids_root = pathlib.Path('../raw_data/eeg_matchingpennies')
    bids_path = BIDSPath(subject='05', task='matchingpennies', datatype='eeg', root=bids_root)
    raw = read_raw_bids(bids_path)
    # Generate events to segment data into epochs 
    events, event_id = mne.events_from_annotations(raw)
    epochs = mne.Epochs(raw, events, event_id=event_id, preload=True)
    # Set montage
    easy_montage = mne.channels.make_standard_montage('standard_1020')
    epochs.set_montage(easy_montage)

    #Sample user parameter 
    user_params={'tmin':-0.2,'tmax':0.5}
    output_dict_finalRej=fr.final_reject_epoch(user_params, epochs, raw)
    print('this is the the output dictionary ---> ',output_dict_finalRej)

if __name__=='__main__':
    main()


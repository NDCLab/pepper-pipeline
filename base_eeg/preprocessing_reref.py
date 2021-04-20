import matplotlib
import pathlib
import mne
import mne_bids

def baseeeg_preprocessing_reref(raw: mne.io.Raw, ref_channels=None) -> mne.io.Raw:
    try:
        raw.load_data()
        
        # add back reference channel (all zero)
        if ref_channels is None:
            raw_new_ref = raw
        else:
            raw_new_ref = mne.add_reference_channels(raw, ref_channels=ref_channels)

        # return average reference
        return raw_new_ref.copy().set_eeg_reference(ref_channels='average')
    
    except TypeError:
        print('Type Error')
        
    except Exception:
        print('Unknown Error')
        
# Read BIDS data
bids_root = pathlib.Path('raw_data/eegmatchingpennies')
bids_path = mne_bids.BIDSPath(subject='05',
                              task='matchingpennies',
                              datatype='eeg',
                              root=bids_root)
raw = mne_bids.read_raw_bids(bids_path)
raw.plot()

# average referencing
raw_avg_ref = baseeeg_preprocessing_reref(raw, ref_channels=['FZ'])
raw_avg_ref.plot()

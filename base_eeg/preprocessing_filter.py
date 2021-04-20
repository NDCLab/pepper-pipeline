import matplotlib
import pathlib
import mne
import mne_bids

def baseeeg_preprocessing_filter(raw: mne.io.Raw, l_freq=0.3, h_freq=40) -> mne.io.Raw:
    try:
        raw.load_data()
        return raw.copy().filter(l_freq=l_freq, h_freq=h_freq)
        
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

# filter
raw_filtered = baseeeg_preprocessing_filter(raw)

raw_filtered.plot()

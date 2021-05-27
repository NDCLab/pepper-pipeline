import pathlib
import mne_bids

# load raw data 
bids_root = pathlib.Path('CMI\\rawdata')
bids_path = mne_bids.BIDSPath(subject='NDARAB793GL3',
                              session='01',
                              task='ContrastChangeBlock1',
                              run='01',
                              datatype='eeg',
                              root=bids_root)
raw = mne_bids.read_raw_bids(bids_path)
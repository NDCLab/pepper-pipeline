import mne
import pathlib
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

    # Set montage
    easy_montage = mne.channels.make_standard_montage('GSN-HydroCel-129')
    epochs.set_montage(easy_montage)

    # Sample user parameter
    output_dict_finalRej = fr.final_reject_epoch(epochs)
    print('this is the the output dictionary ---> ', output_dict_finalRej)

if __name__ == '__main__':
    main()

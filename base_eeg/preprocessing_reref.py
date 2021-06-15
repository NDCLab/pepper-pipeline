import pathlib
import mne
import mne_bids


def reref_raw(raw, ref_channels=None):
    """Re-reference the data to the average of all electrodes
    Parameters
    ----------
    raw:    mne.io.Raw
            raw object of EEG data
    ref_channels: list
            list of reference channels

    Throws
    ----------
    TypeError:
                returns if raw is improper type
    Exception:
                returns if unexpected error is encountered
    Returns
    ----------
    raw_filtered:   mne.io.Raw
                    instance of rereferenced data
    output_dict_reference:  dictionary
                            dictionary with relevant information on re-ref
    """
    try:
        raw.load_data()

        # add back reference channel (all zero)
        if ref_channels is None:
            raw_new_ref = raw
        else:
            raw_new_ref = mne.add_reference_channels(raw,
                                                     ref_channels=ref_channels)

        ref_type = "average"
        raw_new_ref = raw_new_ref.set_eeg_reference(ref_channels=ref_type)

        ref_details = {
            "Reference Type": ref_type
        }
        # return average reference
        return raw_new_ref, {"Reference": ref_details}

    except TypeError:
        print('Type Error')

    except Exception:
        print('Unknown Error')


# Read BIDS data
bids_root = pathlib.Path('CMI/rawdata')
bids_path = mne_bids.BIDSPath(subject='NDARAB793GL3',
                              task='ContrastChangeBlock1',
                              session='01',
                              run='01',
                              datatype='eeg',
                              root=bids_root)
raw = mne_bids.read_raw_bids(bids_path)
raw.plot()

# average referencing
raw_avg_ref, output_dict = reref_raw(raw, ref_channels=['FZ'])
print("output dictionary", output_dict)
raw_avg_ref.plot()

import pathlib
import mne_bids


def baseeeg_preprocessing_filter(raw, l_freq=0.3, h_freq=40):
    """Final and automatic rejection of bad epochs
    Parameters
    ----------
    raw:    mne.io.Raw
            initially loaded raw object of EEG data

    l_freq: float
            lower pass-band edge

    h_freq: float
            higher pass-band edge

    Returns
    ----------
    raw_filtered:   mne.io.Raw
                    instance of "cleaned" raw data using filter

    output_dict_flter:  dictionary
                        dictionary with relevant filter information
    """
    try:
        raw.load_data()
        raw_filtered = raw.filter(l_freq=l_freq, h_freq=h_freq)

        h_pass = raw_filtered.info["highpass"]
        l_pass = raw_filtered.info["lowpass"]
        samp_freq = raw_filtered.info["sfreq"]

        filter_details = {"Highpass corner frequency": h_pass,
                          "Lowpass corner frequency": l_pass,
                          "Sampling Rate": samp_freq}

        return raw_filtered, {"Filter": filter_details}
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
raw_filtered, output_filter = baseeeg_preprocessing_filter(raw)

raw_filtered.plot()
print(output_filter)

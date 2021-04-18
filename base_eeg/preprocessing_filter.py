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

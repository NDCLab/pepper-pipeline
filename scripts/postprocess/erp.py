import numpy as np
import mne

def get_trial_erp(fileList, event):
    """get trial level erp
    Parameters
    ----------
    fileList: list
              a list of file path in .fif format
    event: string
           name of event of interest
    Returns
    ----------
    dataList: a list of numpy arrays
    """
    dataList = []

    for dt in fileList:
        epo = mne.io.read_raw_fif(dt)[event]
        epo_arr = epo.get_data()
        # return a array of shape (n_epochs, n_channels, n_times)
        dataList.append(np.mean(epo_arr, axis=(1, 2)))

    return dataList
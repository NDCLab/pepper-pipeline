import mne


def get_trial_erp(filelist, start_t, end_t, conditions, electrode):
    """get trial level erp
    Parameters
    ----------
    filelist: list
              a list of file path in .fif format
    start_t: float
             start time point of interest (in second), e,g., 0, 0.1
    end_t: float
             end time point of interest (in second), e,g., 0.1, 0.2
    conditions: a list of strings
           name of the events of interest
    pick_elec: a list of strings
           names of the electrode of interest
    Returns
    ----------
    trial_erp: a dictionary with a key per requested condition, each containing a list of numpy arrays
    """
    trial_erp = {key: [] for key in conditions}

    for dt in filelist:
        if dt.endswith('.fdt'):
            raw = mne.read_raw_eeglab(dt)
        else:
            raw = mne.read_epochs(dt)

        # subset to the time and electrodes specified
        data_cropped = raw.copy().pick_channels(electrode).crop(tmin=start_t, tmax=end_t)

        # for each condition, get the average across the time window indicated
        for c in conditions:
            trial_erp[c].append(data_cropped[c].get_data().mean(axis=(1, 2)))

    return trial_erp

import bisect
import mne
import numpy as np
import os
import pandas as pd


def sd_sample_mean(values):
    """get standard error of the sample mean
    Parameters
    ----------
    values: np array
            a list of sample values, shape - epochs * 1
    Returns
    ----------
    sd_sm: float
           standard error of the sample mean
    """
    return np.std(values, ddof=1) / np.sqrt(values.shape[0])


def sme(filelist, start_t, end_t, cond, pick_elec):
    """get trial level erp
    Parameters
    ----------
    filelist: list
              a list of file path in .fif format
    start_t: float
             start time point of interest (in second), e,g., 0, 0.1
    end_t: float
           end time point of interest (in second), e,g., 0.1, 0.2
    cond: a list of string
          names of the event of interest
    pick_elec: a list of string
               names of the electrode of interest
    Returns
    ----------
    result: dataframe
            col1 - subject name (file name)
            col2 - SME values for condition1
            col3 - SME values for condition2
    """
    # create a dataframe to save the result
    col_index = cond.copy()
    col_index.insert(0, 'subject')
    result = pd.DataFrame(columns=col_index)

    for dt in filelist:
        raw = mne.read_epochs(dt)

        # find the start and end time points of interest
        start_point = bisect.bisect_left(raw.times, start_t)
        end_point = bisect.bisect_left(raw.times, end_t)

        # find the index of electrodes of interest
        elec = [raw.ch_names.index(i) for i in pick_elec]

        sem_arr = []
        # loop the condition list
        for i, element in enumerate(cond):
            # get epoch data within the condition of interest
            # return a array of shape (n_epochs, n_channels, n_times)
            try:
                epoch_con = raw[element]
            except KeyError:
                continue
            epoch_con_dat = epoch_con.get_data()

            # average across electrodes and time points of interest
            epoch_con_dat_int = epoch_con_dat[:, elec, start_point:end_point]
            epoch_con_dat_int_mean = np.mean(epoch_con_dat_int, axis=(1, 2))

            # compute standard error of the sample mean
            sem_arr.append(sd_sample_mean(epoch_con_dat_int_mean))

        # get subject name (file name)
        file_name = os.path.basename(dt)
        subj_name = file_name.split('.')[0]
        sem_arr.insert(0, subj_name)

        result.loc[len(result)] = sem_arr

    return result

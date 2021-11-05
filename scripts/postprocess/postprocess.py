import numpy as np
import mne
import bisect


def get_trial_erp(filelist, start_t, end_t, cond1, cond2=None):
    """get trial level erp
    Parameters
    ----------
    filelist: list
              a list of file path in .fif format
    start_t: float
             start time point of interest (in second), e,g., 0, 0.1
    end_t: float
             end time point of interest (in second), e,g., 0.1, 0.2
    cond1: string
           name of the first event of interest
    cond2: string
           name of the second event of interest
    Returns
    ----------
    dataList: a list of numpy arrays
    """
    datalist1 = []
    datalist2 = []

    for dt in filelist:
        raw = mne.read_epochs(dt)

        # find the start and end time points of interest
        start_point = bisect.bisect_left(raw.times, start_t)
        end_point = bisect.bisect_left(raw.times, end_t)

        # get erp data for condition 1
        epoch_con1 = raw[cond1]
        epoch_con1_arr = epoch_con1.get_data()
        # return a array of shape (n_epochs, n_channels, n_times)
        # cut the data to the time of interest
        epoch_con1_arr_int = epoch_con1_arr[:, :, start_point:end_point]

        # compute trial level erp
        datalist1.append(np.mean(epoch_con1_arr_int, axis=(1, 2)))

        # get erp data for condition 2
        if cond2 is not None:
            epoch_con2 = raw[cond2]
            epoch_con2_arr = epoch_con2.get_data()
            # return a array of shape (n_epochs, n_channels, n_times)
            # cut the data to the time of interest
            epoch_con2_arr_int = epoch_con2_arr[:, :, start_point:end_point]

            # compute trial level erp
            datalist2.append(np.mean(epoch_con2_arr_int, axis=(1, 2)))

    return datalist1, datalist2


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
    smelist: a list of list
             a list of SME value for each participant and each condition
    """
    smelist = []

    for dt in filelist:
        raw = mne.read_epoch(dt)

        # find the start and end time points of interest
        start_point = bisect.bisect_left(raw.times, start_t)
        end_point = bisect.bisect_left(raw.times, end_t)

        # find the index of electrodes of interest
        elec = [raw.ch_names.index(i) for i in pick_elec]

        sem_arr = np.empty(len(cond), dtype=float)
        # loop the condition list
        for i, element in enumerate(cond):
            # get epoch data within the condition of interest
            # return a array of shape (n_epochs, n_channels, n_times)
            epoch_con = raw[element]
            epoch_con_dat = epoch_con.get_data()

            # average across electrodes and time points of interest
            epoch_con_dat_int = epoch_con_dat[:, elec, start_point:end_point]
            if len(elec) == 1:
                epoch_con_dat_int_mean = np.mean(epoch_con_dat_int, axis=1)
            else:
                epoch_con_dat_int_mean = np.mean(epoch_con_dat_int, axis=(1, 2))

            # compute standard error of the sample mean
            sem_arr[i] = sd_sample_mean(epoch_con_dat_int_mean)

        smelist.append(sem_arr)
    return smelist
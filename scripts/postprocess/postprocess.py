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
        raw = mne.io.read_raw_fif(dt)

        # find the start and end time points of interest
        start_point = bisect.bisect_left(raw.times, start_t)
        end_point = bisect.bisect_left(raw.times, end_t)

        # get erp data for condition 1
        epoch_con1 = raw[cond1]
        epoch_con1_arr = epoch_con1.get_data()
        # return a array of shape (n_epochs, n_channels, n_times)
        # cut the data to the time of interest
        epoch_con1_arr_int = epoch_con1_arr[:,:,start_point:end_point]

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

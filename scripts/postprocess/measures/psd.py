import bisect
import os
import mne
import numpy as np
import pandas as pd
from mne.time_frequency import psd_welch


def get_trial_psd(filelist, start_freq, end_freq, bands, tmin=None, tmax=None, pick_elec=None, n_fft=256,
                  n_per_seg=None, average="mean"):
    """get power for given bands for each subject by using Welch’s method
    Parameters
    ----------
    filelist: list
              a list of file path in .fif format
    start_freq: float
                min frequency of interest
    end_freq: float
              max frequency of interest
    bands: dict
           a dictionary with a key per band of interest ("delta", "theta" etc.), each containing a list of
           starting freq and ending freq ([1,4], [4,8] etc.).
    tmin: float
          min time of interest
    tmax: float
          max time of interest
    pick_elec: a list of strings
               names of the electrode of interest
    n_fft: int
           The length of FFT used, must be >= n_per_seg (default: 256). The segments will be zero-padded
           if n_fft > n_per_seg. If n_per_seg is None, n_fft must be <= number of time points in the data.
    n_per_seg: int
               Length of each Welch segment (windowed with a Hamming window).
               Defaults to None, which sets n_per_seg equal to n_fft.
    average: str
             How to average the segments. If mean (default), calculate the arithmetic mean.
             If median, calculate the median, corrected for its bias relative to the mean.
             If None, returns the unaggregated segments.
    Returns
    ----------
    trial_psd: a dictionary with a key per requested band, each containing a list of numpy arrays
    result: dataframe
            col1 - subject name (file name)
            col2 - psd values for band1
            col3 - psd values for band2
    """
    # save trial level data to feed downstream analysis
    trial_psd = {key: [] for key in bands}

    # save subject psd for output
    col_name = [key for key in bands]
    # create a dataframe to save the result
    col_name.insert(0, 'subject')
    result = pd.DataFrame(columns=col_name)

    # if average is "none" -- the unaggregated segments will be returned. Then "mean" will be used.
    if average is None:
        average = "mean"

    for dt in filelist:
        if dt.endswith('.set'):
            raw = mne.io.read_epochs_eeglab(dt)
        else:
            raw = mne.read_epochs(dt)

        kwargs = dict(fmin=start_freq, fmax=end_freq,
                      tmin=tmin, tmax=tmax,
                      n_jobs=1, picks=pick_elec,
                      n_fft=n_fft, n_per_seg=n_per_seg)
        psds_welch_mean, freqs_mean = psd_welch(raw, average=average, **kwargs)

        # Convert power to dB scale and average across epochs and channels
        psds_welch_mean_db = 10 * np.log10(psds_welch_mean)

        # average across subjects and electrodes for computing result
        psds_welch_mean_db_avg = psds_welch_mean_db.mean(axis=(0, 1))

        band_list = []
        # loop through given freq bands
        for k in bands:
            start_idx = bisect.bisect_left(freqs_mean, bands[k][0])
            end_idx = bisect.bisect_left(freqs_mean, bands[k][1])
            
            # make sure to include both boundaries, since the end_idex will not be included in python
            if bands[k][1] == freqs_mean[end_idx]:
                end_idx = end_idx + 1

            # the end_idex will not be included in python
            band_list.append(psds_welch_mean_db_avg[start_idx:end_idx].mean())

            trial_psd[k].append(psds_welch_mean_db[:, :, start_idx:end_idx].mean(axis=(1, 2)))

        # get subject name (file name) to organize the output data into a dataframe(result)
        file_name = os.path.basename(dt)
        subj_name = file_name.split('.')[0]
        band_list.insert(0, subj_name)

        # append band_ser to new row
        band_ser = pd.Series(band_list, index=result.columns[:len(band_list)])
        result = result.append(band_ser, ignore_index=True)

    return trial_psd, result

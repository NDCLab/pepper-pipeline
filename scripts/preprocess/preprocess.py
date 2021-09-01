import autoreject as ar
import collections
import mne
import numpy as np
import pandas as pd

from mne.preprocessing.bads import _find_outliers
from scipy.stats import zscore

from scripts.constants import \
    INVALID_DATA_MSG, \
    INVALID_FILTER_FREQ_MSG, \
    INVALID_FR_DATA_MSG, \
    INVALID_MONTAGE_MSG, \
    INVALID_UPARAM_MSG


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
    except (AttributeError, TypeError):
        print(INVALID_DATA_MSG)
        return raw, {"Reference": {"ERROR": INVALID_DATA_MSG}}

    # add back reference channel (all zero)
    if ref_channels is None:
        raw_new_ref = raw
    else:
        raw_new_ref = mne.add_reference_channels(raw, ref_channels)

    ref_type = "average"
    raw_new_ref = raw_new_ref.set_eeg_reference(ref_channels=ref_type)

    ref_details = {
        "Reference Type": ref_type
    }
    # return average reference
    return raw_new_ref, {"Reference": ref_details}


def filter_data(raw, l_freq=0.3, h_freq=40):
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
    except (AttributeError, TypeError):
        print(INVALID_DATA_MSG)
        return raw, {"Filter": {"ERROR": INVALID_DATA_MSG}}
    except ValueError:
        print(INVALID_FILTER_FREQ_MSG)
        return raw, {"Filter": {"ERROR": INVALID_FILTER_FREQ_MSG}}

    h_pass = raw_filtered.info["highpass"]
    l_pass = raw_filtered.info["lowpass"]
    samp_freq = raw_filtered.info["sfreq"]

    filter_details = {
        "Highpass corner frequency": h_pass,
        "Lowpass corner frequency": l_pass,
        "Sampling Rate": samp_freq
    }

    return raw_filtered, {"Filter": filter_details}


def ica_raw(raw, montage):
    """Automatic artifacts identification - raw data is modified in place
    Parameters:
    ----------:
    raw:    mne.io.Raw
            raw object of EEG data after processing by previous steps (filter
            and bad channels removal)
    montage:    str
                montage
    Returns:
    ----------
    raw:   mne.io.Raw
           instance of raw data after removing artifacts (eog)
    output_dict_ica:  dictionary
                      dictionary with relevant ica information
    """

    try:
        raw.set_montage(montage)
    except ValueError:
        print(INVALID_MONTAGE_MSG)
        return raw, {"Ica": {"ERROR": INVALID_MONTAGE_MSG}}
    except (AttributeError, TypeError):
        print(INVALID_DATA_MSG)
        return raw, {"Ica": {"ERROR": INVALID_DATA_MSG}}

    # prepica - step1 - filter
    # High-pass with 1. Hz
    raw_filtered_1 = raw.copy()
    raw_filtered_1 = raw_filtered_1.load_data().filter(l_freq=1, h_freq=None)

    # prepica - step2 - segment continuous EEG into arbitrary 1-second epochs
    epochs_prep = mne.make_fixed_length_epochs(raw_filtered_1,
                                               duration=1.0,
                                               preload=True,
                                               overlap=0.0)
    # compute the number of original epochs
    epochs_original = epochs_prep.__len__()

    # drop epochs that are excessively “noisy”
    reject_criteria = dict(eeg=1000e-6)       # 1000 µV
    epochs_prep.drop_bad(reject=reject_criteria)

    # compute the number of epochs after removal
    epochs_bads_removal = epochs_prep.__len__()
    epochs_bads = epochs_original - epochs_bads_removal

    # ica
    method = 'picard'
    max_iter = 500
    fit_params = dict(fastica_it=5)
    ica = mne.preprocessing.ICA(n_components=None,
                                method=method,
                                max_iter=max_iter,
                                fit_params=fit_params)
    ica.fit(epochs_prep)

    # exclude eog
    # Note: should be edited later for "ch_name"
    eog_indices, eog_scores = ica.find_bads_eog(epochs_prep, ch_name='FC1')
    ica.exclude = eog_indices

    # reapplying the matrix back to raw data -- modify in place
    raw_icaed = ica.apply(raw.load_data())

    ica_details = {"original epochs": epochs_original,
                   "bad epochs": epochs_bads,
                   "bad epochs rate": epochs_bads / epochs_original,
                   "eog indices": eog_indices,
                   "eog_scores": eog_scores}

    return raw_icaed, {"Ica": ica_details}


def segment_data(raw, tmin, tmax, baseline, picks, reject_tmin, reject_tmax,
                 decim, verbose, preload):
    """Used to segment continuous data into epochs

    Parameters:
    -----------
    raw:    Raw
            Raw data in FIF format

    tmin:   float
            time before event

    tmax:   float
            time after event

    baseline:   None | tuple of length 2
                The time interval to consider as “baseline” when applying
                baseline correction

    picks:  str | list | slice | None
            Channels to include.

    reject_tmin:    float | None
                    Start of the time window used to reject epochs.

    reject_tmax: float | None
        End of the time window used to reject epochs.

    decim:  int
            Factor by which to subsample the data.

    verbose:    bool | str | int | None
                default verbose level

    preload:    bool
                Indicates whether epochs are in memory.

    Throws:
    -----------
    Will throw errors and exit if:
        - Null raw object

    Returns:
    -----------
    Will return epochs and a dictionary of epochs information
    during segmentation stage
    """

    try:
        events, event_id = mne.events_from_annotations(raw)
    except (TypeError, AttributeError):
        print(INVALID_DATA_MSG)
        return raw, {"Segment": {"ERROR": INVALID_DATA_MSG}}

    epochs = mne.Epochs(raw, events, event_id=event_id,
                        tmin=tmin,
                        tmax=tmax,
                        baseline=baseline,
                        picks=picks,
                        reject_tmin=reject_tmin,
                        reject_tmax=reject_tmax,
                        decim=decim,
                        verbose=verbose,
                        preload=preload
                        )

    # get count of all epochs to output dictionary
    ch_names = epochs.info.ch_names
    ch_epochs = {}
    for name in ch_names:
        ch_epochs[name] = epochs.get_data(picks=name).shape[0]

    return epochs, {"Segment": {"Generated Epochs": ch_epochs}}


def plot_sensor_locations(epochs, user_params):
    """Used to plot sensor locations given epochs

    Parameters:
    -----------
    epochs: Epoch
            Epochs extracted from a Raw instance

    user_params:dict
                Dictionary of user manipulated values

    Throws:
    -----------
    Will throw errors and exit if:
        - Null epoch object
        - Null user_params dictionary

    Returns:
    -----------
    Graph plotting of sensor locations
    """
    try:
        kind_selected = user_params["Segment"]["Plotting Information"]["Kinds"]
        ch_types = user_params["Segment"]["Plotting Information"]["Ch_type"]
    except TypeError:
        print(INVALID_UPARAM_MSG)
        return 1

    try:
        epochs.plot_sensors(kind=kind_selected, ch_type=ch_types)
    except TypeError:
        print(INVALID_DATA_MSG)
        return 1


def final_reject_epoch(epochs):
    """Final and automatic rejection of  epochs
    Parameters
    ----------
    epochs: mne.Epochs object
            instance of the mne.Epochs,

    Returns
    ----------
    epochs_clean:   mne.Epochs object
                    instance of "cleaned" epochs using autoreject

    output_dict_finalRej:   dictionary
                            dictionary with epochs droped per channel and
                            channels interpolated
    """

    # creates the output dictionary to store the function output
    output_dict_finalRej = collections.defaultdict(dict)
    output_dict_finalRej['interpolatedChannels'] = []

    # fit and clean epoch data using autoreject
    autoRej = ar.AutoReject()
    try:
        autoRej.fit(epochs)
    except ValueError:
        print(INVALID_FR_DATA_MSG)
        return epochs, {"Final Reject": {"ERROR": INVALID_FR_DATA_MSG}}
    except (TypeError, AttributeError):
        print(INVALID_DATA_MSG)
        return epochs, {"Final Reject": {"ERROR": INVALID_DATA_MSG}}

    epochs_clean = autoRej.transform(epochs)

    # Create a rejection log
    reject_log = autoRej.get_reject_log(epochs)

    # get channel names
    ch_names = epochs.info.ch_names

    # Create dataframe with the labels of which channel was interpolated
    df = pd.DataFrame(data=reject_log.labels, columns=ch_names)
    for ch in ch_names:
        if df[df[ch] == 2][ch].count() > 0:
            output_dict_finalRej['interpolatedChannels'].append(ch)

    for ch in ch_names:
        # store amount of epochs dropped for each channel
        output_dict_finalRej['epochsDropped'][ch] = str(
            epochs_clean.drop_log.count((ch,)))

    return epochs_clean, output_dict_finalRej


def interpolate_data(epochs, mode, method, reset_bads):
    """Used to return an epoch object that has been interpolated

    Parameters:
    ----------:
    epochs: mne.Epochs
            epochs before interpolation

    mode:   str
            Either 'accurate' or 'fast'

    method: dict
            Method to use for each channel type.

    reset_bads: bool
                If True, remove the bads from info.

    Throws:
    ----------
    Will throw errors and exit if:
        - Null raw object

    Will throw a warning if there are no bad channels to interpolate

    Returns:
    ----------
    Modified in place epochs object and output dictionary
    """
    try:
        epochs.interpolate_bads(mode=mode,
                                method=method,
                                reset_bads=reset_bads
                                )
        return epochs, {"Interpolation": {"Affected": epochs.info['bads']}}
    except (TypeError, AttributeError):
        print(INVALID_DATA_MSG)
        return epochs, {"Interpolation": {"ERROR": INVALID_DATA_MSG}}


def plot_orig_and_interp(orig_raw, interp_raw):
    """Used to plot the difference between the original data
    and the interpolated data.

    Parameters:
    ----------
    orig_raw:   Raw
                Raw data in FIF format. Before interpolation
    interp_raw: Raw
                Raw data in FIF format. After interpolation

    Throws:
    ----------
    An error and will exit if any of the raw objects are null

    Returns:
    ----------
    Graph plotting the difference between the original and
    interpolated data

    """
    if not orig_raw or not interp_raw:
        print(INVALID_DATA_MSG)
        return 1

    for title_, data_ in zip(['orig.', 'interp.'], [orig_raw, interp_raw]):
        figure = data_.plot(butterfly=True, color='#00000022', bad_color='r')
        figure.subplots_adjust(top=0.9)
        figure.suptitle(title_, size='xx-large', weight='bold')


def hurst(data):
    """Estimate Hurst exponent on a timeseries.

    Parameters:
    ----------
    data:    1D numpy array
             The timeseries to estimate the Hurst exponent for.

    Returns
    -------
    h:    float
          The estimation of the Hurst exponent for the given timeseries.
    """

    npoints = data.size
    yvals = np.zeros(npoints)
    xvals = np.zeros(npoints)
    data2 = np.zeros(npoints)

    index = 0
    binsize = 1

    while npoints > 4:
        y = np.std(data)
        index = index + 1
        xvals[index - 1] = binsize
        yvals[index - 1] = binsize * y

        npoints = (np.fix(npoints / 2)).astype(np.int32)
        binsize = binsize * 2

        # average adjacent points in pairs
        for i in range(npoints):
            index_i = (i + 1) * 2 - 1
            data2[i] = (data[index_i] + data[index_i - 1]) * 0.5

        data = data2[0:npoints]

    xvals = xvals[0:index]
    yvals = yvals[0:index]

    try:
        logx = np.log(xvals)
        logy = np.log(yvals)
        p2 = np.polyfit(logx, logy, 1)
    except Exception:
        print('Log Error!')
        return np.nan

    # Hurst exponent is the slope of the linear fit of log-log plot
    return p2[0]


def identify_badchans_raw(raw):
    """Automatic bad channel identification - raw data is modified in place

    Parameters:
    ----------:
    raw:    mne.io.Raw
            initially loaded raw object of EEG data

    Returns:
    ----------
    raw:   mne.io.Raw
           instance of "cleaned" raw data

    output_dict_flter:  dictionary
                        dictionary with relevant bad channel information
    """

    # get raw data matrix
    raw_data = raw.get_data()

    # get spherical and polar coordinates
    chs_x = np.array([loc['loc'][1] for loc in raw.info['chs']])
    chs_y = np.array([loc['loc'][0] * (-1) for loc in raw.info['chs']])
    chs_z = np.array([loc['loc'][2] for loc in raw.info['chs']])
    sph_phi = (np.arctan2(chs_z, np.sqrt(chs_x**2 + chs_y**2))) / np.pi * 180
    sph_theta = (np.arctan2(chs_y, chs_x)) / np.pi * 180
    theta = sph_theta * (-1)
    radius = 0.5 - sph_phi / 180
    chanlocs = pd.DataFrame({'x': chs_x,
                             'y': chs_y,
                             'z': chs_z,
                             'theta': theta,
                             'radius': radius})

    # compute the distance between each channel and reference
    # -- should be edited later to take reference from user_params
    # -- need to confirm the naming of channels across systems
    ref_theta = chanlocs.iloc[128]['theta']
    ref_radius = chanlocs.iloc[128]['radius']

    chanlocs['distance'] = chanlocs.apply(lambda x: np.sqrt(x['radius']**2 + ref_radius**2 - 2 * x['radius'] * ref_radius * np.cos(x['theta'] / 180 * np.pi - ref_theta / 180 * np.pi)), axis=1)

    # find bad channels based on their variances and correct for the distance
    chns_var = np.var(raw_data, axis=1)
    reg_var = np.polyfit(chanlocs['distance'], chns_var, 2)
    fitcurve_var = np.polyval(reg_var, chanlocs['distance'])
    corrected_var = chns_var - fitcurve_var
    bads_var = [raw.ch_names[i] for i in _find_outliers(corrected_var,
                                                        threshold=3.0,
                                                        max_iter=1,
                                                        tail=0)]

    # find bad channels based on correlations and correct for the distance
    chns_cor = np.nanmean(abs(np.corrcoef(raw_data)), axis=0)
    chns_cor[128] = np.nanmean(chns_cor)
    reg_cor = np.polyfit(chanlocs['distance'], chns_cor, 2)
    fitcurve_cor = np.polyval(reg_cor, chanlocs['distance'])
    corrected_cor = chns_cor - fitcurve_cor
    bads_cor = [raw.ch_names[i] for i in _find_outliers(corrected_cor,
                                                        threshold=3.0,
                                                        max_iter=1,
                                                        tail=0)]

    # find bad channels based on hurst exponent
    hurst_exp = np.array([hurst(i) for i in raw_data])
    hurst_exp[np.isnan(hurst_exp)] = np.nanmean(hurst_exp)
    bads_loc = np.where(abs(zscore(hurst_exp)) > 3)[0]
    bads_hurst = [raw.ch_names[i] for i in bads_loc]

    # mark bad channels
    raw.info['bads'].extend(bads_var + bads_cor + bads_hurst)

    badchans_details = {"badchans based on variances": bads_var,
                        "badchans based on correlations": bads_cor,
                        "badchans based on hurst exponent": bads_hurst}

    return raw, {"Badchans": badchans_details}

import autoreject as ar
import mne
import numpy as np
import pandas as pd
import scipy.stats as sp_stats
import warnings

from functools import reduce
from mne.preprocessing.bads import _find_outliers
from scipy.stats import zscore

from scripts.constants import MISSING_MONTAGE_MSG, INVALID_DATA_MSG


def set_montage(raw, montage):
    """Associate a montage with the dataset
    Parameters
    ----------
    raw:    mne.io.Raw
            raw EEG object

    montage: string
            name of montage to use

    Returns
    ----------
    raw:   mne.io.Raw
           raw EEG object with montage applied

    output_dict_montage:  dictionary
                          dictionary with montage information
    """
    try:
        raw.set_montage(montage)
    except (ValueError, AttributeError, TypeError) as error_msg:
        return raw, {"ERROR": str(error_msg)}

    montage_details = {
        "Montage": montage
    }
    return raw, {"Montage": montage_details}


def set_reference(raw, ref_channels):
    """Add reference channel into the dataset
    Parameters
    ----------
    raw:    mne.io.Raw
            raw EEG object

    ref_channels: string
                  name of online reference channel

    Returns
    ----------
    raw:   mne.io.Raw
           raw EEG object with reference channel added

    output_dict_reference:  dictionary
                            dictionary with reference information
    """
    try:
        raw.load_data()
        raw_new_ref = mne.add_reference_channels(raw, ref_channels)
        reference_details = {
            "Reference": ref_channels
        }
        return raw_new_ref, {"Reference": reference_details}
    except ValueError:
        reference_details = {
            "Reference": "Reference is already specified. Or invalid reference \
            channel name."
        }
        return raw, {"Reference": reference_details}


def reref_raw(raw, reref_channels='average'):
    """Re-reference the data
    Parameters
    ----------
    raw: instance of Raw | Epochs
         EEG data
    reref_channels: list of str | str
                    Can be:
                    The name(s) of the channel(s) used to construct the
                    reference.
                    'average' to apply an average reference (default)
                    'REST' to use the Reference Electrode Standardization
                    Technique infinity reference 4.
                    An empty list, in which case MNE will not attempt any
                    re-referencing of the data

    Throws
    ----------
    TypeError:
                returns if raw is improper type
    Exception:
                returns if unexpected error is encountered

    Returns
    ----------
    raw_rerefed: instance of Raw | Epochs
                 data after re-referenced
    output_dict_reference:  dictionary
                            dictionary with relevant information on re-ref
    """
    try:
        raw.load_data()
    except (AttributeError, TypeError) as error_msg:
        return raw, {"ERROR": str(error_msg)}

    raw_new_ref = raw.set_eeg_reference(reref_channels)

    reref_details = {
        "Rereference": reref_channels
    }

    # return rereferenced data
    return raw_new_ref, {"Rereference": reref_details}


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
    except (ValueError, AttributeError, TypeError) as error_msg:
        return raw, {"ERROR": str(error_msg)}

    h_pass = raw_filtered.info["highpass"]
    l_pass = raw_filtered.info["lowpass"]
    samp_freq = raw_filtered.info["sfreq"]

    filter_details = {
        "Highpass corner frequency": h_pass,
        "Lowpass corner frequency": l_pass,
        "Sampling Rate": samp_freq
    }

    return raw_filtered, {"Filter": filter_details}


def ica_raw(raw):
    """Automatic artifacts identification - raw data is modified in place
    Parameters:
    ----------
    raw:    mne.io.Raw
            raw object of EEG data after processing by previous steps (filter
            and bad channels removal)

    Returns:
    ----------
    raw:   mne.io.Raw
           instance of raw data after removing artifacts (eog)
    output_dict_ica:  dictionary
                      dictionary with relevant ica information
    """
    try:
        if raw.get_montage() is None:
            return raw, {"ERROR": MISSING_MONTAGE_MSG}
        # prep for ica - load and make a copy
        raw.load_data()
        raw_filt_copy = raw.copy()

        # High-pass with 1. Hz cut-off is recommended for ICA
        raw_filt_copy = raw_filt_copy.load_data().filter(l_freq=1, h_freq=None)
    except (ValueError, AttributeError, TypeError) as error_msg:
        return raw, {"ERROR": str(error_msg)}

    # epoch with arbitrary 1s
    epochs_prep = mne.make_fixed_length_epochs(raw_filt_copy,
                                               duration=1.0,
                                               preload=True,
                                               overlap=0.0)

    # number of epeochs pre-rejection
    epochs_original = epochs_prep.__len__()

    # detect epochs - that are excessively “noisy” for any channel
    reject_criteria = dict(eeg=1000e-6)  # 1000 µV
    epochs_prep.drop_bad(reject=reject_criteria)

    # compute the number of epochs after removal
    epochs_bads_removal = epochs_prep.__len__()
    epochs_bads = epochs_original - epochs_bads_removal

    # ica
    method = 'infomax'
    max_iter = 'auto'
    fit_params = dict(extended=True)
    ica = mne.preprocessing.ICA(n_components=None,
                                method=method,
                                max_iter=max_iter,
                                fit_params=fit_params)
    ica.fit(epochs_prep)

    # get the activation matrix - epochs * ics * time points
    icaact = ica.get_sources(epochs_prep).get_data()
    # transpose the activation matrix into ics * time points * epochs
    icaact = np.transpose(icaact, (1, 2, 0))

    # get the mixing matrix - channels * components
    icawinv = ica.get_components()

    # compute channel locations
    # first get a list of channel names after removing bad channels and the
    # reference channel
    raw_locs = raw_filt_copy.copy()
    bad_chans = raw_locs.info['bads']

    # remove bad channels
    raw_locs.drop_channels(bad_chans)

    # get channel positions from the raw data to compute the theta and radius
    cartesian_locations = raw_locs._get_channel_positions()

    # convert the unit from 'm' into 'cm'
    cartesian_locations = cartesian_locations * 100

    # get spherical coordinates
    spher_locations = mne.transforms._cart_to_sph(cartesian_locations)

    # get polar coordinates
    chn_locs = np.zeros([cartesian_locations.shape[0], 5])
    chn_locs[:, 0:3] = cartesian_locations
    # get polar coordinates - theta - convert to angle [-180, 180]
    chn_locs[:, 3] = spher_locations[:, 1] * 180 / np.pi
    # get polar coordinates - radius
    chn_locs[:, 4] = spher_locations[:, 0] * np.sin(spher_locations[:, 2])

    # identify artifacts by using adjust
    arti_hem, arti_vem, arti_eb, arti_gd, arti_adj = _adjust(icaact,
                                                             icawinv,
                                                             chn_locs)
    ica.exclude = arti_adj

    # reapplying the matrix back to raw data -- modify in place
    raw_icaed = ica.apply(raw.load_data())

    ica_details = {"original epochs": epochs_original,
                   "bad epochs": epochs_bads,
                   "bad epochs rate": epochs_bads / epochs_original,
                   "Horizontal Eye Movement": list(arti_hem.astype(str)),
                   "Vertical Eye Movement": list(arti_vem.astype(str)),
                   "Eye Blink": list(arti_eb.astype(str)),
                   "Generic Discontinuity": list(arti_gd.astype(str)),
                   "Total artifact components": list(arti_adj.astype(str))}

    return raw_icaed, {"Ica": ica_details}


def _adjust(icaact, icawinv, chanlocs):
    """Automatic EEG artifact Detector based on the Joint Use of Spatial and
    Temporal features this is the python version of the eeglab plugin ADJUST
    which is developed by Andrea Mognon (1) and Marco Buiatti (2)
    Reference paper: Mognon A, Jovicich J, Bruzzone L, Buiatti M,
    ADJUST: An Automatic EEG artifact Detector based on the Joint Use of
    Spatial and Temporal features. Psychophysiology 48 (2), 229-240 (2011).

    Parameters:
    ----------
    icaact:    3D numpy array
               the activation matrix - ics * time points * epochs
    icawinv:   2D numpy array
               the mixing matrix - channels * ics
    chanlocs:  2D numpy array
               1-3 columns: x, y and z;
               4th column: theta (in polar coordinates);
               5th column: radius (in polar coordinates)

    Returns:
    ----------
    hem: 1D numpy array
         artifact components for the horizontal eye movement
    vem: 1D numpy array
         artifact components for the vertical eye movement
    eb:  1D numpy array
         artifact components for the eye blink
    gd:  1D numpy array
         artifact components for the generic discontinuity
    result_ci: 1D numpy array
         total artifact components
    """

    # numbers of epochs
    num_epoch = icaact.shape[2]
    num_chs = chanlocs.shape[0]
    num_ics = icaact.shape[0]

    # compute IC topographies
    topografie = np.transpose(icawinv)

    # topographies and time courses normalization
    ScalingFactor = np.apply_along_axis(np.linalg.norm, 1, topografie)
    icaact_normed = np.ones_like(icaact)
    topografie_normed = np.ones_like(topografie)
    for i in range(0, num_ics):
        icaact_normed[i, :, :] = icaact[i, :, :] * ScalingFactor[i]
        topografie_normed[i, :] = topografie[i, :] / ScalingFactor[i]

    # compute GD - res
    # pos_x&y&z, *****need to adjust according to real data*****
    pos = chanlocs[:, 0:3]
    res = np.zeros(num_ics)

    for ic in range(0, num_ics):
        aux = []
        for el in range(0, num_chs - 1):
            # compute distance
            P = pos[el, :]
            d = pos - np.tile(P, (num_chs, 1))
            dist = np.sqrt(np.asarray((d * d).sum(1), dtype=np.float64))

            # 10 nearest channels to el
            repchas = np.argsort(dist)[1:11]
            # respective weights, computed wrt distance
            weightchas = np.exp(-dist[repchas])

            # difference between el and the average of 10 neighbors
            # weighted according to weightchas
            aux.append(abs(topografie_normed[ic, el] -
                           np.mean(weightchas * topografie_normed[ic, repchas])
                           ))

        res[ic] = max(aux)

    # get GD values
    gd_value = res

    # compute SED - Computes Spatial Eye Difference feature without
    # normalization
    # find electrodes in Left Eye area (LE)
    # indexes of LE electrodes - disagreement between
    # the matlab ADJUST and the paper
    indexl = np.where((chanlocs[:, 3] > 119) & (chanlocs[:, 3] < 151)
                      & (chanlocs[:, 4] > .3 * 9.5))
    # number of LE electrodes
    dimleft = len(indexl[0])

    # find electrodes in Right Eye area (RE)
    # indexes of RE electrodes
    indexr = np.where((chanlocs[:, 3] > 29) & (chanlocs[:, 3] < 61)
                      & (chanlocs[:, 4] > .3 * 9.5))
    # number of RE electrodes
    dimright = len(indexr[0])

    if dimleft * dimright == 0:
        # should return warning message as well
        print('ERROR: no channels included in some\
               scalp areas (dimleft & dimright).')

    # SED value
    medie_left = topografie_normed[:, indexl[0]].mean(1)
    medie_right = topografie_normed[:, indexr[0]].mean(1)
    sed_value = abs(medie_left - medie_right)

    # compute SAD - Spatial Average Difference
    # find electrodes in Frontal Area (FA)
    # indexes of FA electrodes
    indexf = np.where((chanlocs[:, 3] > 30) & (chanlocs[:, 3] < 150)
                      & (chanlocs[:, 4] > .4 * 9.5))
    # number of FA electrodes
    dimfront = len(indexf[0])

    # find electrodes in Posterior Area (PA)
    # indexes of PA electrodes
    indexp = np.where((chanlocs[:, 3] > -160) & (chanlocs[:, 3] < -20)
                      & (chanlocs[:, 4] > 0))
    # number of PA electrodes
    dimback = len(indexp[0])

    if dimfront * dimback == 0:
        # should return warning message as well
        print('ERROR: no channels included in some scalp areas \
              (dimfront & dimback).')

    # SAD value
    mean_front = topografie_normed[:, indexf[0]].mean(1)
    mean_back = topografie_normed[:, indexp[0]].mean(1)
    sad_value = abs(mean_front) - abs(mean_back)
    var_front = np.var(topografie_normed[:, indexf[0]], ddof=1, axis=1)
    var_back = np.var(topografie_normed[:, indexp[0]], ddof=1, axis=1)

    # SVD - Spatial Variance Difference between front zone and back zone
    diff_var = var_front - var_back

    # epoch dynamic range, variance and kurtosis
    # kurtosis is not exactly same
    # (matlab ADJUST uses the kurt method from eeglab), but fairly close
    kurt = np.apply_along_axis(lambda x: sp_stats.kurtosis(x, axis=None), 1,
                               icaact_normed).transpose()
    varmat = np.apply_along_axis(lambda x: np.var(x, ddof=1), 1,
                                 icaact_normed).transpose()

    # compute average value removing the top 1% of the values
    dim_remove = int(np.floor(.01 * num_epoch))

    mean_kurt = np.apply_along_axis(lambda x: np.mean(
        x[np.argsort(x)[0:(len(x) - dim_remove)]]), 0, kurt)

    mean_varmat = np.apply_along_axis(lambda x: np.mean(
        x[np.argsort(x)[0:(len(x) - dim_remove)]]), 0, varmat)

    max_varmat = np.apply_along_axis(
        lambda x: x[np.argsort(x)[-(dim_remove + 1)]], 0, varmat)

    # MEV in reviewed formulation
    nuovav = max_varmat / mean_varmat

    # Computing EM thresholds
    soglia_K, med1_K, med2_K = _em(mean_kurt)
    soglia_SED, med1_SED, med2_SED = _em(sed_value)
    soglia_SAD, med1_SAD, med2_SAD = _em(sad_value)
    soglia_GDSF, med1_GDSF, med2_GDSF = _em(gd_value)
    soglia_V, med1_V, med2_V = _em(nuovav)

    # Horizontal Eye Movement (HEM)
    hem = reduce(np.intersect1d, [np.where(sed_value >= soglia_SED)[0],
                                  np.where(medie_left * medie_right < 0)[0],
                                  np.where(nuovav >= soglia_V)[0]])

    # Vertical Eye Movements (VEM)
    vem = reduce(np.intersect1d, [np.where(sad_value >= soglia_SAD)[0],
                                  np.where(medie_left * medie_right > 0)[0],
                                  np.where(diff_var > 0)[0],
                                  np.where(nuovav >= soglia_V)[0]])

    # Eye Blink (EB)
    eb = reduce(np.intersect1d, [np.where(sad_value >= soglia_SAD)[0],
                                 np.where(medie_left * medie_right > 0)[0],
                                 np.where(diff_var > 0)[0],
                                 np.where(mean_kurt >= soglia_K)[0]])

    # Generic Discontinuities (GD)
    gd = reduce(np.intersect1d, [np.where(gd_value >= soglia_GDSF)[0],
                                 np.where(nuovav >= soglia_V)[0]])

    # Final results
    result_ci = np.unique(np.concatenate((hem, vem, eb, gd)))
    return hem, vem, eb, gd, result_ci


def _em(arr):
    """Automatic threshold on the digital numbers of the input vector 'vec';
    based on Expectation - Maximization algorithm
    Parameters:
    ----------
    arr:    1D numpy array
            row vector, to be thresholded

    Returns:
    ----------
    last:  float
           threshold value
    med1,med2:  float
           mean values of the Gaussian-distributed classes 1,2
    """

    len_arr = len(arr)
    # False Alarm cost
    c_FA = 1
    # Missed Alarm cost
    c_MA = 1

    # med = np.mean(arr)
    # std = np.std(arr)
    mediana = (max(arr) + min(arr)) / 2

    # initialization parameter/ righthand side
    alpha1 = 0.01 * (max(arr) - mediana)
    # initialization parameter/ lefthand side
    alpha2 = 0.01 * (mediana - min(arr))

    # EXPECTATION
    train1 = []
    train2 = []
    train = []

    for i in range(0, len_arr):
        if (arr[i] < (mediana - alpha2)):
            train2.append(arr[i])
        elif (arr[i] > (mediana + alpha1)):
            train1.append(arr[i])
        else:
            train.append(arr[i])

    n1 = len(train1)
    n2 = len(train2)

    med1 = np.mean(train1)
    med2 = np.mean(train2)
    prior1 = n1 / (n1 + n2)
    prior2 = n2 / (n1 + n2)
    var1 = np.var(train1, ddof=1)
    var2 = np.var(train2, ddof=1)

    if np.isnan(var1):
        var1 = 0
    if np.isnan(var2):
        var2 = 0

    # MAXIMIZATION
    count = 0
    dif_med_1 = 1
    dif_med_2 = 1
    dif_var_1 = 1
    dif_var_2 = 1
    dif_prior_1 = 1
    dif_prior_2 = 1
    stop = 0.0001

    while ((dif_med_1 > stop) & (dif_med_2 > stop) & (dif_var_1 > stop)
           & (dif_var_2 > stop) & (dif_prior_1 > stop) & (dif_prior_2 > stop)):

        count = count + 1

        med1_old = med1
        med2_old = med2
        var1_old = var1
        var2_old = var2
        prior1_old = prior1
        prior2_old = prior2
        prior1_i = []
        prior2_i = []

        # FOLLOWING FORMULATION IS ACCORDING TO REFERENCE PAPER
        for i in range(0, len_arr):
            if var1_old == 0:
                prob1 = 1
            else:
                prob1 = ((1 / (np.sqrt(2 * np.pi * var1_old))) * np.exp(
                    (-1) * ((arr[i] - med1_old) ** 2) / (2 * var1_old)))

            if var2_old == 0:
                prob2 = 1
            else:
                prob2 = ((1 / (np.sqrt(2 * np.pi * var2_old))) * np.exp(
                    (-1) * ((arr[i] - med2_old) ** 2) / (2 * var2_old)))

            prior1_i.append(prior1_old * prob1 /
                            (prior1_old * prob1 + prior2_old * prob2))
            prior2_i.append(prior2_old * prob2 /
                            (prior1_old * prob1 + prior2_old * prob2))

        prior1 = sum(prior1_i) / len_arr
        prior2 = sum(prior2_i) / len_arr
        med1 = sum(prior1_i * arr) / (prior1 * len_arr)
        med2 = sum(prior2_i * arr) / (prior2 * len_arr)
        var1 = sum(prior1_i * ((arr - med1_old) ** 2)) / (prior1 * len_arr)
        var2 = sum(prior2_i * ((arr - med2_old) ** 2)) / (prior2 * len_arr)

        dif_med_1 = abs(med1 - med1_old)
        dif_med_2 = abs(med2 - med2_old)
        dif_var_1 = abs(var1 - var1_old)
        dif_var_2 = abs(var2 - var2_old)
        dif_prior_1 = abs(prior1 - prior1_old)
        dif_prior_2 = abs(prior2 - prior2_old)

    # THRESHOLDING
    k = c_MA / c_FA
    a = (var1 - var2) / 2
    b = ((var2 * med1) - (var1 * med2))

    c = (np.log((k * prior1 * np.sqrt(var2)) / (prior2 * np.sqrt(var1)))
         * (var2 * var1)) + (((((med2) ** 2) * var1) -
                              (((med1) ** 2) * var2)) / 2)

    rad = (b ** 2) - (4 * a * c)
    if rad < 0:
        print('ERROR: Negative Discriminant!')
        return np.nan, med1, med2

    soglia1 = (-b + np.sqrt(rad)) / (2 * a)
    soglia2 = (-b - np.sqrt(rad)) / (2 * a)

    if (soglia1 < med2) | (soglia1 > med1):
        last = soglia2
    else:
        last = soglia1

    if np.isnan(last):
        last = mediana

    return last, med1, med2


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
        raw.load_data()
        events, event_id = mne.events_from_annotations(raw)
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
    except (TypeError, AttributeError, ValueError) as error_msg:
        return raw, {"ERROR": str(error_msg)}

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
    kind_selected = user_params["Segment"]["Plotting Information"]["Kinds"]
    ch_types = user_params["Segment"]["Plotting Information"]["Ch_type"]
    epochs.plot_sensors(kind=kind_selected, ch_type=ch_types)


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
    # fit and clean epoch data using autoreject
    autoRej = ar.AutoReject()
    try:
        # load in epochs and fit on autoRej model
        epochs.load_data()
        autoRej.fit(epochs)
    except (ValueError, TypeError, AttributeError) as error_msg:
        return epochs, {"ERROR": str(error_msg)}

    # creates the output dictionary to store the function output
    output_dict_finalRej = {}
    interpolatedChannels = []
    epochsDropped = {}

    epochs_clean = autoRej.transform(epochs)

    # Create a rejection log
    reject_log = autoRej.get_reject_log(epochs)

    # get channel names
    ch_names = epochs.info.ch_names

    # Create dataframe with the labels of which channel was interpolated
    df = pd.DataFrame(data=reject_log.labels, columns=ch_names)
    for ch in ch_names:
        if df[df[ch] == 2][ch].count() > 0:
            interpolatedChannels.append(ch)

    for ch in ch_names:
        # store amount of epochs dropped for each channel
        epochsDropped[ch] = str(epochs_clean.drop_log.count((ch,)))

    output_dict_finalRej = {
        "Interpolated channels": interpolatedChannels,
        "Epochs dropped": epochsDropped
    }

    return epochs_clean, {"Final Reject": output_dict_finalRej}


def interpolate_data(epochs, mode='accurate'):
    """Used to return an epoch object that has been interpolated

    Parameters:
    ----------:
    epochs: mne.Epochs
            epochs before interpolation

    mode:   str
            Either 'accurate' or 'fast'

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
        epochs.load_data()
        bads_before = epochs.info['bads']
    except (TypeError, AttributeError) as error_msg:
        return epochs, {"ERROR": str(error_msg)}

    if len(bads_before) == 0:
        return epochs, {"Interpolation": {"Affected": bads_before}}
    else:
        try:
            epochs_interp = epochs.interpolate_bads(mode=mode)
            return epochs_interp, {"Interpolation": {"Affected": bads_before}}
        except (TypeError, AttributeError) as error_msg:
            return epochs, {"ERROR": str(error_msg)}


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

    if 0 in xvals or 0 in yvals:
        print('Func hurst encountered zero in log. Nan value was returned.')
        return np.nan
    else:
        logx = np.log(xvals)
        logy = np.log(yvals)
        p2 = np.polyfit(logx, logy, 1)

    # Hurst exponent is the slope of the linear fit of log-log plot
    return p2[0]


def identify_badchans_raw(raw, ref_elec_name):
    """Automatic bad channel identification - raw data is modified in place

    Parameters:
    ----------:
    raw:    mne.io.Raw
            initially loaded raw object of EEG data

    ref_elec_name:    str
                      reference electrode name

    Returns:
    ----------
    raw:   mne.io.Raw
           instance of "cleaned" raw data

    output_dict_flter:  dictionary
                        dictionary with relevant bad channel information
    """
    try:
        raw.load_data()
        # get raw data matrix
        raw_data = raw.get_data()
        # get the index of reference electrode
        ref_index = raw.ch_names.index(ref_elec_name)
    except (ValueError, TypeError, AttributeError) as error_msg:
        return raw, {"ERROR": str(error_msg)}

    # get reference electrode location
    channel_positions = raw._get_channel_positions() * 100
    ref_x = channel_positions[ref_index][0]
    ref_y = channel_positions[ref_index][1]
    ref_z = channel_positions[ref_index][2]

    # get distances between electrodes and the reference electrode
    chan_ref_dist = [np.sqrt((x[0] - ref_x) ** 2 + (x[1] - ref_y) ** 2 +
                             (x[2] - ref_z) ** 2) for x in channel_positions]

    # find bad channels based on their variances and correct for the distance
    chns_var = np.var(raw_data, axis=1)

    try:
        reg_var = np.polyfit(chan_ref_dist, chns_var, 2)
        fitcurve_var = np.polyval(reg_var, chan_ref_dist)
    except np.linalg.LinAlgError as error_msg:
        return raw, {"ERROR": str(error_msg)}

    corrected_var = chns_var - fitcurve_var
    bads_var = [raw.ch_names[i] for i in _find_outliers(corrected_var,
                                                        threshold=3.0,
                                                        max_iter=1,
                                                        tail=0)]

    # find bad channels based on correlations and correct for the distance
    # ignore the warning when the data has nothing but nan values for the
    # np.nanmean

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        chns_cor = np.nanmean(abs(np.corrcoef(raw_data)), axis=0)
        chns_cor[ref_index] = np.nanmean(chns_cor)

    reg_cor = np.polyfit(chan_ref_dist, chns_cor, 2)
    fitcurve_cor = np.polyval(reg_cor, chan_ref_dist)
    corrected_cor = chns_cor - fitcurve_cor
    bads_cor = [raw.ch_names[i] for i in _find_outliers(corrected_cor,
                                                        threshold=3.0,
                                                        max_iter=1,
                                                        tail=0)]

    # find bad channels based on hurst exponent
    hurst_exp = np.array([hurst(i) for i in raw_data])

    # ignore the warning when the data has nothing but nan values for the
    # np.nanmean
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        hurst_exp[np.isnan(hurst_exp)] = np.nanmean(hurst_exp)
    bads_loc = np.where(abs(zscore(hurst_exp)) > 3)[0]
    bads_hurst = [raw.ch_names[i] for i in bads_loc]

    # mark bad channels
    raw.info['bads'].extend(bads_var + bads_cor + bads_hurst)

    badchans_details = {"badchans based on variances": bads_var,
                        "badchans based on correlations": bads_cor,
                        "badchans based on hurst exponent": bads_hurst}

    return raw, {"Badchans": badchans_details}

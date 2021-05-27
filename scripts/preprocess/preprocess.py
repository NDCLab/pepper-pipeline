import mne
import autoreject as ar
import pandas as pd

import collections
import sys

# changes: made output dictionary of raw info
def filter(raw, l_freq=0.3, h_freq=40):
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

        return raw_filtered, {"Filter": {
            "Highpass corner frequency": raw_filtered.info["highpass"], 
            "Lowpass corner frequency": raw_filtered.info["lowpass"],
            "Sampling Rate": raw_filtered.info["sfreq"],
            }
        }
    except TypeError:
        print('Type Error')
    except Exception:
        print('Unknown Error')

# changes: takes in epochs only, used ar.fit_transform to get clean epoch object, 
# removed current user_params since epochs are determined by segment
# removed rej_epochs to omit need for raw since epochs_clean has interp'd epochs already
def final_reject_epoch(epochs):
    """Final and automatic rejection of bad epochs
    Parameters
    ----------
    epochs: mne.Epochs object
            instance of the mne.Epochs,

    Returns 
    ----------
    epochs_clean:   mne.Epochs object
                    instance of "cleaned" epochs using autoreject 

    output_dict_finalRej:   dictionary
                            dictionary with epochs droped per channel and channels interpolated
    """
    
    #creates the output dictionary to store the function output
    output_dict_finalRej = collections.defaultdict(dict)
    output_dict_finalRej['interpolatedChannels']=[]

    #fit and clean epoch data using autoreject
    autoRej = ar.AutoReject()
    epochs_clean = autoRej.fit_transform(epochs)  

    #Create a rejection log 
    reject_log = autoRej.get_reject_log(epochs)
    
    # get channel names
    ch_names = epochs.info.ch_names

    #Create a dataframe with the labels that indicate if a channel was interpolated
    df = pd.DataFrame(data=reject_log.labels,columns=ch_names)
    for ch in ch_names:
        if df[df[ch]==2][ch].count()>0:
            output_dict_finalRej['interpolatedChannels'].append(ch)
    
    for ch in ch_names:     
        # store amount of epochs dropped for each channel
        output_dict_finalRej['epochsDropped'][ch]=str(epochs_clean.drop_log.count((ch,)))

    return epochs_clean, output_dict_finalRej

# changes: made user_params to explicit, made epochs to be last return value
def segment_data(raw, tmin, tmax, baseline, picks, reject_tmin, reject_tmax, decim, verbose, preload):
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
                The time interval to consider as “baseline” when applying baseline correction

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

    if raw is None:
        print("Invalid raw object")
        sys.exit(1)

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

    if epochs is None:
        print("Invalid epoch object")
        sys.exit(1)

    if user_params is None:
        print("Invalid user_params dictionary")
        sys.exit(1)

    epochs.plot_sensors(kind=user_params["Segment"]["Plotting Information"]["Kinds"],
                        ch_type=user_params["Segment"]["Plotting Information"]["Ch_type"])

# changes: changed user_params to be explicit,
# Question: should interpolate_data take in cleaned epochs instead of raw? 
# answer: yes, changed orig_raw to epochs
def interpolate_data(epochs, mode, method, reset_bads):
    """Used to return a Raw object that has been interpolated

    Parameters:
    ----------:
    epochs: mne.Epochs
            epochs before interpolation

    mode:


    method:


    reset_bads:

    Throws:
    ----------
    Will throw errors and exit if:
        - Null raw object

    Will throw a warning if there are no bad channels to interpolate

    Returns:
    ----------
    Modified in place epochs object and output dictionary
    """
    if epochs is None:
        print("Null raw objects")
        sys.exit(1)

    epochs.interpolate_bads(mode=mode,
                              method=method,
                              reset_bads=reset_bads
                              )
    return epochs, {"Interpolation": {"Affected_Channels": epochs.info['bads']}}


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
        print("Null raw objects")
        sys.exit(1)

    for title_, data_ in zip(['orig.', 'interp.'], [orig_raw, interp_raw]):
        figure = data_.plot(butterfly=True, color='#00000022', bad_color='r')
        figure.subplots_adjust(top=0.9)
        figure.suptitle(title_, size='xx-large', weight='bold')
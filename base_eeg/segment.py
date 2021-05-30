"""
    Segmentation module to cut the continuous data
    into epochs of data, such that the zero point
    for each epoch is a given marker of interest
"""


import sys
import mne


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

    kind_selected = user_params["Segment"]["Plotting Information"]["Kinds"]
    ch_types = user_params["Segment"]["Plotting Information"]["Ch_type"]

    epochs.plot_sensors(kind=kind_selected, ch_type=ch_types)

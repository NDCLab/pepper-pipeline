"""
    Segmentation module to cut the continuous data
    into epochs of data, such that the zero point
    for each epoch is a given marker of interest
"""


import sys
import mne


def segment_data(raw, user_params):
    """Used to segment continuous data into epochs

    Parameters:
    -----------
    raw:    Raw
            Raw data in FIF format

    user_params:dict
                Dictionary of user manipulated values

    Throws:
    -----------
    Will throw errors and exit if:
        - Null raw object
        - Null user_params dictionary

    Returns:
    -----------
    Will return epochs and a dictionary of epochs information
    during segmentation stage
    """

    if raw is None:
        print("Invalid raw object")
        sys.exit(1)

    if user_params is None:
        print("Invalid user_params dictionary")
        sys.exit(1)

    events, event_id = mne.events_from_annotations(raw)

    epochs = mne.Epochs(raw, events, event_id=event_id,
                        preload=user_params["Segment"]["preload"])

    return epochs, {"Segment": epochs.info}


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

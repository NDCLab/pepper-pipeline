"""
    Interpolation Module to assist on interpolating missing channels
    at the channel/epoch level using a spherical spline interpolation.
    Will also write out to a dictionary to express what has occured
    during this stage of the pipeline.
"""
import sys


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
    if epochs is None:
        print("Null raw objects")
        sys.exit(1)

    epochs.interpolate_bads(mode=mode,
                            method=method,
                            reset_bads=reset_bads
                            )
    return epochs, {"Interpolation": {"Affected": epochs.info['bads']}}


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

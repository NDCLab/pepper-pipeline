"""
    Interpolation Module to assist on interpolating missing channels
    at the channel/epoch level using a spherical spline interpolation.
    Will also write out to a dictionary to express what has occured
    during this stage of the pipeline.
"""
import sys


def interpolate_data(orig_raw, user_params):
    """Used to return a Raw object that has been interpolated

    Parameters:
    ----------:
    orig_raw:   Raw
                Raw data in FIF format. Before interpolation

    output_dict:dict
                Dictionary of parameters provided to the user for
                manipulating specific values within the pipeline

    Throws:
    ----------
    Will throw errors and exit if:
        - Null raw object
        - Null user_params dictionary

    Will throw a warning if there are no bad channels to interpolate

    Returns:
    ----------
    Modified in place raw object and output dictionary
    """
    if orig_raw is None:
        print("Null raw objects")
        sys.exit(1)

    if user_params is None:
        print("Null user_params objects")
        sys.exit(1)

    orig_raw.interpolate_bads(mode=user_params["Interpolation"]["mode"],
                              method=user_params["Interpolation"]["method"],
                              reset_bads=user_params["Interpolation"]["reset_bads"]
                              )
    return {"Interpolation": {"Affected_Channels": orig_raw.info['bads']}}


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

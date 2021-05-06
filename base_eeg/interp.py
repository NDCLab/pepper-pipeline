import sys


def interpolate_data(orig_raw, reset_bads=False):
    """Used to return a Raw object that has been interpolated. 
    
    Parameters:
    ----------:
    orig_raw:   Raw
                Raw data in FIF format. Before interpolation. 
    reset_bads: bool
                If true, removes the bads from info. 
    
    Throws:
    ----------
    Will throw a warning if there are no bad channels to interpolate. 
    In this case, it will simply return from the function. 
    
    Returns:
    ----------
    Instance of a modified Raw, Epochs, or Evoked after interpolation. 
    """
    return orig_raw.copy().interpolate_bads(reset_bads=reset_bads)


def plot_orig_and_interp(orig_raw, interp_raw):
    """Used to plot the difference between the original data and 
    the interpolated data. 
    
    Parameters:
    ----------
    orig_raw:   Raw 
                Raw data in FIF format. Before interpolation. 
    interp_raw: Raw
                Raw data in FIF format. After interpolation. 
    
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


import mne
from collections import namedtuple

# Pipeline name constants
PIPE_NAME = "PEPPER_pipeline"
INTERM = PIPE_NAME + "_intermediate"
FINAL = PIPE_NAME + "_preprocessed"

# Data selection
ALL = ["*"]
OMIT = ""

# Load data error/warning messages
ERROR_KEY = "ERROR: "
MISSING_PATH_MSG = "Missing path. Please check if file or directory exists."
MISSING_DATA_MSG = "Missing data at path. Please check if data at path exists\
 and is a valid BIDS directory."
INVALID_SELECT_PARAM_MSG = "Param is not list. Please populate the selection parameter w/correct values.\
 A valid template can be created using data:write.write_template_params()"
INVALID_EXCEPT_PARAM_MSG = "Param is not list or empty string. Please populate \
 the exception parameter w/correct values. A valid template can be created \
 using data:write.write_template_params()"

# Preprocess error/warning messages
MISSING_MONTAGE_MSG = "This operation requires a montage however the data does \
 not have a montage applied. Add a montage prior to this step via \
 set_montage()."
INVALID_MONTAGE_MSG = f"Invalid value for the 'montage' parameter.\
 Allowed values are: {', '.join(mne.channels.get_builtin_montages())}."
# reference channel error
INVALID_REF_MSG = "The reference electrode is NOT provided or in the list."
# ica error
BAD_CHAN_MSG = "20% or more channels are bad channels and have been removed."
BAD_EPOCH_MSG = "50% or more epochs have been rejected."

# Pipeline default parameters
loaddata = namedtuple('load_data', 'channel_type exit_on_error \
                       overwrite parallel_runs')
setref = namedtuple('set_reference', 'ref_channels')
setmont = namedtuple('set_montage', 'montage')
filtdata = namedtuple('filter_data', 'l_freq h_freq')
identbad = namedtuple('identify_badchans_raw', 'ref_elec_name')
segdata = namedtuple('segment_data', 'tmin tmax baseline picks reject_tmin \
                      reject_tmax decim verbose preload')
interpdata = namedtuple('interpolate_data', 'mode')

DEFAULT_LOAD_PARAMS = loaddata("eeg", False, True, 1)
DEFAULT_REF_PARAMS = setref("Cz")
DEFAULT_MONT_PARAMS = setmont("GSN-HydroCel-129")
DEFAULT_FILT_PARAMS = filtdata(0.3, 40)
DEFAULT_IDENT_PARAMS = identbad("Cz")
DEFAULT_SEG_PARAMS = segdata(-0.2, 0.5, None, None, None, None, 1, False, None)
DEFAULT_INTERP_PARAMS = interpdata("accurate")

CONFIG_FILE_NAME = "input_config.json"
ICA_NAME = "ica_raw"
FINAL_NAME = "final_reject_epoch"
REREF_NAME = "reref_raw"

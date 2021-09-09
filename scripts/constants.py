# Pipeline name constants
PIPE_NAME = "PEPPER"
INTERM = "_intermediate"
FINAL = "_preprocessed"

# Load data error messages/exceptions
MISSING_PATH_MSG = ": Missing Path. Please check if directory exists."
INVALID_DATA_MSG = "Please use mne.io.Raw or mne.Epochs datatype \
    as raw."
INVALID_UPARAM_MSG = "Please use a valid user_param file. A valid template can be \
    created using data:write.write_template_params()"
INVALID_SUBJ_PARAM_MSG = "Please populate the subject parameter w/correct values. \
    A valid template can be created using data:write.write_template_params()"
INVALID_TASK_PARAM_MSG = "Please populate the task parameter w/correct values. \
    A valid template can be created using data:write.write_template_params()"
INVALID_E_SUBJ_MSG = "Please populate the exception subject parameter w/correct values. \
    A valid template can be created using data:write.write_template_params()"
INVALID_E_TASK_MSG = "Please populate the exception task parameter w/correct values. \
    A valid template can be created using data:write.write_template_params()"
INVALID_E_RUN_MSG = "Please populate the exception run parameter w/correct values. \
    A valid template can be created using data:write.write_template_params()"

# Preprocess feature error messages/exceptions
INVALID_FILTER_FREQ_MSG = "'Please use sufficiently seperated floats for \
            l_freq & h_freq."
INVALID_FR_DATA_MSG = "The least populated class in y has only 1 member, which is too\
            few. The minimum number of groups for any class cannot be\
            less than 2."
INVALID_MONTAGE_MSG = "Invalid value for the 'montage' parameter. Allowed values are 'EGI_256', \
        'GSN-HydroCel-128', 'GSN-HydroCel-129', 'GSN-HydroCel-256',\
        'GSN-HydroCel-257', 'GSN-HydroCel-32', 'GSN-HydroCel-64_1.0',\
        'GSN-HydroCel-65_1.0', 'biosemi128', 'biosemi16', 'biosemi160',\
        'biosemi256', 'biosemi32', 'biosemi64', 'easycap-M1', 'easycap-M10',\
        'mgh60', 'mgh70', 'standard_1005', 'standard_1020',\
        'standard_alphabetic', 'standard_postfixed', 'standard_prefixed',\
        'standard_primed', 'artinis-octamon', and 'artinis-brite23'."

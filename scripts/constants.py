import mne

# Pipeline name constants
PIPE_NAME = "PEPPER_pipeline"
INTERM = "_intermediate"
FINAL = "_preprocessed"

# Load data error messages
MISSING_PATH_MSG = "Missing path. Please check if file or directory exists."
MISSING_DATA_MSG = "Missing data at path. Please check if data at path exists\
 and is a valid BIDS directory."
INVALID_DATA_MSG = "Invalid data type. Please use mne.io.Raw or mne.Epochs datatype\
 as raw."
INVALID_UPARAM_MSG = "Invalid pipeline parameter. Please use a valid user_param file. A \
  valid template can be created using data:write.write_template_params()"
INVALID_SUBJ_PARAM_MSG = "Invalid parameter. Please populate the subject parameter w/correct values.\
 A valid template can be created using data:write.write_template_params()"
INVALID_TASK_PARAM_MSG = "Invalid parameter. Please populate the task parameter w/correct values.\
 A valid template can be created using data:write.write_template_params()"
INVALID_E_SUBJ_MSG = "Invalid parameter. Please populate the exception subject \
 parameter w/correct values. A valid template can be created using \
 data:write.write_template_params()"
INVALID_E_TASK_MSG = "Invalid parameter. Please populate the exception task \
 parameter w/correct values. A valid template can be created using \
 data:write.write_template_params()"
INVALID_E_RUN_MSG = "Invalid parameter. Please populate the exception run \
 parameter w/correct values. A valid template can be created using \
 data:write.write_template_params()"

# Preprocess feature error messages/exceptions
MISSING_MONTAGE_MSG = "This operation requires a montage however the data does \
 not have a montage applied. Add a montage prior to this step via \
 set_montage()."
INVALID_MONTAGE_MSG = f"Invalid value for the 'montage' parameter.\
 Allowed values are: {', '.join(mne.channels.get_builtin_montages())}."

# reference channel error
INVALID_REF_MSG = "The reference electrode is NOT provided or in the list."

# write error messages
SKIP_REWRITE_MSG = "File already exists. Skipping write according to 'rewrite'\
 parameter."

# main driver code error messages
CAUGHT_EXCEPTION_SKIP = ": Exception caught in function. Skipping to next\
 subject."
EXIT_MESSAGE = "Pipeline exited according to 'exit_on_error' parameter."

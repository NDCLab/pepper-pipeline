import json
import sys
import os


def read_dict_to_json(dict_array, file, datatype, root):
    if dict_array is None:
        print("Invalid dictionary array", file=sys.stderr)
        sys.exit(1)

    # get file metadata
    subj, ses, task, run = file.subject, file.session, file.task, file.run

    # Creates the directory if it does not exist
    dir_path = f'{root}/raw_derivatives/'.split("/")
    temp = ""
    for sec in dir_path:
        temp += sec + "/"
        # checks that the directory path doesn't already exist
        if not os.path.isdir(temp):
            os.mkdir(temp)  # creates the directory path

    bids_format = 'sub-{}_ses-{}_task-{}_run-{}_{}.json'.format(subj, ses, task, run, datatype)

    with open(f'{root}/raw_derivatives/output_preproc_' + bids_format, 'w') as file:
        str = json.dumps(dict_array, indent=4)
        file.seek(0)
        file.write(str)


def write_eeg_data(raw, func, file, datatype, root):
    """Used to store the modified raw file after each processing step
    Parameters:
    -----------
    raw:    Raw
            Raw data in FIF format
    func:   String
            name of the function
    subject:    String
                name of the subject
    session:    String
                session number
    task:   String
            name of the task
    datatype:   String
                type of data(e.g EEG, MEG, etc )
    root:   String
            directory from where the data was loaded
    """
    # get file metadata
    subj, ses, task, run = file.subject, file.session, file.task, file.run

    # puts together the path to be created
    dir_path = '{}/raw_derivatives/preprocessed/sub-{}/ses-{}/{}/'.format(
        root.split("/")[0], subj, ses, datatype)

    dir_section = dir_path.split("/")

    # creates the directory path
    temp = ""
    for sec in dir_section:
        temp += sec + "/"
        # checks that the directory path doesn't already exist
        if not os.path.isdir(temp):
            os.mkdir(temp)  # creates the directory path

    # saves the raw file in the directory
    raw_savePath = dir_path + 'sub-{}_task-{}_{}_{}'.format(
        subj, task, datatype, func)

    raw.save(raw_savePath, overwrite=True)

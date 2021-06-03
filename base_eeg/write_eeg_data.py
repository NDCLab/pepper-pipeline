import os

def write_eeg_data(raw, func, subject, session, task, datatype, root):
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

    # puts together the path to be created
    dir_path = '{}/raw_derivatives/preprocessed/sub-{}/ses-{}/{}/'.format(root.split("/")[0], subject, session, datatype)
    dir_section = dir_path.split("/")
    
    # creates the directory path
    temp = ""
    for sec in dir_section:
        temp += sec + "/"
        if not os.path.isdir(temp): # checkts that the directory path doesn't already exist
            os.mkdir(temp) # creates the directory path

    # saves the raw file in the directory
    raw_savePath = dir_path + 'ses-{}_task-{}_{}_{}'.format(subject, task, datatype, func)
    raw.save(raw_savePath, overwrite=True)


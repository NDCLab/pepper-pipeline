import pathlib
import os
from mne_bids import BIDSPath, read_raw_bids

def write_eeg_data(raw, func , subject, session, task, datatype, root):
    #puts together the path to be created
    dir_path='{}/raw_derivatives/preprocessed/sub-{}/ses-{}/{}/'.format(root,subject,session,datatype)
    dir_section=dir_path.split("/")
    
    #creates the directory path
    temp=""
    for sec in dir_section :
        temp+=sec+"/"
        if not os.path.isdir(temp): # checkts that the directory path doesn't already exist
            os.mkdir(temp) #creates the directory path

    #saves the raw file in the directory
    raw_savePath =dir_path+'ses-{}_task-{}_{}_{}}'.format(subject,task,datatype,func)
    raw.save(raw_savePath,overwrite=True)


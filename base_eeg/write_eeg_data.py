import pathlib
import os
from mne_bids import BIDSPath, read_raw_bids

def write_eeg_data(func):
    bids_root = pathlib.Path('CMI/rawdata')
    bids_path = BIDSPath(subject='NDARAB793GL3',session="01",run='01', task='ContrastChangeBlock1', datatype='eeg', root=bids_root)
    raw = read_raw_bids(bids_path)
    
    #puts together the path to be created
    dir_path='CMI/raw_derivatives/preprocessed/sub-{}/ses-{}/'.format(bids_path.subject,bids_path.session)
    dir_section=dir_path.split("/")
    dir_section
    
    #creates the directory path
    temp=""
    for sec in dir_section :
        temp+=sec+"/"
        if not os.path.isdir(temp): # checkts that the directory path doesn't already exist
            os.mkdir(temp) #creates the directory path

    #saves the raw file in the directory
    raw_savePath =dir_path+'ses-{}_task-{}_eeg_{}}'.format(bids_path.subject,bids_path.task,func)
    raw.save(raw_savePath,overwrite=True)


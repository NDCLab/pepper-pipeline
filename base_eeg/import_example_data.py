import mne
import mne_bids
import numpy as np
import os
import pathlib
import pandas as pd

bids_root = pathlib.Path.cwd() / 'BIDS'

# TODO: load and merge phenotype metadata files from all batches of data
meta_data = pd.read_csv(pathlib.Path.cwd() / 'HBN_R2_1_Pheno.csv')

# mapping of event codes to block starts
block_mapping = {'90': 'RestingState',
                 '91': 'SequenceLearning',
                 '92': 'SymbolSearch',
                 '93': 'SurrSuppBlock1',
                 '94': 'ContrastChangeBlock1',
                 '95': 'ContrastChangeBlock2',
                 '96': 'ContrastChangeBlock3',
                 '97': 'SurrSuppBlock2',
                 '81': 'Video1',
                 '82': 'Video2',
                 '83': 'Video3',
                 '84': 'Video4'}

# TODO: double check that the sex mapping is correct
sex_mapping = {0: 'F',
               1: 'M'}

input_path = 'NDARAB793GL3.mff'

participant_code = pathlib.Path(input_path).stem
meta_data_rows = (meta_data['EID'] == participant_code).sum()
# fetch metadata
if meta_data_rows < 1:
    raise Exception('Participant not in metadata')
elif meta_data_rows > 1:
    raise Exception('Participant in metadata more than once')
else:
    participant_age = float(meta_data.loc[meta_data['EID'] == participant_code, 'Age'])
    participant_sex = sex_mapping[int(meta_data.loc[meta_data['EID'] == participant_code, 'Sex'])]

# here, MNE was deciding to exclude channel 90 if not set to explicitly not exclude any channels
raw = mne.io.read_raw_egi(input_path, preload=True, verbose=True, exclude=[])

# add metadata
raw.info['line_freq'] = 60

# associate montage
raw.rename_channels({'E129': 'Cz'})
raw.set_montage('GSN-HydroCel-129')

# set the reference channel
raw.set_eeg_reference(ref_channels=['Cz'], ch_type='eeg')

# get the mapping from channel name to integer event ID
event_keys = raw.event_id
# extract the events from the 'STI 014' composite channel
events = mne.find_events(raw, stim_channel='STI 014', shortest_event=1)
# reverse the dict so that the keys are items and items are keys, stripping any trailing whitespace from the event strings
event_map = dict((v, k.rstrip()) for k, v in event_keys.items())
# use the event numpy array with integers, and the event_map going from integer to string names, to create annotations with the correct labels
event_annotations = mne.annotations_from_events(events=events, sfreq=raw.info['sfreq'],
                                                orig_time=raw.info['meas_date'], event_desc=event_map)
# add the event annotations to the existing annotations
raw.set_annotations(raw.annotations + event_annotations)
# keep only the EEG channels, removing the stimulation channels
raw.pick_types(eeg=True)

# get the time and code for each annotation
annotation_codes = [(a['onset'], a['description']) for a in raw.annotations]

# reduce to only the annotations that indicate block starts
block_annotations = [a for a in annotation_codes if np.isin(a[1], list(block_mapping))]
block_df = pd.DataFrame(data=block_annotations, columns=['start_time', 'code'])

# each block end is the time of the next block start
block_df['end_time'] = np.roll(block_df['start_time'], -1)

# extend the length of the first and last block periods to the start / end of the recording
block_df.loc[0, 'start_time'] = 0
block_df.loc[block_df.index[-1], 'end_time'] = raw.times[-1]

# subtract an amount of time equal to 1 sample from each end time
# to avoid the next annotation from being included in cropped data
block_df['end_time'] = block_df['end_time'] - (1 / raw.info['sfreq'])

block_df['run'] = block_df.groupby('code').cumcount() + 1

# write out each block as a separate file
for b in block_df.index:
    task_name = block_mapping[block_df.loc[b, 'code']]
    run_number = str(block_df.loc[b, 'run']).zfill(2)

    # crop & save as .fif
    raw_cropped = raw.copy().crop(tmin=block_df.loc[b, 'start_time'],
                                  tmax=block_df.loc[b, 'end_time'],
                                  include_tmax=False)
    temp_path = pathlib.Path.cwd() / f'{task_name}_{run_number}_raw.fif'
    raw_cropped.save(temp_path, overwrite=True)

    # read .fif back and write BIDS
    raw_temp = mne.io.read_raw_fif(temp_path)

    bids_path = mne_bids.BIDSPath(subject=participant_code,
                                  session='01',
                                  task=task_name,
                                  run=run_number,
                                  datatype='eeg',
                                  root=bids_root)

    mne_bids.write_raw_bids(raw_temp, bids_path, format='BrainVision', overwrite=True)

    # update sidecar values
    bids_path.update(suffix='eeg', extension='.json')
    eeg_sidecar_values = {'EEGReference': 'Cz'}
    mne_bids.update_sidecar_json(bids_path, eeg_sidecar_values)

    # remove the temporary FIF
    os.remove(temp_path)

# update participants.tsv
participant_data = pd.read_csv(bids_root / 'participants.tsv', sep='\t')
participant_data.loc[participant_data['participant_id'] == f'sub-{participant_code}', 'age'] = participant_age
participant_data.loc[participant_data['participant_id'] == f'sub-{participant_code}', 'sex'] = participant_sex
participant_data.to_csv(bids_root / 'participants.tsv', sep='\t')

import datetime
import glob
import logging
import mne
import mne_bids
import pathlib
import pandas as pd
import scipy
import tarfile

# TODO: Check if multiple runs of a given task are present in the HBN dataset
# TODO: Add progress bar

# Format the Child Mind Institute (CMI) Healthy Brain Network (HBN) data in BIDS format
# http://fcon_1000.projects.nitrc.org/indi/cmi_healthy_brain_network/sharing_neuro.html

# utility function:
# from: https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-a-list-of-lists
def flatten(t):
    return [item for sublist in t for item in sublist]

sourcedata_root = pathlib.Path.cwd() / '../CMI/sourcedata'
bids_root = pathlib.Path.cwd() / '../CMI/rawdata'

launch_time = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
logging.basicConfig(filename=f'import_cmi_hbn_data_{launch_time}.log',
                    format='%(asctime)s:%(levelname)s:%(message)s',
                    level=logging.DEBUG)

# whether to overwrite data that already exists
overwrite = False

# assemble list of files to process
releases = glob.glob(f'{sourcedata_root}/release-*')
pheno_paths = flatten([glob.glob(f'{release}/HBN_*_Pheno.csv') for release in releases])
pheno_data = pd.concat([pd.read_csv(path) for path in pheno_paths])

eeg_file_paths = flatten([glob.glob(f'{release}/eeg/*.tar.gz') for release in releases])

# the original task names are not BIDS compliant, as they contain dashes and underscores
# map them to compliant names
task_mapping = {'RestingState': 'restingState',
                'vis_learn': 'visLearn',
                'WISC_ProcSpeed': 'wiscProcSpeed',
                'SurroundSupp_Block1': 'surroundSuppBlock1',
                'SurroundSupp_Block2': 'surroundSuppBlock2',
                'SAIIT_2AFC_Block1': 'saitt2afcBlock1',
                'SAIIT_2AFC_Block2': 'saitt2afcBlock2',
                'SAIIT_2AFC_Block3': 'saitt2afcBlock3',
                'Video-FF': 'videoFF',
                'Video-DM': 'videoDM',
                'Video-WK': 'videoWK',
                'Video-TP': 'videoTP'}

sex_mapping = {0: 'M',
               1: 'F'}

channel_names = [f'E{c}' for c in range(1, 129)]
channel_names.append('Cz')

for input_path in eeg_file_paths:

    print(f'Processing {input_path}')

    participant_code = pathlib.Path(input_path).stem.split('.')[0]
    pheno_data_rows = (pheno_data['EID'] == participant_code).sum()
    # fetch metadata
    if pheno_data_rows < 1:
        raise Exception('Participant not in metadata')
    elif pheno_data_rows > 1:
        raise Exception('Participant in metadata more than once')
    else:
        participant_age = float(pheno_data.loc[pheno_data['EID'] == participant_code, 'Age'])
        participant_sex = sex_mapping[int(pheno_data.loc[pheno_data['EID'] == participant_code, 'Sex'])]


    # Get the .mat versions of needed tasks
    with tarfile.open(input_path) as tar_data:
        tar_contents = tar_data.getnames()
        for task in task_mapping.keys():
            task_filename = f'{participant_code}/EEG/raw/mat_format/{task}.mat'

            bids_path = mne_bids.BIDSPath(subject=participant_code,
                                          session='01',
                                          task=task_mapping[task],
                                          run=1,
                                          datatype='eeg',
                                          root=bids_root)

            if not overwrite and len(bids_path.match()) != 0:
                # skip the file since we've already processsed it
                logging.info('Participant %s Task %s already present, skipping', participant_code, task)
            elif task_filename not in tar_contents:
                logging.warning('Participant %s Task %s is missing', participant_code, task)
            else:
                task_file_obj = tar_data.extractfile(task_filename)
                mat_data = scipy.io.loadmat(task_file_obj, simplify_cells = True)
                EEG = mat_data['EEG']
                info = mne.create_info(channel_names, ch_types='eeg', sfreq=EEG['srate'])
                info['line_freq'] = 60
                raw = mne.io.RawArray(EEG['data'], info)
                raw.set_montage('GSN-HydroCel-129')
                raw.set_eeg_reference(ref_channels=['Cz'], ch_type='eeg')

                # create annotations from events
                event_onset_seconds = [(event['sample'] - 1) / EEG['srate'] for event in EEG['event']]
                event_duration_seconds = [event['duration'] / EEG['srate'] for event in EEG['event']]
                event_descriptions = [event['type'].strip() for event in EEG['event']]
                annotations = mne.Annotations(onset=event_onset_seconds,
                                              duration=event_duration_seconds,
                                              description=event_descriptions)
                raw.set_annotations(annotations)

                mne_bids.write_raw_bids(raw, bids_path, format='BrainVision', overwrite=overwrite, allow_preload=True)

                # update sidecar values
                bids_path.update(suffix='eeg', extension='.json')
                eeg_sidecar_values = {'EEGReference': 'Cz'}
                mne_bids.update_sidecar_json(bids_path, eeg_sidecar_values)

    # update participants.tsv
    participant_data = pd.read_csv(bids_root / 'participants.tsv', sep='\t', na_filter=False)
    participant_data.loc[participant_data['participant_id'] == f'sub-{participant_code}', 'age'] = participant_age
    participant_data.loc[participant_data['participant_id'] == f'sub-{participant_code}', 'sex'] = participant_sex
    participant_data.to_csv(bids_root / 'participants.tsv', sep='\t', index=False)

from scripts.data import write, load

import pytest
from pathlib import Path

import mne_bids
import pandas as pd


@pytest.fixture
def root():
    root = Path("CMI/rawdata")
    return root


@pytest.fixture
def default_params(root):
    default_params = write.write_template_params(root)
    return default_params


@pytest.fixture
def avail_subjects(root):
    avail_subj = mne_bids.get_entity_vals(root, 'subject')
    return avail_subj


@pytest.fixture
def subj_to_files(avail_subjects, root):
    # create a dictionary of subjects and corresponding files
    subjects = {}
    for subject in avail_subjects:
        bids_path = mne_bids.BIDSPath(subject=subject, root=root)

        files = bids_path.match()
        scans_file = [f for f in files if "scans" in f.suffix][0]
        scans_info = pd.read_csv(scans_file, sep='\t')
        subjects[subject] = scans_info["filename"].to_list()

    return subjects


def test_select_all(default_params, avail_subjects, subj_to_files):
    # Load data using the default parameters
    data = load.load_files(default_params["load_data"])

    # check if the number of files loaded matches
    # the number of all files available
    count = 0
    for subject in avail_subjects:
        count += len(subj_to_files[subject])
    assert len(data) == count


def test_select_participants(default_params, subj_to_files):
    # select participants (make this a random selection?)
    selected_participants = ["NDARAB793GL3"]
    default_params["load_data"]["subjects"] = selected_participants

    # Load data using the selected participants
    data = load.load_files(default_params["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected subjects
    count = 0
    for subject in selected_participants:
        count += len(subj_to_files[subject])
    assert len(data) == count


def test_select_tasks(default_params, avail_subjects, subj_to_files):
    # select tasks (make this a random selection?)
    selected_tasks = ["ContrastChangeBlock1"]
    default_params["load_data"]["tasks"] = selected_tasks

    # Load data using the selected task
    data = load.load_files(default_params["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected task
    count = 0
    for subject in avail_subjects:
        for file in subj_to_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in selected_tasks:
                count += 1
    assert len(data) == count


def test_select_particip_tasks(default_params, avail_subjects, subj_to_files):
    # select subjects & tasks (randomize?)
    selected_participants = ["NDARAB793GL3"]
    selected_tasks = ["ContrastChangeBlock1"]

    default_params["load_data"]["subjects"] = selected_participants
    default_params["load_data"]["tasks"] = selected_tasks

    # Load data using the selected subjects & tasks
    data = load.load_files(default_params["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected tasks & subjects
    count = 0
    for subject in selected_participants:
        for file in subj_to_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in selected_tasks:
                count += 1
    assert len(data) == count


def test_except_subjects(default_params , avail_subjects, subj_to_files):
    # select excluded subjects (randomize?)
    exclude_part = ["NDARAB793GL3"]
    default_params["load_data"]["exceptions"]["subjects"] = exclude_part

    # Load data using the excluded subjects
    data = load.load_files(default_params["load_data"])

    count = 0

    # get the excluded subset of subjects
    

    # check if the number of files loaded matches
    # the total number of all subjects apart from the excluded
    for subject in avail_subjects:
        for file in avail_subjects[subject]:
            # if file.task in selected_tasks:
            count += 1
    assert len(data) == count


'''
def test_except_tasks(default_params, avail_subjects):
    return


def test_except_subj_tasks(default_params, avail_subjects):
    return


def test_except_subj_runs(default_params, avail_subjects):
    return


def test_except_subj_tasks_runs(default_params, avail_subjects):
    return


def test_select_particip_tasks_except_subjects(default_params, avail_subjects):
    return


def test_select_particip_tasks_except_tasks(default_params, avail_subjects):
    return


def test_select_particip_tasks_except_subj_tasks(default_params, avail_subjects):
    return


def test_select_particip_tasks_except_subj_tasks_runs(default_params, avail_subjects):
    return


def test_missing_subj(default_params, avail_subjects):
    return


def test_missing_tasks(default_params, avail_subjects):
    return


def test_missing_exceptions(default_params, avail_subjects):
    return
'''
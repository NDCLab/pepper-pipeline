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


def test_select_subjects(default_params, subj_to_files):
    # select participants (make this a random selection?)
    selected_subjects = ["NDARAB793GL3"]
    default_params["load_data"]["subjects"] = selected_subjects

    # Load data using the selected participants
    data = load.load_files(default_params["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected subjects
    count = 0
    for subject in selected_subjects:
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


def test_select_subjects_tasks(default_params, subj_to_files):
    # select subjects & tasks (randomize?)
    selected_subjects = ["NDARAB793GL3"]
    selected_tasks = ["ContrastChangeBlock1"]

    default_params["load_data"]["subjects"] = selected_subjects
    default_params["load_data"]["tasks"] = selected_tasks

    # Load data using the selected subjects & tasks
    data = load.load_files(default_params["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected tasks & subjects
    count = 0
    for subject in selected_subjects:
        for file in subj_to_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in selected_tasks:
                count += 1
    assert len(data) == count


def test_except_subjects(default_params, avail_subjects, subj_to_files):
    # select excluded subjects (randomize?)
    exclude_subject = set(["NDARAB793GL3"])
    default_params["load_data"]["exceptions"]["subjects"] = exclude_subject
    default_params["load_data"]["exceptions"]["tasks"] = ["*"]
    default_params["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the excluded subjects
    data = load.load_files(default_params["load_data"])

    # get the excluded subset of subjects
    exclude_set = set(avail_subjects).difference(exclude_subject)

    # check if the number of files loaded matches
    # the total number of all subjects apart from the excluded
    count = 0
    for subject in exclude_set:
        count += len(subj_to_files[subject])
    assert len(data) == count


def test_except_tasks(default_params, avail_subjects):
    # select excluded tasks (randomize?)
    exclude_task = set(["ContrastChangeBlock1"])
    default_params["load_data"]["exceptions"]["subjects"] = ["*"]
    default_params["load_data"]["exceptions"]["tasks"] = exclude_task
    default_params["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the excluded tasks
    data = load.load_files(default_params["load_data"])

    # check if the number of files loaded matches
    # the total number of all tasks apart from the excluded
    count = 0
    for subject in avail_subjects:
        for file in subj_to_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in exclude_task:
                continue
            count += 1
    assert len(data) == count


def test_except_subjects_tasks(default_params):
    # select excluded subjects & tasks (randomize?)
    exclude_subject = set(["NDARAB793GL3"])
    exclude_task = set(["ContrastChangeBlock1"])

    default_params["load_data"]["exceptions"]["subjects"] = exclude_subject
    default_params["load_data"]["exceptions"]["tasks"] = exclude_task
    default_params["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the excluded subjects & tasks
    data = load.load_files(default_params["load_data"])

    # check if the number of files loaded matches
    # the total number of all subjects & tasks apart from the excluded
    count = 0
    for subject in exclude_subject:
        for file in subj_to_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in exclude_task:
                continue
            count += 1
    assert len(data) == count


def test_except_subjects_tasks_runs(default_params):
    # select excluded subjects, tasks, & runs (randomize?)
    exclude_subject = set(["NDARAB793GL3"])
    exclude_task = set(["ContrastChangeBlock1"])
    exclude_run = set(["01"])

    default_params["load_data"]["exceptions"]["subjects"] = exclude_subject
    default_params["load_data"]["exceptions"]["tasks"] = exclude_task
    default_params["load_data"]["exceptions"]["runs"] = exclude_run

    # Load data using the excluded subjects & tasks
    data = load.load_files(default_params["load_data"])

    # check if the number of files loaded matches
    # the total number of all subjects & tasks apart from the excluded
    count = 0
    for subject in exclude_subject:
        for file in subj_to_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            # split and find run of file (TODO: need to BIDSIFY)
            run_id = [s for s in file.split("_") if "run" in s][0]
            run = [s for s in run_id.split("-") if s != "run"][0]

            if task in exclude_task and run in exclude_run:
                continue
            count += 1
    assert len(data) == count


def test_except_all(default_params):
    # select all for exceptions
    default_params["load_data"]["exceptions"]["subjects"] = ["*"]
    default_params["load_data"]["exceptions"]["tasks"] = ["*"]
    default_params["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the excluded subjects & tasks
    data = load.load_files(default_params["load_data"])

    # assert nothing is selected
    assert len(data) == 0


def test_select_subjects_tasks_except_subjects(default_params):
    # select subjects (randomize?)
    selected_subjects = ["NDARAB793GL3"]
    selected_tasks = ["ContrastChangeBlock1"]
    default_params["load_data"]["subjects"] = selected_subjects
    default_params["load_data"]["tasks"] = selected_tasks

    # select excluded subjects (randomize?)
    exclude_subject = set(["NDARAB793GL3"])
    default_params["load_data"]["exceptions"]["subjects"] = exclude_subject
    default_params["load_data"]["exceptions"]["tasks"] = ["*"]
    default_params["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the selected subjects & tasks
    data = load.load_files(default_params["load_data"])

    # get the excluded subset of subjects
    subjects_diff = set(selected_subjects).difference(exclude_subject)

    # check if the number of files loaded matches
    # the total number of files for all selected subjects excluding exceptions
    count = 0
    for subject in subjects_diff:
        for file in subj_to_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in selected_tasks:
                count += 1
    assert len(data) == count


def test_select_subjects_tasks_except_tasks(default_params):
    # select subjects & tasks (randomize?)
    selected_subjects = ["NDARAB793GL3"]
    selected_tasks = ["ContrastChangeBlock1"]
    default_params["load_data"]["subjects"] = selected_subjects
    default_params["load_data"]["tasks"] = selected_tasks

    # select excluded subjects (randomize?)
    exclude_task = ["ContrastChangeBlock1"]
    default_params["load_data"]["exceptions"]["subjects"] = ["*"]
    default_params["load_data"]["exceptions"]["tasks"] = exclude_task
    default_params["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the selected subjects & tasks
    data = load.load_files(default_params["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected subjects excluding exceptions
    count = 0
    for subject in selected_subjects:
        for file in subj_to_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in exclude_task:
                continue
            count += 1
    assert len(data) == count


def test_select_subjects_tasks_except_subj_tasks(default_params):
    # select subjects & tasks (randomize?)
    selected_subjects = ["NDARAB793GL3"]
    selected_tasks = ["ContrastChangeBlock1"]
    default_params["load_data"]["subjects"] = selected_subjects
    default_params["load_data"]["tasks"] = selected_tasks

    # select excluded subjects (randomize?)
    exclude_subject = ["NDARAB793GL3"]
    exclude_task = ["ContrastChangeBlock1"]
    default_params["load_data"]["exceptions"]["subjects"] = exclude_subject
    default_params["load_data"]["exceptions"]["tasks"] = exclude_task
    default_params["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the selected subjects & tasks
    data = load.load_files(default_params["load_data"])

    # get the excluded subset of subjects
    subjects_diff = set(selected_subjects).difference(set(exclude_subject))

    # check if the number of files loaded matches
    # the total number of files for all selected subjects excluding exceptions
    count = 0
    for subject in subjects_diff:
        for file in subj_to_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in exclude_task:
                continue
            count += 1
    assert len(data) == count


def test_select_subjects_tasks_except_subj_tasks_runs(default_params):
    # select subjects & tasks (randomize?)
    selected_subjects = ["NDARAB793GL3"]
    selected_tasks = ["ContrastChangeBlock1"]
    default_params["load_data"]["subjects"] = selected_subjects
    default_params["load_data"]["tasks"] = selected_tasks

    # select excluded subjects (randomize?)
    exclude_subject = ["NDARAB793GL3"]
    exclude_task = ["ContrastChangeBlock1"]
    exclude_run = ["01"]
    default_params["load_data"]["exceptions"]["subjects"] = exclude_subject
    default_params["load_data"]["exceptions"]["tasks"] = exclude_task
    default_params["load_data"]["exceptions"]["runs"] = exclude_run

    # Load data using the selected subjects & tasks
    data = load.load_files(default_params["load_data"])

    # get the excluded subset of subjects
    subjects_diff = set(selected_subjects).difference(set(exclude_subject))

    # check if the number of files loaded matches
    # the total number of files for all selected subjects excluding exceptions
    count = 0
    for subject in subjects_diff:
        for file in subj_to_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            # split and find run of file (TODO: need to BIDSIFY)
            run_id = [s for s in file.split("_") if "run" in s][0]
            run = [s for s in run_id.split("-") if s != "run"][0]

            if task in exclude_task and run in exclude_run:
                continue
            count += 1
    assert len(data) == count


def test_missing_subjects(default_params):
    # input invalid value for subjects
    default_params["load_data"]["subjects"] = ""

    # Load data using the invalid field
    with pytest.raises(Exception):
        load.load_files(default_params["load_data"])
        assert True


def test_missing_tasks(default_params):
    # input invalid value for tasks
    default_params["load_data"]["tasks"] = ""

    # Load data using the invalid field
    with pytest.raises(Exception):
        load.load_files(default_params["load_data"])
        assert True


def test_missing_except_subjects(default_params, avail_subjects):
    # input invalid value for tasks
    default_params["load_data"]["exceptions"]["subjects"] = ""
    default_params["load_data"]["exceptions"]["tasks"] = ["*"]
    default_params["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the invalid field
    with pytest.raises(Exception):
        load.load_files(default_params["load_data"])
        assert True


def test_missing_except_tasks(default_params):
    # input invalid value for tasks
    default_params["load_data"]["exceptions"]["subjects"] = ["*"]
    default_params["load_data"]["exceptions"]["tasks"] = ""
    default_params["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the invalid field
    with pytest.raises(Exception):
        load.load_files(default_params["load_data"])
        assert True


def test_missing_except_runs(default_params):
    # input invalid value for tasks
    default_params["load_data"]["exceptions"]["subjects"] = ["*"]
    default_params["load_data"]["exceptions"]["tasks"] = ["*"]
    default_params["load_data"]["exceptions"]["runs"] = ""

    # Load data using the invalid field
    with pytest.raises(Exception):
        load.load_files(default_params["load_data"])
        assert True


def test_missing_data(default_params, tmp_path):
    # create empty and temporary directory
    empty_data = tmp_path / "empty"
    empty_data.mkdir()

    # input invalid value for tasks
    default_params["load_data"]["root"] = empty_data

    # Load data using the invalid field
    with pytest.raises(Exception):
        load.load_files(default_params["load_data"])
        assert True

from scripts.data import write, load

import pytest

from pathlib import Path
import os

import mne_bids
import pandas as pd


@pytest.fixture
def root():
    root = Path("CMI/rawdata")
    return root


@pytest.fixture
def default_param(root):
    default_param = write.write_template_params(root)
    return default_param


@pytest.fixture
def avail_subj(root):
    avail_subj = mne_bids.get_entity_vals(root, 'subject')
    return avail_subj


@pytest.fixture
def subj_files(avail_subj, root):
    # create a dictionary of subjects and corresponding files
    subjects = {}
    for subject in avail_subj:
        bids_path = mne_bids.BIDSPath(subject=subject, root=root)

        files = bids_path.match()
        scans_file = [f for f in files if "scans" in f.suffix][0]

        scans_info = pd.read_csv(scans_file, sep='\t')
        filenames = scans_info["filename"].to_list()

        cleaned_filenames = []
        for file in filenames:
            _, tail = os.path.split(file)
            cleaned_filenames.append(tail)
        subjects[subject] = cleaned_filenames
    return subjects


def test_select_all(default_param, avail_subj, subj_files):
    # Load data using the default parameters
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the number of all files available
    count = 0
    for subject in avail_subj:
        count += len(subj_files[subject])
    assert len(data) == count


def test_select_subj(default_param, subj_files):
    # select participants (make this a random selection?)
    selected_subjects = ["NDARAB793GL3"]
    default_param["load_data"]["subjects"] = selected_subjects

    # Load data using the selected participants
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected subjects
    count = 0
    for subject in selected_subjects:
        count += len(subj_files[subject])
    assert len(data) == count


def test_select_task(default_param, avail_subj, subj_files):
    # select tasks (make this a random selection?)
    selected_tasks = ["ContrastChangeBlock1"]
    default_param["load_data"]["tasks"] = selected_tasks

    # Load data using the selected task
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected task
    count = 0
    for subject in avail_subj:
        for file in subj_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in selected_tasks:
                count += 1
    assert len(data) == count


def test_select_subj_task(default_param, subj_files):
    # select subjects & tasks (randomize?)
    selected_subjects = ["NDARAB793GL3"]
    selected_tasks = ["ContrastChangeBlock1"]

    default_param["load_data"]["subjects"] = selected_subjects
    default_param["load_data"]["tasks"] = selected_tasks

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected tasks & subjects
    count = 0
    for subject in selected_subjects:
        for file in subj_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in selected_tasks:
                count += 1
    assert len(data) == count


def test_except_subj(default_param, avail_subj, subj_files):
    # select excluded subjects (randomize?)
    exc_subj = ["NDARAB793GL3"]
    default_param["load_data"]["exceptions"]["subjects"] = exc_subj
    default_param["load_data"]["exceptions"]["tasks"] = ["*"]
    default_param["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the excluded subjects
    data = load.load_files(default_param["load_data"])

    # get the excluded subset of subjects
    subjects_diff = set(avail_subj).difference(set(exc_subj))

    # check if the number of files loaded matches
    # the total number of all subjects apart from the excluded
    count = 0
    for subject in subjects_diff:
        count += len(subj_files[subject])
    assert len(data) == count


def test_except_task(default_param, avail_subj, subj_files):
    # select excluded tasks (randomize?)
    exc_task = ["ContrastChangeBlock1"]
    default_param["load_data"]["exceptions"]["subjects"] = ["*"]
    default_param["load_data"]["exceptions"]["tasks"] = exc_task
    default_param["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the excluded tasks
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of all tasks apart from the excluded
    count = 0
    for subject in avail_subj:
        for file in subj_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in exc_task:
                continue
            count += 1
    assert len(data) == count


def test_except_subj_task(default_param, avail_subj, subj_files):
    # select excluded subjects & tasks (randomize?)
    exc_subj = ["NDARAB793GL3"]
    exc_task = ["ContrastChangeBlock1"]

    default_param["load_data"]["exceptions"]["subjects"] = exc_subj
    default_param["load_data"]["exceptions"]["tasks"] = exc_task
    default_param["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the excluded subjects & tasks
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of all subjects & tasks apart from the excluded
    count = 0
    for subject in avail_subj:
        for file in subj_files[subject]:

            file_vals = file.split("_")

            # split and find subject of file (TODO: need to BIDSIFY)
            sub_id = [s for s in file_vals if "sub" in s][0]
            sub = [s for s in sub_id.split("-") if s != "sub"][0]

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if sub in exc_subj and task in exc_task:
                continue
            count += 1
    assert len(data) == count


def test_except_subj_task_run(default_param, avail_subj, subj_files):
    # select excluded subjects, tasks, & runs (randomize?)
    exc_subj = ["NDARAB793GL3"]
    exc_task = ["ContrastChangeBlock1"]
    exc_run = ["01"]

    default_param["load_data"]["exceptions"]["subjects"] = exc_subj
    default_param["load_data"]["exceptions"]["tasks"] = exc_task
    default_param["load_data"]["exceptions"]["runs"] = exc_run

    # Load data using the excluded subjects & tasks
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of all subjects & tasks apart from the excluded
    count = 0
    for subject in avail_subj:
        for file in subj_files[subject]:

            file_vals = file.split("_")

            # split and find subject of file (TODO: need to BIDSIFY)
            sub_id = [s for s in file_vals if "sub" in s][0]
            sub = [s for s in sub_id.split("-") if s != "sub"][0]

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file_vals if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            # split and find run of file (TODO: need to BIDSIFY)
            run_id = [s for s in file_vals if "run" in s][0]
            run = [s for s in run_id.split("-") if s != "run"][0]

            if sub in exc_subj and task in exc_task and run in exc_run:
                continue
            count += 1
    assert len(data) == count


def test_except_all(default_param):
    # select all for exceptions
    default_param["load_data"]["exceptions"]["subjects"] = ["*"]
    default_param["load_data"]["exceptions"]["tasks"] = ["*"]
    default_param["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the excluded subjects & tasks
    data = load.load_files(default_param["load_data"])

    # assert nothing is selected
    assert len(data) == 0


def test_select_subj_task_except_subj(default_param, subj_files):
    # select subjects (randomize?)
    selected_subjects = ["NDARAB793GL3"]
    selected_tasks = ["ContrastChangeBlock1"]
    default_param["load_data"]["subjects"] = selected_subjects
    default_param["load_data"]["tasks"] = selected_tasks

    # select excluded subjects (randomize?)
    exc_subj = ["NDARAB793GL3"]
    default_param["load_data"]["exceptions"]["subjects"] = exc_subj
    default_param["load_data"]["exceptions"]["tasks"] = ["*"]
    default_param["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # get the excluded subset of subjects
    subjects_diff = set(selected_subjects).difference(set(exc_subj))

    # check if the number of files loaded matches
    # the total number of files for all selected subjects excluding exceptions
    count = 0
    for subject in subjects_diff:
        for file in subj_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in selected_tasks:
                count += 1
    assert len(data) == count


def test_select_subj_task_except_task(default_param, subj_files):
    # select subjects & tasks (randomize?)
    selected_subjects = ["NDARAB793GL3"]
    selected_tasks = ["ContrastChangeBlock1"]
    default_param["load_data"]["subjects"] = selected_subjects
    default_param["load_data"]["tasks"] = selected_tasks

    # select excluded subjects (randomize?)
    exc_task = ["ContrastChangeBlock1"]
    default_param["load_data"]["exceptions"]["subjects"] = ["*"]
    default_param["load_data"]["exceptions"]["tasks"] = exc_task
    default_param["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected subjects excluding exceptions
    count = 0
    for subject in selected_subjects:
        for file in subj_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in exc_task:
                continue
            elif task in selected_tasks:
                count += 1
    assert len(data) == count


def test_sel_subj_task_except_subj_task(default_param, avail_subj, subj_files):
    # select subjects & tasks (randomize?)
    selected_subjects = ["NDARAB793GL3"]
    selected_tasks = ["ContrastChangeBlock1"]
    default_param["load_data"]["subjects"] = selected_subjects
    default_param["load_data"]["tasks"] = selected_tasks

    # select excluded subjects (randomize?)
    exc_subj = ["NDARAB793GL3"]
    exc_task = ["ContrastChangeBlock1"]
    default_param["load_data"]["exceptions"]["subjects"] = exc_subj
    default_param["load_data"]["exceptions"]["tasks"] = exc_task
    default_param["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected subjects excluding exceptions
    count = 0
    for subject in avail_subj:
        for file in subj_files[subject]:

            file_vals = file.split("_")

            # split and find subject of file (TODO: need to BIDSIFY)
            sub_id = [s for s in file_vals if "sub" in s][0]
            sub = [s for s in sub_id.split("-") if s != "sub"][0]

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if sub in exc_subj and task in exc_task:
                continue
            elif task in selected_tasks:
                count += 1
    assert len(data) == count


def test_select_subj_task_except_subj_task_run(default_param, subj_files):
    # select subjects & tasks (randomize?)
    selected_subjects = ["NDARAB793GL3"]
    selected_tasks = ["ContrastChangeBlock1"]
    default_param["load_data"]["subjects"] = selected_subjects
    default_param["load_data"]["tasks"] = selected_tasks

    # select excluded subjects (randomize?)
    exc_subj = ["NDARAB793GL3"]
    exc_task = ["ContrastChangeBlock1"]
    exc_run = ["01"]
    default_param["load_data"]["exceptions"]["subjects"] = exc_subj
    default_param["load_data"]["exceptions"]["tasks"] = exc_task
    default_param["load_data"]["exceptions"]["runs"] = exc_run

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected subjects excluding exceptions
    count = 0
    for subject in selected_subjects:
        for file in subj_files[subject]:

            file_vals = file.split("_")

            # split and find subject of file (TODO: need to BIDSIFY)
            sub_id = [s for s in file_vals if "sub" in s][0]
            sub = [s for s in sub_id.split("-") if s != "sub"][0]

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            # split and find run of file (TODO: need to BIDSIFY)
            run_id = [s for s in file.split("_") if "run" in s][0]
            run = [s for s in run_id.split("-") if s != "run"][0]

            if sub in exc_subj and task in exc_task and run in exc_run:
                continue
            elif task in selected_tasks:
                count += 1
    assert len(data) == count


def test_missing_subj(default_param):
    # input invalid value for subjects
    default_param["load_data"]["subjects"] = ""

    # Load data using the invalid field
    with pytest.raises(TypeError):
        load.load_files(default_param["load_data"])
        assert True


def test_missing_task(default_param):
    # input invalid value for tasks
    default_param["load_data"]["tasks"] = ""

    # Load data using the invalid field
    with pytest.raises(TypeError):
        load.load_files(default_param["load_data"])
        assert True


def test_missing_except_subj(default_param):
    # input invalid value for tasks
    default_param["load_data"]["exceptions"]["subjects"] = ""
    default_param["load_data"]["exceptions"]["tasks"] = ["*"]
    default_param["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the invalid field
    with pytest.raises(TypeError):
        load.load_files(default_param["load_data"])
        assert True


def test_missing_except_task(default_param):
    # input invalid value for tasks
    default_param["load_data"]["exceptions"]["subjects"] = ["*"]
    default_param["load_data"]["exceptions"]["tasks"] = ""
    default_param["load_data"]["exceptions"]["runs"] = ["*"]

    # Load data using the invalid field
    with pytest.raises(TypeError):
        load.load_files(default_param["load_data"])
        assert True


def test_missing_except_run(default_param):
    # input invalid value for tasks
    default_param["load_data"]["exceptions"]["subjects"] = ["*"]
    default_param["load_data"]["exceptions"]["tasks"] = ["*"]
    default_param["load_data"]["exceptions"]["runs"] = ""

    # Load data using the invalid field
    with pytest.raises(Exception):
        load.load_files(default_param["load_data"])
        assert True


def test_missing_data(default_param, tmp_path):
    # create empty and temporary directory
    empty_data = tmp_path / "empty"
    empty_data.mkdir()

    # input invalid value for tasks
    default_param["load_data"]["root"] = empty_data

    # Load data using the invalid field
    with pytest.raises(Exception):
        load.load_files(default_param["load_data"])
        assert True

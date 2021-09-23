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
def default_param(root, tmp_path):
    default_param = write.write_template_params(root, tmp_path)
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


@pytest.fixture
def all():
    return ["*"]


@pytest.fixture
def select_subj():
    return ["NDARAB793GL3"]


@pytest.fixture
def select_task():
    return ["ContrastChangeBlock1"]


@pytest.fixture
def except_subj():
    return ["NDARAB793GL3"]


@pytest.fixture
def except_task():
    return ["ContrastChangeBlock1"]


@pytest.fixture
def except_run():
    return ["01"]


@pytest.fixture
def error_select_param():
    return ""


@pytest.fixture
def error_except_param():
    return None


def test_select_all(default_param, avail_subj, subj_files):
    # Load data using the default parameters
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the number of all files available
    count = 0
    for subject in avail_subj:
        count += len(subj_files[subject])
    assert len(data) == count


def test_select_subj(default_param, subj_files, select_subj):
    # select participants (make this a random selection?)
    default_param["load_data"]["subjects"] = select_subj

    # Load data using the selected participants
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected subjects
    count = 0
    for subject in select_subj:
        count += len(subj_files[subject])
    assert len(data) == count


def test_select_task(default_param, avail_subj, subj_files, select_task):
    # select tasks (make this a random selection?)
    default_param["load_data"]["tasks"] = select_task

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

            if task in select_task:
                count += 1
    assert len(data) == count


def test_select_subj_task(default_param, subj_files, select_subj, select_task):
    default_param["load_data"]["subjects"] = select_subj
    default_param["load_data"]["tasks"] = select_task

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected tasks & subjects
    count = 0
    for subject in select_subj:
        for file in subj_files[subject]:
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in select_task:
                count += 1
    assert len(data) == count


def test_except_subj(default_param, avail_subj, subj_files, all, except_subj):
    default_param["load_data"]["exceptions"]["subjects"] = except_subj
    default_param["load_data"]["exceptions"]["tasks"] = all
    default_param["load_data"]["exceptions"]["runs"] = all

    # Load data using the excluded subjects
    data = load.load_files(default_param["load_data"])

    # get the excluded subset of subjects
    subjects_diff = set(avail_subj).difference(set(except_subj))

    # check if the number of files loaded matches
    # the total number of all subjects apart from the excluded
    count = 0
    for subject in subjects_diff:
        count += len(subj_files[subject])
    assert len(data) == count


def test_except_task(default_param, avail_subj, subj_files, all, except_task):
    default_param["load_data"]["exceptions"]["subjects"] = all
    default_param["load_data"]["exceptions"]["tasks"] = except_task
    default_param["load_data"]["exceptions"]["runs"] = all

    # Load data using the excluded tasks
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of all tasks apart from the excluded
    count = 0
    for subject in avail_subj:
        for file in subj_files[subject]:

            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in except_task:
                continue
            count += 1
    assert len(data) == count


def test_except_subj_task(default_param, avail_subj, subj_files, all,
                          except_subj, except_task):
    default_param["load_data"]["exceptions"]["subjects"] = except_subj
    default_param["load_data"]["exceptions"]["tasks"] = except_task
    default_param["load_data"]["exceptions"]["runs"] = all

    # Load data using the excluded subjects & tasks
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of all subjects & tasks apart from the excluded
    count = 0
    for subject in avail_subj:
        for file in subj_files[subject]:

            file_vals = file.split("_")
            sub_id = [s for s in file_vals if "sub" in s][0]
            sub = [s for s in sub_id.split("-") if s != "sub"][0]

            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if sub in except_subj and task in except_task:
                continue
            count += 1
    assert len(data) == count


def test_except_subj_task_run(default_param, avail_subj, subj_files,
                              except_subj, except_task, except_run):
    default_param["load_data"]["exceptions"]["subjects"] = except_subj
    default_param["load_data"]["exceptions"]["tasks"] = except_task
    default_param["load_data"]["exceptions"]["runs"] = except_run

    # Load data using the excluded subjects & tasks
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of all subjects & tasks apart from the excluded
    count = 0
    for subject in avail_subj:
        for file in subj_files[subject]:

            file_vals = file.split("_")
            sub_id = [s for s in file_vals if "sub" in s][0]
            sub = [s for s in sub_id.split("-") if s != "sub"][0]

            task_id = [s for s in file_vals if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            # split and find run of file (TODO: need to BIDSIFY)
            run_id = [s for s in file_vals if "run" in s][0]
            run = [s for s in run_id.split("-") if s != "run"][0]

            if sub in except_subj and task in except_task \
               and run in except_run:
                continue
            count += 1
    assert len(data) == count


def test_except_all(default_param, all):
    # select all for exceptions
    default_param["load_data"]["exceptions"]["subjects"] = all
    default_param["load_data"]["exceptions"]["tasks"] = all
    default_param["load_data"]["exceptions"]["runs"] = all

    # Load data using the excluded subjects & tasks
    data = load.load_files(default_param["load_data"])

    # assert nothing is selected
    assert len(data) == 0


def test_select_all_except_subj(default_param, subj_files, all,
                                select_subj, select_task, except_subj):

    default_param["load_data"]["subjects"] = select_subj
    default_param["load_data"]["tasks"] = select_task

    default_param["load_data"]["exceptions"]["subjects"] = except_subj
    default_param["load_data"]["exceptions"]["tasks"] = all
    default_param["load_data"]["exceptions"]["runs"] = all

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # get the excluded subset of subjects
    subjects_diff = set(select_subj).difference(set(except_subj))

    # check if the number of files loaded matches
    # the total number of files for all selected subjects excluding exceptions
    count = 0
    for subject in subjects_diff:
        for file in subj_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in select_subj:
                count += 1
    assert len(data) == count


def test_select_all_except_task(default_param, subj_files, all,
                                select_subj, select_task, except_task):

    default_param["load_data"]["subjects"] = select_subj
    default_param["load_data"]["tasks"] = select_task

    default_param["load_data"]["exceptions"]["subjects"] = all
    default_param["load_data"]["exceptions"]["tasks"] = except_task
    default_param["load_data"]["exceptions"]["runs"] = all

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected subjects excluding exceptions
    count = 0
    for subject in select_subj:
        for file in subj_files[subject]:

            # split and find task of file (TODO: need to BIDSIFY)
            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if task in except_task:
                continue
            elif task in select_task:
                count += 1
    assert len(data) == count


def test_sel_all_except_subj_task(default_param, avail_subj, subj_files, all,
                                  select_subj, select_task, except_subj,
                                  except_task):

    default_param["load_data"]["subjects"] = select_subj
    default_param["load_data"]["tasks"] = select_task

    default_param["load_data"]["exceptions"]["subjects"] = except_subj
    default_param["load_data"]["exceptions"]["tasks"] = except_task
    default_param["load_data"]["exceptions"]["runs"] = all

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected subjects excluding exceptions
    count = 0
    for subject in avail_subj:
        for file in subj_files[subject]:

            file_vals = file.split("_")
            sub_id = [s for s in file_vals if "sub" in s][0]
            sub = [s for s in sub_id.split("-") if s != "sub"][0]

            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            if sub in except_subj and task in except_task:
                continue
            elif task in select_task:
                count += 1
    assert len(data) == count


def test_select_all_except_all(default_param, subj_files,
                               select_subj, select_task, except_subj,
                               except_task, except_run):

    default_param["load_data"]["subjects"] = select_subj
    default_param["load_data"]["tasks"] = select_task

    default_param["load_data"]["exceptions"]["subjects"] = except_subj
    default_param["load_data"]["exceptions"]["tasks"] = except_task
    default_param["load_data"]["exceptions"]["runs"] = except_run

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # check if the number of files loaded matches
    # the total number of files for all selected subjects excluding exceptions
    count = 0
    for subject in select_subj:
        for file in subj_files[subject]:

            file_vals = file.split("_")

            sub_id = [s for s in file_vals if "sub" in s][0]
            sub = [s for s in sub_id.split("-") if s != "sub"][0]

            task_id = [s for s in file.split("_") if "task" in s][0]
            task = [s for s in task_id.split("-") if s != "task"][0]

            run_id = [s for s in file.split("_") if "run" in s][0]
            run = [s for s in run_id.split("-") if s != "run"][0]

            if sub in except_subj and task in except_task \
               and run in except_run:
                continue
            elif task in select_task:
                count += 1
    assert len(data) == count


def test_missing_subj(default_param, error_select_param):
    # input invalid value for subjects
    default_param["load_data"]["subjects"] = error_select_param

    # Load data using the invalid field
    with pytest.raises(TypeError):
        load.load_files(default_param["load_data"])
        assert True


def test_missing_task(default_param, error_select_param):
    # input invalid value for tasks
    default_param["load_data"]["tasks"] = error_select_param

    # Load data using the invalid field
    with pytest.raises(TypeError):
        load.load_files(default_param["load_data"])
        assert True


def test_missing_except_subj(default_param, error_except_param, all):
    # input invalid value for tasks
    default_param["load_data"]["exceptions"]["subjects"] = error_except_param
    default_param["load_data"]["exceptions"]["tasks"] = all
    default_param["load_data"]["exceptions"]["runs"] = all

    # Load data using the invalid field
    with pytest.raises(TypeError):
        load.load_files(default_param["load_data"])
        assert True


def test_missing_except_task(default_param, error_except_param, all):
    # input invalid value for tasks
    default_param["load_data"]["exceptions"]["subjects"] = all
    default_param["load_data"]["exceptions"]["tasks"] = error_except_param
    default_param["load_data"]["exceptions"]["runs"] = all

    # Load data using the invalid field
    with pytest.raises(TypeError):
        load.load_files(default_param["load_data"])
        assert True


def test_missing_except_run(default_param, error_except_param, all):
    # input invalid value for tasks
    default_param["load_data"]["exceptions"]["subjects"] = all
    default_param["load_data"]["exceptions"]["tasks"] = all
    default_param["load_data"]["exceptions"]["runs"] = error_except_param

    # Load data using the invalid field
    with pytest.raises(TypeError):
        load.load_files(default_param["load_data"])
        assert True


def test_missing_data(default_param, tmp_path):
    # create empty and temporary directory
    empty_path = str(tmp_path) + "empty"
    os.mkdir(empty_path)

    # input invalid value for tasks
    default_param["load_data"]["root"] = empty_path

    # Load data using the invalid field
    with pytest.raises(FileNotFoundError):
        load.load_files(default_param["load_data"])
        assert True


def test_bad_path(default_param, tmp_path):
    # create empty and temporary directory
    invalid_path = str(tmp_path) + "empty"

    # input invalid value for tasks
    default_param["load_data"]["root"] = invalid_path

    # Load data using the invalid field
    with pytest.raises(FileNotFoundError):
        load.load_files(default_param["load_data"])
        assert True

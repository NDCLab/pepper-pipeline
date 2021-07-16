from scripts.data.load import load_files
from scripts.data.write import write_template_params

import pytest
import unittest
from pathlib import Path

import mne_bids
import pandas as pd


class LoadFilesTest(unittest.TestCase):
    """Testing module to check if load_data properly filters files
    Instance Variables
    ----------
    self.default_params:    dict
                            a dictionary containing the default params
    self.root:  string
                string containg path to root of BIDS data
    self.available_subj:    list
                            a list of all available subjects in test_data

    Public Methods
    ----------
    test_select_all()
        test if load_data() selects all files with default values
    test_select_participants()
        test if load_data() selects specific participants correctly
    test_select_tasks()
        test if load_data() selects specific tasks
    test_select_particip_tasks()
        test if load_data selects specific subjects & tasks

    test_except_subjects()
        test if load_data removes specific subjects
    test_except_tasks()
        test if load_data removes specific tasks
    test_except_subj_tasks()
        test if load_data removes specific subjects & tasks
    test_except_subj_runs()
        test if load_data removes specific subjects & runs
    test_except_subj_tasks_runs()
        test if load_data removes specific subjects, tasks, & runs

    test_select_particip_tasks_except_subjects()
    test_select_particip_tasks_except_tasks()
    test_select_particip_tasks_except_subj_tasks()
    test_select_particip_tasks_except_subj_tasks_runs()

    test_missing_subj()
        test if missing subject errors out correctly
    test_missing_tasks()
        test if missing tasks errors out correctly
    test_missing_exceptions()
        test if missing exceptions errors out correctly
    """
    def setUp(self):
        # init default parameters
        self.root = Path("CMI/rawdata")
        self.default_params = write_template_params(self.root)
        self.available_subj = mne_bids.get_entity_vals(self.root, 'subject')

        # create a dictionary of subjects and corresponding files
        self.subjects = {}
        for subject in self.available_subj:
            bids_path = mne_bids.BIDSPath(subject=subject, root=self.root)

            files = bids_path.match()
            scans_file = [f for f in files if "scans" in f.suffix][0]
            scans_info = pd.read_csv(scans_file, sep='\t')
            self.subjects[subject] = scans_info["filename"].to_list()

    def test_select_all(self):
        # Load data using the default parameters
        data = load_files(self.default_params["load_data"])

        count = 0
        # check if the number of files matches the number per subject
        for subject in self.available_subj:
            count += len(self.subjects[subject])
        assert len(data) == count

    def test_select_participants(self):
        # select participants (make this a random selection?)
        selected_participants = ["NDARAB793GL3"]
        self.default_params["load_data"]["subjects"] = selected_participants

        # Load data using the default parameters
        data = load_files(self.default_params["load_data"])

        count = 0
        # check if the number of files matches the number per subject
        for subject in selected_participants:
            count += len(self.subjects[subject])
        assert len(data) == count

    def test_select_tasks(self):
        # select tasks (make this a random selection?)
        selected_tasks = ["ContrastChangeBlock1"]
        self.default_params["load_data"]["tasks"] = selected_tasks

        # Load data using the default parameters
        data = load_files(self.default_params["load_data"])

        count = 0
        # check if the number of files matches the number per subject
        for subject in self.available_subj:
            for file in self.subjects[subject]:
                if file.task in selected_tasks:
                    count += 1
        assert len(data) == count

    def test_select_particip_tasks(self):
        # select subjects & tasks
        selected_participants = ["NDARAB793GL3"]
        selected_tasks = ["ContrastChangeBlock1"]

        self.default_params["load_data"]["subjects"] = selected_participants
        self.default_params["load_data"]["tasks"] = selected_tasks

        # Load data using the default parameters
        data = load_files(self.default_params["load_data"])

        count = 0
        # check if the number of files matches the number per subject
        for subject in self.available_subj:
            for file in self.subjects[subject]:
                if file.task in selected_tasks:
                    count += 1
        assert len(data) == count

    def test_except_subjects(self):
        exclude_participants = ["NDARAB793GL3"]

        self.default_params["load_data"]["exceptions"]["subjects"] = exclude_participants
        # Load data using the default parameters
        data = load_files(self.default_params["load_data"])

        count = 0
        # check if the number of files matches the number per subject
        for subject in self.available_subj:
            for file in self.subjects[subject]:
                if file.task in selected_tasks:
                    count += 1
        assert len(data) == count

    def test_except_tasks(self):
        return

    def test_except_subj_tasks(self):
        return

    def test_except_subj_runs(self):
        return

    def test_except_subj_tasks_runs(self):
        return

    def test_select_particip_tasks_except_subjects(self):
        return

    def test_select_particip_tasks_except_tasks(self):
        return

    def test_select_particip_tasks_except_subj_tasks(self):
        return

    def test_select_particip_tasks_except_subj_tasks_runs(self):
        return

    def test_missing_subj(self):
        return

    def test_missing_tasks(self):
        return

    def test_missing_exceptions(self):
        return


if __name__ == '__main__':
    unittest.main()

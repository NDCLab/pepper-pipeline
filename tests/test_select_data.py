from scripts.data.write_annotate import write_template_params

import unittest
from pathlib import Path
import mne_bids


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
        self.root = Path("../CMI/rawdata")
        self.default_params = write_template_params(self.root)
        self.available_subj = mne_bids.get_entity_vals(self.root, 'subject')

    def test_select_all(self):
        return

    def test_select_participants(self):
        return

    def test_select_tasks(self):
        return

    def test_select_particip_tasks(self):
        return

    def test_except_subjects(self):
        return

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
    LoadFilesTest.main()

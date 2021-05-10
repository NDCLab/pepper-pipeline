from pathlib import Path
from os import walk
from os.path import join

from bids_validator import BIDSValidator

import unittest


class BidsTest(unittest.TestCase):
    """Testing module that validates BIDS format and files

    Instance Variables
    ----------
    self.validator: BIDSValidator()
        BIDSValidator object

    self.files: list
        list that contains all data files from BIDS directory

    Public Methods
    ----------
    test_if_valid()
        verbose method that checks if each BIDS file is in proper format

    """
    def setUp(self):
        # init validator
        self.validator = BIDSValidator()

        root = Path('BIDS')
        self.files = []
        # "walk" through BIDS directory and append all found files
        for (dirpath, dirnames, filenames) in walk(root):
            path_filenames = [join(dirpath, name) for name in filenames]
            self.files += path_filenames

    def test_if_valid(self):
        # for each file found, inspect if BIDS
        for file in self.files:
            print("checking", file)
            self.assertTrue(self.validator.is_bids(file[4:]),
                            msg="BIDS validate failed on file" + str(file[4:]))


if __name__ == '__main__':
    unittest.main()

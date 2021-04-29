from pathlib import Path

from mne_bids import BIDSPath
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

        # get all available BIDS files
        bids_root = Path('BIDS')
        bids_path = BIDSPath(
            datatype='eeg',
            root=bids_root
        )
        # init list of BIDS files
        self.files = map(str, bids_path.match())

    def test_if_valid(self):
        for file in self.files:
            print("checking", file)
            self.assertTrue(self.validator.is_bids(file[4:]),
                            msg="BIDS validate failed on file" + str(file[4:]))


if __name__ == '__main__':
    unittest.main()

from pathlib import Path
from os import walk, sep
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

    self.root: str
        BIDS directory root

    Public Methods
    ----------
    test_if_valid()
        verbose method that checks if each BIDS file is in proper format

    """
    def setUp(self):
        # init validator
        self.validator = BIDSValidator()

        self.root = Path('BIDS')
        self.files = []
        # "walk" through BIDS directory and append all found files
        for (dirpath, dirnames, filenames) in walk(self.root):
            path_filenames = [join(dirpath, name) for name in filenames]
            self.files += path_filenames

    def test_if_valid(self):
        # for each file found, inspect if BIDS
        for file in self.files:
            with self.subTest(file=file):
                print("checking", file)
                relative_path = join(sep, Path(file).relative_to(self.root))
                self.assertTrue(self.validator.is_bids(relative_path),
                                msg="BIDS validate failed on file "
                                + relative_path)


if __name__ == '__main__':
    unittest.main()

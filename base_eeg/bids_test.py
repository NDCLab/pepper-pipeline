import unittest
from bids_validator import BIDSValidator


class BidsTest(unittest.TestCase):
    def test_if_valid(self):
        self.assertTrue(BIDSValidator.is_bids("BIDS"))


if __name__ == '__main__':
    unittest.main()

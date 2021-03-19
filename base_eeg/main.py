import preprocessing
import mne
from mne_bids import BIDSPath, write_raw_bids
import argparse, sys, os 

# from mne.datasets import sample
# from mne_bids import BIDSPath

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocessing Script for EEG Data")
    parser.add_argument(
        '--fname', 
        help="Path to raw EGI file",
        type=str, 
    )

    args = parser.parse_args()
    if not args.fname:
        parser.print_usage()
        sys.exit(1)

    raw = preprocessing.read_raw(args.fname)
    
    bids_path = BIDSPath(
        subject="01",
        session="01",
        task="testing",
        run="01", 
        root="/data/BIDS"
    )
    
    bids = preprocessing.write_bids(raw, bids_path)

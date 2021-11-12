import mne_bids
import pytest
import os

from scripts.data import write
from scripts.preprocess import preprocess as pre


@pytest.fixture
def raw_data():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    bids_root = f'{root_dir}/test_bids_data/'
    bids_path = mne_bids.BIDSPath(subject='testdata',
                                  session='01',
                                  task='SurroundSupression',
                                  run='01',
                                  datatype='eeg',
                                  root=bids_root)
    raw_test_data = mne_bids.read_raw_bids(bids_path)
    return raw_test_data


@pytest.fixture(params=['preloaded_data', 'non_preloaded_data'])
def bids_test_data(request, raw_data):
    if request.param == 'preloaded_data':
        raw_data.load_data()
    return raw_data


@pytest.fixture(params=['preloaded_data', 'non_preloaded_data'])
def bids_test_epoch_data(request, raw_data, default_params):
    # Get default montage, ref, and segment params
    feature_params = default_params["preprocess"]
    ref_params = feature_params["set_reference"]
    seg_params = feature_params["segment_data"]
    montage_param = feature_params["set_montage"]

    # Set the ref electrode
    eeg_obj, _ = pre.set_reference(raw_data, **ref_params)
    # Set the montage file
    eeg_obj, _ = pre.set_montage(eeg_obj, **montage_param)
    # Generate epoched object
    epo, _ = pre.segment_data(eeg_obj, **seg_params)

    if request.param == 'preloaded_data':
        epo.load_data()

    return epo


@pytest.fixture
def default_params(tmp_path):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    bids_root = f'{root_dir}/test_bids_data/'
    default_params = write.write_template_params(bids_root, tmp_path)
    return default_params

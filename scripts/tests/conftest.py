import mne_bids
import pytest
import os

from scripts.data import write


@pytest.fixture(params=['preloaded_data', 'non_preloaded_data'])
def bids_test_data(request):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    bids_root = f'{root_dir}/test_bids_data/'
    bids_path = mne_bids.BIDSPath(subject='testdata',
                                  session='01',
                                  task='SurroundSupression',
                                  run='01',
                                  datatype='eeg',
                                  root=bids_root)
    raw_test_data = mne_bids.read_raw_bids(bids_path)
    if request.param == 'preloaded_data':
        raw_test_data.load_data()
    return raw_test_data


@pytest.fixture
def default_params(tmp_path):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    bids_root = f'{root_dir}/test_bids_data/'
    default_params = write.write_template_params(bids_root, tmp_path)
    return default_params

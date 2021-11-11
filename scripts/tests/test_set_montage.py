from scripts.preprocess import preprocess as pre
import pytest
import mne
import numpy as np

from scripts.constants import ERROR_KEY


@pytest.fixture
def simulated_raw_hydrocel_129():
    # simulate an EEG dataset conforming to the
    channel_names = [f'E{c}' for c in range(1, 129)]
    channel_names.append('Cz')
    num_channels = len(channel_names)
    num_samples = 5000
    eeg_data = np.random.randn(num_channels, num_samples)
    info = mne.create_info(channel_names, ch_types='eeg', sfreq=500)
    raw = mne.io.RawArray(eeg_data, info)
    return raw


def test_valid_montage(simulated_raw_hydrocel_129):
    # Apply the correct montage
    montage_to_use = 'GSN-HydroCel-129'
    data_with_montage, montage_output = pre.set_montage(simulated_raw_hydrocel_129, montage_to_use)
    assert data_with_montage.get_montage() is not None
    assert montage_output['Montage']['Montage'] == montage_to_use


def test_invalid_montage(simulated_raw_hydrocel_129):
    # Apply an incorrect montage
    montage_to_use = 'standard_1020'
    data_with_montage, montage_output = pre.set_montage(simulated_raw_hydrocel_129, montage_to_use)
    assert ERROR_KEY in montage_output.keys()

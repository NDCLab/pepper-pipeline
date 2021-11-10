import pytest
from scripts.preprocess import preprocess as pre
import mne


@pytest.fixture(params=['preloaded_data', 'non_preloaded_data'])
def single_event_epoch_data(request, default_params, raw_data):
    # Get montage and segment params
    feature_params = default_params["preprocess"]
    seg_params = feature_params["segment_data"]
    montage_param = feature_params["set_montage"]

    # Set the montage file
    eeg_obj, _ = pre.set_montage(raw_data, **montage_param)

    # Generate epoch object
    epo, _ = pre.segment_data(eeg_obj, **seg_params)

    # Get sfreq and event metadata
    s_freq = epo.info["sfreq"]
    events = epo.events
    event_id = epo.event_id

    # Convert events to annotations from epoch events
    annotate = mne.annotations_from_events(events, sfreq=s_freq)

    # Delete all other event annotations except for first
    annotate.delete(list(range(1, annotate.__len__())))
    # Set newly deleted annotations to raw
    single_event_data = raw_data.set_annotations(annotate)
    # Generate epochs from raw containing single event
    events, event_id = mne.events_from_annotations(single_event_data)
    single_event_epo = mne.Epochs(single_event_data,
                                  events,
                                  event_id,
                                  )
    if request.param == 'preloaded_data':
        single_event_epo.load_data()

    return single_event_epo


@pytest.fixture
def error_obj():
    # Maybe this should eventually become a busted EEG file
    return None


def test_return_values(bids_test_epoch_data):
    # Reject epochs using ar
    rej_epo, output_dict = pre.final_reject_epoch(bids_test_epoch_data)

    # assert that data is valid
    assert "ERROR" not in output_dict.keys()
    assert isinstance(rej_epo, mne.Epochs)


def test_bad_object(error_obj):
    # attempt to filter data w/invalid data
    _, output = pre.final_reject_epoch(error_obj)
    assert "ERROR" in output.keys()


def test_single_event(single_event_epoch_data):
    # attempt to reject epochs with data containing only one entire epoch
    # across each channel
    _, output = pre.final_reject_epoch(single_event_epoch_data)
    assert "ERROR" in output.keys()

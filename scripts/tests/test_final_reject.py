from scripts import preprocess as pre
import mne


def test_return_values(bids_test_epoch_data):
    # Reject epochs using ar
    rej_epo, _ = pre.final_reject_epoch(bids_test_epoch_data)

    # assert that data is valid
    assert isinstance(rej_epo, mne.Epochs)

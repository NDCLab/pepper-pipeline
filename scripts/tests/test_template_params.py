from scripts.data import write
import pytest

import json
import os


@pytest.fixture
def write_path():
    dn = "test"
    if os.path.isdir(dn):
        os.rmdir(dn)
    os.mkdir(dn)
    return dn


@pytest.fixture
def default_params_write(default_params, tmp_path, write_path):
    root = default_params["load_data"]["root"]
    default_param = write.write_template_params(str(root), str(tmp_path),
                                                to_file=write_path)
    return default_param


@pytest.fixture
def load_params():
    return set(["root", "subjects", "tasks", "exceptions", "channel-type",
                "exit_on_error", "overwrite", "parallel"])


@pytest.fixture
def preprocess_params():
    return set(["set_reference", "set_montage", "filter_data",
                "identify_badchans_raw", "ica_raw", "segment_data",
                "final_reject_epoch", "interpolate_data", "reref_raw"])


@pytest.fixture
def write_params():
    return set(["root"])


@pytest.fixture
def exception_params():
    return set(["subjects", "tasks", "runs"])


@pytest.fixture
def set_ref_params():
    return set(["ref_channels"])


@pytest.fixture
def montage_params():
    return set(["montage"])


@pytest.fixture
def filter_params():
    return set(["l_freq", "h_freq"])


@pytest.fixture
def badchans_params():
    return set(["ref_elec_name"])


@pytest.fixture
def ica_params():
    return set()


@pytest.fixture
def segment_params():
    return set(["tmin", "tmax", "baseline", "picks", "reject_tmin",
                "reject_tmax", "decim", "verbose", "preload"])


@pytest.fixture
def finalReject_params():
    return set()


@pytest.fixture
def interp_params():
    return set(["mode"])


@pytest.fixture
def reref_params():
    return set()


def test_params(default_params, load_params, preprocess_params, write_params,
                exception_params, set_ref_params, montage_params,
                filter_params, badchans_params, ica_params, segment_params, 
                finalReject_params, interp_params, reref_params):
    # get overall sections of user_params
    load_data = default_params["load_data"]
    preprocess = default_params["preprocess"]
    output_data = default_params["output_data"]

    # check that each valid param set is a subset of the created params
    assert load_params == set(load_data)
    assert preprocess_params == set(preprocess)
    assert write_params == set(output_data)

    # get param list of exceptions
    exceptions = load_data["exceptions"]

    # check that a set of valid params is equal to the set of created params
    assert exception_params == set(exceptions)

    # get a param list of each feature
    set_ref = preprocess["set_reference"]
    montage = preprocess["set_montage"]
    filter = preprocess["filter_data"]
    bad_chans = preprocess["identify_badchans_raw"]
    ica = preprocess["ica_raw"]
    segment = preprocess["segment_data"]
    final_reject = preprocess["final_reject_epoch"]
    interp = preprocess["interpolate_data"]
    reref = preprocess["reref_raw"]

    # check that a set of valid params is equal to the set of created params
    assert set_ref_params == set(set_ref)
    assert montage_params == set(montage)
    assert filter_params == set(filter)
    assert badchans_params == set(bad_chans)
    assert ica_params == set(ica)
    assert segment_params == set(segment)
    assert finalReject_params == set(final_reject)
    assert interp_params == set(interp)
    assert reref_params == set(reref)


def test_write(default_params_write, write_path):
    # check if file has been written
    for _, dirnames, filenames in os.walk(write_path):
        if not dirnames:
            assert len(filenames) == 1
    # assert that the written file is the same as user_params
    full_path = os.path.join(write_path, "user_params.json")
    with open(full_path) as fp:
        written_params = json.load(fp)
    assert default_params_write == written_params

    # remove temp directory
    os.remove(full_path)
    os.rmdir(write_path)

import numpy as np
import os
import pytest
import pandas as pd
import scripts.reliability.reliability


@pytest.fixture
def root_dir():
    return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture()
def test_data(root_dir):
    # test data is the 'simdata' produced by the splithalf package for R: https://github.com/sdparsons/splithalf
    test_data = pd.read_csv(f'{root_dir}/test_split_half_data/test_split_half_data.csv')
    test_data = test_data[test_data.block_name == 'A']  # only retain block 'A'
    return test_data


@pytest.fixture
def single_condition_data(test_data):
    participant_list = np.unique(test_data.participant_number)
    test_data = [test_data[test_data.participant_number == p].RT for p in participant_list]
    return test_data


@pytest.fixture
def two_condition_data(test_data):
    participant_list = np.unique(test_data.participant_number)
    cond_one_rows = test_data.trial_type == 'congruent'
    cond_two_rows = test_data.trial_type == 'incongruent'
    condition_one_data = [test_data[(test_data.participant_number == p) & cond_one_rows].RT for p in participant_list]
    condition_two_data = [test_data[(test_data.participant_number == p) & cond_two_rows].RT for p in participant_list]
    return condition_one_data, condition_two_data


def test_single_condition_reliability(single_condition_data):
    result = scripts.reliability.reliability.split_half(single_condition_data, None, 5000)
    # comparison values derived from the splithalf package for R: https://github.com/sdparsons/splithalf
    assert pytest.approx([.11, -.19, .40], abs=.02) == list(result.reliability)


def test_condition_difference_reliability(two_condition_data):
    result = scripts.reliability.reliability.split_half(two_condition_data[0], two_condition_data[1], 5000)
    # comparison values derived from the splithalf package for R: https://github.com/sdparsons/splithalf
    assert pytest.approx([-.13, -.39, .20], abs=.02) == list(result.reliability)

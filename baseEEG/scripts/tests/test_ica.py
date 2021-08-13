from scripts.preprocess import preprocess as pre
from scripts.data import load, write

import pytest

from pathlib import Path

@pytest.fixture
def root():
    root = Path("CMI/rawdata")
    return root


@pytest.fixture
def default_param(root):
    default_param = write.write_template_params(root)
    return default_param


@pytest.fixture
def select_subjects():
    # should be a random subject?
    return ["NDARAB793GL3"]


@pytest.fixture
def select_tasks():
    # should be a random task?
    return ["ContrastChangeBlock1"]


@pytest.fixture
def error_tasks():
    return ["Video1"]


def test_intermediate_raw_object(default_param, select_subjects, select_tasks):


def test_output_object(default_param, select_subjects, error_tasks):

import re

from importlib.metadata import version as dist_version

import hotdata_marimo as hm


def test_version_is_pep440_core():
    assert re.fullmatch(r"\d+\.\d+\.\d+(\+.*)?", hm.__version__)


def test_version_matches_distribution_metadata():
    assert dist_version("hotdata-marimo") == hm.__version__

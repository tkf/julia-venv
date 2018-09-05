"""
Tests that should be run only in CI (or in properly virtualized environment).
"""

import os

import pytest

try:
    import matplotlib
    del matplotlib
    has_matplotlib = True
except ImportError:
    has_matplotlib = False


pytestmark = pytest.mark.skipif(
    os.environ.get("TRAVIS", "") != "true",
    reason="Not in CI ($TRAVIS not set to 'true').")

require_matplotlib = pytest.mark.skipif(
    not has_matplotlib,
    reason="matplotlib is not installed")


@require_matplotlib
def test_install_pyplot(julia):
    from julia import Pkg
    Pkg.add("PyPlot")


@require_matplotlib
def test_use_pyplot(julia):
    test_install_pyplot(julia)
    from julia import PyPlot
    from matplotlib import pyplot
    PyPlot.plot()
    pyplot.close("all")

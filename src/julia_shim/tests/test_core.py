import os

from .. import core


def test_depot_path(julia):
    DEPOT_PATH = julia.eval("Base.DEPOT_PATH")
    assert DEPOT_PATH[0] == os.path.join(core.here, "depot")

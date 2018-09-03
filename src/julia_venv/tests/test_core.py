import os

import pytest

from .. import core
from ..core import SimpleJulia, _append_strings


def test_depot_path(julia):
    DEPOT_PATH = julia.eval("Base.DEPOT_PATH")
    assert DEPOT_PATH[0] == os.path.join(core.here, "depot")


@pytest.mark.parametrize("strings", [
    [],
    ["a"],
    ["a", "b", "c"],
    ["α", "β", "γ"],
])
def test_append_strings(julia, strings):
    dest = "__test_append_strings"

    jl = SimpleJulia()
    jl.eval("{} = []".format(dest))
    bytes_list = [s.encode("utf-8") for s in strings]
    _append_strings(jl, dest, bytes_list)

    actual = julia.eval(dest)
    assert actual == strings

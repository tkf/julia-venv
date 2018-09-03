import pytest

from .core import get_julia


@pytest.fixture
def julia():
    """ pytest fixture for providing a `julia.Julia` instance. """
    return get_julia()

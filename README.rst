Virtual Julia environments for PyJulia
======================================

|build-status| |coveralls|

PyJulia_ is an excellent interface to use Julia from Python.  However,
there are some limitations (`JuliaPy/pyjulia#185`_) for using it with
Python installed by Debian-based Linux distributions such as Ubuntu
and also by Conda.  Fixing this limitation may require some support
from Julia core (`JuliaLang/julia#28518`_).

PyJulia_ currently has a clever hack to workaround this problem but it
works only with Julia 0.6.  `julia-venv` is an implementation of a
similar hack but extending it such that it works even with multiple
virtual environments created for different Python executables.

.. _JuliaLang/julia#28518: https://github.com/JuliaLang/julia/issues/28518
.. _JuliaPy/pyjulia#185: https://github.com/JuliaPy/pyjulia/issues/185
.. _PyJulia: https://github.com/JuliaPy/pyjulia


Example usage
-------------

::

   virtualenv myenv
   source myenv/bin/activate
   pip install https://github.com/tkf/pyjulia/archive/juliainfo.zip
   pip install https://github.com/tkf/julia-venv/archive/master.zip
   julia-venv-manage --help
   julia-venv-manage install-deps   # install PyCall.jl etc. to myenv

Then, there is a CLI ``julia-venv`` inside ``myenv`` which (tries to)
behave like a normal ``julia`` program::

   $ julia-venv
      _       _ _(_)_     |  Documentation: https://docs.julialang.org
     (_)     | (_) (_)    |
      _ _   _| |_  __ _   |  Type "?" for help, "]?" for Pkg help.
     | | | | | | |/ _` |  |
     | | |_| | | | (_| |  |  Version 1.0.0 (2018-08-08)
    _/ |\__'_|_|_|\__'_|  |  Official https://julialang.org/ release
   |__/                   |

   julia>


To get an appropriately initialized ``julia.Julia`` instance for this
virtual environment, use ``julia_venv.get_julia``:

>>> from julia_venv import get_julia
>>> jl = get_julia()
>>> jl.eval("[1, 2, 3] .+ 10")
[11, 12, 13]

Once ``get_julia`` is called, PyJulia uses Julia runtime configured by
`julia_venv`:

>>> from julia import Main
>>> Main.using("PyCall")
>>> Main.eval("pathof(PyCall)")
'.../myenv/lib/python3.7/site-packages/julia_venv/depot/packages/PyCall/rUul9/src/PyCall.jl'


How it works
------------

The key feature of `julia-venv` package is to use `PyCall.jl`_ always
in "PyJulia-mode" so that the precompilation cache can be shared with
the Julia interpreter ``julia-venv`` and PyJulia_ API instantiated via
``julia_venv.get_julia()``.  This is done by calling Julia C API from
Python in ``julia-venv``.

Since `PyCall.jl`_ requires isolated ``deps`` directory for each
Python program for which `PyCall.jl`_ is configured, `julia-venv`
prepares its own `Base.DEPOT_PATH[1]` and ignores the default
`Base.DEPOT_PATH[1]` (which is ``~/.julia``).

.. _PyCall.jl: https://github.com/JuliaPy/PyCall.jl

.. budges

.. |build-status|
   image:: https://travis-ci.org/tkf/julia-venv.svg?branch=master
   :target: https://travis-ci.org/tkf/julia-venv
   :alt: Build Status

.. |coveralls|
   image:: https://coveralls.io/repos/github/tkf/julia-venv/badge.svg?branch=master
   :target: https://coveralls.io/github/tkf/julia-venv?branch=master
   :alt: Test Coverage

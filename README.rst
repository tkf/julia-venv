Virtual Julia environments for PyJulia
======================================

|build-status| |coveralls|

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


.. budges

.. |build-status|
   image:: https://travis-ci.org/tkf/julia-venv.svg?branch=master
   :target: https://travis-ci.org/tkf/julia-venv
   :alt: Build Status

.. |coveralls|
   image:: https://coveralls.io/repos/github/tkf/julia-venv/badge.svg?branch=master
   :target: https://coveralls.io/github/tkf/julia-venv?branch=master
   :alt: Test Coverage

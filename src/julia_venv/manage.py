"""
Manage julia-venv.
"""

from __future__ import print_function

import pprint

from .core import Configuration, rebuild_deps, install_deps, print_deps_file


def cli_set_julia(julia):
    """
    Set `julia` executable to be used.
    """
    config = Configuration.load()
    config.julia = julia
    config.dump()
    print("Configuration written to", config.path)


def cli_rebuild_deps():
    """
    Re-build PyCall.jl
    """
    config = Configuration.load()
    return rebuild_deps(config)


def cli_install_deps():
    """
    Install dependencies
    """
    config = Configuration.load()
    return install_deps(config)


def cli_show():
    """
    Show current configuration.
    """
    config = Configuration.load()
    print("Configuration:")
    pprint.pprint(config.as_dict())

    print_deps_file("Conda", "build.log")
    print_deps_file("PyCall", "build.log")
    print_deps_file("PyCall", "deps.jl")


def make_parser(doc=__doc__):
    import argparse

    class FormatterClass(argparse.RawDescriptionHelpFormatter,
                         argparse.ArgumentDefaultsHelpFormatter):
        pass

    parser = argparse.ArgumentParser(
        formatter_class=FormatterClass,
        description=doc)
    subparsers = parser.add_subparsers()

    def subp(command, func):
        doc = func.__doc__
        title = None
        for title in filter(None, map(str.strip, (doc or "").splitlines())):
            break
        p = subparsers.add_parser(
            command,
            formatter_class=FormatterClass,
            help=title,
            description=doc)
        p.set_defaults(func=func)
        return p

    p = subp("set-julia", cli_set_julia)
    p.add_argument(
        "julia",
        help="Path or command name to be used.")

    p = subp("install-deps", cli_install_deps)

    p = subp("build-pycall", cli_rebuild_deps)

    p = subp("show", cli_show)

    return parser


def main(args=None):
    parser = make_parser()
    ns = parser.parse_args(args)
    return (lambda func, **kwds: func(**kwds))(**vars(ns))


if __name__ == "__main__":
    main()

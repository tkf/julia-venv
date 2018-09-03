"""
Manage julia-shim.
"""

from __future__ import print_function

import pprint

from .core import Configuration


def cli_set_julia(julia):
    """
    Set `julia` executable to be used.
    """
    config = Configuration.load()
    config.julia = julia
    config.dump()
    print("Configuration written to", config.path)


def cli_show():
    """
    Show current configuration.
    """
    config = Configuration.load()
    pprint.pprint(config.as_dict())


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

    p = subp("show", cli_show)

    return parser


def main(args=None):
    parser = make_parser()
    ns = parser.parse_args(args)
    return (lambda func, **kwds: func(**kwds))(**vars(ns))


if __name__ == "__main__":
    main()

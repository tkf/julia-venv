import sys

from .core import exec_repl


def main(args=None):
    if args is None:
        args = sys.argv[1:]
        if sys.version_info[0] == 2:
            args = [a.decode("utf-8") for a in args]

    if len(args) > 0 and args[0] == "--julia-venv-debug":
        import logging
        logging.basicConfig(level=logging.DEBUG)
        args = args[1:]

    exec_repl(args)


if __name__ == "__main__":
    main()

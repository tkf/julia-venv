import os
import sys

from .core import Configuration


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    config = Configuration.load()
    command = config.make_command(args)
    os.environ["PYTHON"] = sys.executable
    os.execvp(command[0], command)


if __name__ == "__main__":
    main()

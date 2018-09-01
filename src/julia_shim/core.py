import json
import os
import sys

try:
    from shutil import which
except ImportError:
    # For Python < 3.3; it should behave more-or-less similar to
    # shutil.which when used with single argument.
    from distutils.spawn import find_executable as which


here = os.path.dirname(os.path.abspath(__file__))
default_path = os.path.join(here, "config.json")


def devirtualized_path(path=None):
    if path is None:
        path = os.environ["PATH"]
    vpath = os.path.dirname(sys.executable)
    return os.pathsep.join(p for p in path.split(os.pathsep) if p != vpath)


def devirtualized_which(command):
    return which(command, path=devirtualized_path())


class Configuration(object):

    def __init__(self, path, julia="julia", arguments=[]):
        self.julia = julia
        self.arguments = arguments

    def as_dict(self):
        return dict(
            julia=self.julia,
            arguments=self.arguments,
        )

    def dump(self):
        dct = self.as_dict()
        with open(self.path, "w") as file:
            json.dump(dct, file)

    @classmethod
    def load(cls, path=default_path):
        if not os.path.exists(default_path):
            return cls(path)
        with open(default_path) as file:
            dct = json.load(file)
        return cls(path, **dct)

    def get_julia(self):
        if os.path.abspath(self.julia):
            return self.julia
        return devirtualized_which(self.julia)

    def make_command(self, args=[]):
        command = [self.get_julia()]
        command.extend([
            "--load",
            os.path.join(here, "startup.jl"),
        ])
        command.extend(self.arguments)
        command.extend(args)
        return command

from ctypes import c_char_p, c_void_p
from logging import getLogger
import ctypes
import json
import os
import sys

from .utils import Singleton

try:
    from shutil import which
except ImportError:
    # For Python < 3.3; it should behave more-or-less similar to
    # shutil.which when used with single argument.
    from distutils.spawn import find_executable as which

logger = getLogger(__name__)

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

    def get_julia_executable(self):
        if os.path.abspath(self.julia):
            return self.julia
        return devirtualized_which(self.julia)

    def make_command(self, args=[]):
        command = [self.get_julia_executable()]
        command.extend([
            "--load",
            os.path.join(here, "startup.jl"),
        ])
        command.extend(self.arguments)
        command.extend(args)
        return command


class LibJuliaInitializer(Singleton):

    def __init__(self, config):
        self.config = config
        self.libjulia = _init_libjulia(config)


class PyJuliaInitializer(Singleton):

    def __init__(self, config):
        self.config = config
        self.libjulia = LibJuliaInitializer.instance(config).libjulia
        self.julia = _init_pyjulia(config)


def _init_libjulia(config):
    from julia.core import juliainfo

    runtime = config.get_julia_executable()
    jlinfo = juliainfo(runtime)
    BINDIR, libjulia_path, image_file = jlinfo[:3]
    logger.debug("Base.Sys.BINDIR = %s", BINDIR)
    logger.debug("libjulia_path = %s", libjulia_path)
    if not os.path.exists(libjulia_path):
        raise RuntimeError('Julia library ("libjulia") not found! {}'
                           .format(libjulia_path))

    # fixes a specific issue with python 2.7.13
    # ctypes.windll.LoadLibrary refuses unicode argument
    # http://bugs.python.org/issue29294
    if (2, 7, 13) <= sys.version_info < (2, 7, 14):
        libjulia_path = libjulia_path.encode("ascii")

    julia_bindir = BINDIR.encode("utf-8")

    libjulia = ctypes.PyDLL(libjulia_path, ctypes.RTLD_GLOBAL)
    try:
        jl_init_with_image = libjulia.jl_init_with_image
    except AttributeError:
        try:
            jl_init_with_image = libjulia.jl_init_with_image__threading
        except AttributeError:
            raise RuntimeError(
                "No libjulia entrypoint found! "
                "(tried jl_init_with_image and jl_init_with_image__threading)")

    jl_init_with_image.argtypes = [c_char_p, c_char_p]
    logger.debug("calling jl_init_with_image(%s, %s)", julia_bindir, image_file)
    jl_init_with_image(julia_bindir, image_file.encode("utf-8"))
    logger.debug("seems to work...")

    return libjulia


class SimpleJulia(object):

    def __init__(self, libjulia=None):
        if libjulia is None:
            initializer = LibJuliaInitializer.initialized()
            assert initializer is not None
            libjulia = initializer.libjulia

        libjulia.jl_eval_string.argtypes = [c_char_p]
        libjulia.jl_eval_string.restype = c_void_p
        libjulia.jl_exception_occurred.restype = c_void_p
        libjulia.jl_typeof_str.argtypes = [c_void_p]
        libjulia.jl_typeof_str.restype = c_char_p
        libjulia.jl_exception_clear.restype = None
        libjulia.jl_exception_clear()

        self.libjulia = libjulia

    def eval(self, code):
        logger.debug("eval:\n%s", code)
        ans = self.libjulia.jl_eval_string(code.encode("utf-8"))
        self.check_exception(code)
        return ans

    def check_exception(self, src=None):
        exoc = self.libjulia.jl_exception_occurred()
        if not exoc:
            self.libjulia.jl_exception_clear()
            return
        exception = self.libjulia.jl_typeof_str(exoc).decode("utf-8")
        if src is None:
            raise RuntimeError("Julia exception {}".format(exception))
        else:
            raise RuntimeError(
                "Julia Exception {} occurred while evaluating:\n{}"
                .format(exception, src))

    def include(self, path):
        if not os.path.exists(path):
            raise ValueError("{} does not exist".format(path))
        if '"' in path:
            raise NotImplementedError(
                'Path containing " is not supported yet. Trying to include:\n',
                '{}'.format(path))
        self.eval("""Base.include(Main, "{}")""".format(path))
        # Note at this point, there is no `include` (`Main.include`).


def _init_pyjulia(config):
    jl = SimpleJulia()
    jl.include(os.path.join(here, "startup.jl"))

    from julia import Julia
    return Julia(init_julia=False)


def _get_simplejulia(config=None):
    if config is None:
        config = Configuration.load()
    libjulia = LibJuliaInitializer.instance(config).libjulia
    return SimpleJulia(libjulia)


def get_julia(config=None):
    """
    Get `julia.Julia` instance for this virtual environment.
    """
    if config is None:
        config = Configuration.load()
    return PyJuliaInitializer.instance(config).julia


def start_repl(config=None, interactive=True,
               quiet=True, banner=True, history_file=True, color_set=False):
    jl = get_julia(config)
    jl.eval("""function(interactive, args...)
    was_interactive = Base.is_interactive
    try
        # Required for Pkg.__init__ to setup the REPL mode:
        Base.eval(:(is_interactive = $interactive))

        Base.run_main_repl(interactive, args...)
    finally
        Base.eval(:(is_interactive = $was_interactive))
    end
    end""")(interactive, quiet, banner, history_file, color_set)

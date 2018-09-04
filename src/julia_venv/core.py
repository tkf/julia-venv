from ctypes import POINTER, pointer, c_int, c_char_p, c_void_p, c_size_t
from logging import getLogger
import ctypes
import glob
import json
import os
import subprocess
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

os.environ["JULIA_VENV_PYTHON"] = sys.executable


def devirtualized_path(path=None):
    if path is None:
        path = os.environ["PATH"]
    vpath = os.path.dirname(sys.executable)
    return os.pathsep.join(p for p in path.split(os.pathsep) if p != vpath)


def devirtualized_which(command):
    return which(command, path=devirtualized_path())


class Configuration(object):

    def __init__(self, path, julia="julia"):
        self.julia = julia

    def as_dict(self):
        return dict(
            julia=self.julia,
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
        if os.path.isabs(self.julia):
            return self.julia
        return devirtualized_which(self.julia)

    def juliainfo(self):
        try:
            return self._juliainfo
        except AttributeError:
            pass

        from julia.core import juliainfo
        self._juliainfo = juliainfo(self.get_julia_executable())
        return self._juliainfo

    def is_compatible_exe(self):
        try:
            from julia.core import is_compatible_exe
        except ImportError:
            return False
        return is_compatible_exe(self.juliainfo())


# TODO: At some point, it would be better for depot to be able to
# configured per-Configuration basis.


def depot_path(*parts):
    return os.path.join(here, "depot", *parts)
# See: [[./startup.jl::venv_depot]]


def depot_glob(*parts):
    return glob.glob(depot_path(*parts))


def package_files(package, *parts):
    return depot_glob("packages", package, "*", *parts)


class LibJuliaInitializer(Singleton):

    def __init__(self, config):
        self.config = config
        self.load_libjulia(config)

    _libjulia_loaded = False

    def load_libjulia(self, config):
        if self._libjulia_loaded:
            return

        jlinfo = config.juliainfo()
        BINDIR, libjulia_path, image_file = jlinfo[:3]
        logger.debug("Base.Sys.BINDIR = %s", BINDIR)
        logger.debug("libjulia_path = %s", libjulia_path)
        if not os.path.exists(libjulia_path):
            raise RuntimeError('Julia library ("libjulia") not found! {}'
                               .format(libjulia_path))

        self.julia_bindir = BINDIR.encode("utf-8")
        self.image_file = image_file

        # fixes a specific issue with python 2.7.13
        # ctypes.windll.LoadLibrary refuses unicode argument
        # http://bugs.python.org/issue29294
        if (2, 7, 13) <= sys.version_info < (2, 7, 14):
            libjulia_path = libjulia_path.encode("ascii")

        libjulia = ctypes.PyDLL(libjulia_path, ctypes.RTLD_GLOBAL)
        try:
            jl_init_with_image = libjulia.jl_init_with_image
        except AttributeError:
            try:
                jl_init_with_image = libjulia.jl_init_with_image__threading
            except AttributeError:
                raise RuntimeError(
                    "No libjulia entrypoint found! (tried jl_init_with_image"
                    " and jl_init_with_image__threading)")
        jl_init_with_image.argtypes = [c_char_p, c_char_p]

        self.jl_init_with_image = jl_init_with_image
        self._libjulia = libjulia

        self._libjulia_loaded = True

    __libjulia_initialized = False

    def init_libjulia(self):
        """Ensure that libjulia is initialized only once."""
        if self.__libjulia_initialized:
            return

        julia_bindir = self.julia_bindir
        image_file = self.image_file
        logger.debug("calling jl_init_with_image(%s, %s)",
                     julia_bindir, image_file)
        self.jl_init_with_image(julia_bindir, image_file.encode("utf-8"))
        logger.debug("seems to work...")

        self.__libjulia_initialized = True

    @property
    def uninitialized_libjulia(self):
        return self._libjulia

    @property
    def libjulia(self):
        self.init_libjulia()
        return self._libjulia


class PyJuliaInitializer(Singleton):

    def __init__(self, config):
        self.config = config
        self.libjulia = LibJuliaInitializer.instance(config).libjulia
        self.julia = _init_pyjulia(config)


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
        libjulia.jl_parse_opts.argtypes = [POINTER(c_int),
                                           POINTER(POINTER(c_char_p))]
        libjulia.jl_pchar_to_string.argtypes = [c_char_p, c_size_t]
        libjulia.jl_pchar_to_string.restype = c_void_p
        libjulia.jl_call2.argtypes = [c_void_p] * 3
        libjulia.jl_call2.restype = c_void_p

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
        include = self.eval("Base.include")
        Main = self.eval("Main")
        chars = path.encode("utf-8")
        jl_str = self.libjulia.jl_pchar_to_string(chars, len(chars))
        self.libjulia.jl_call2(include, Main, jl_str)
        self.check_exception('''Base.include(Main, "{}")'''.format(path))
        # Note: at this point, there is no `include` (`Main.include`).


def _init_pyjulia(config):
    jl = SimpleJulia()
    jl.include(os.path.join(here, "startup.jl"))
    jl.eval("import PyCall")

    from julia.core import Julia
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


def _append_strings(jl, dest, bytes_list):
    assert isinstance(jl, SimpleJulia)
    libjulia = jl.libjulia

    jl_dest = jl.eval(dest)
    jl_push = jl.eval("push!")
    for chars in bytes_list:
        jl_s = libjulia.jl_pchar_to_string(chars, len(chars))
        libjulia.jl_call2(jl_push, jl_dest, jl_s)


def exec_repl(args=[], config=None):
    if config is None:
        config = Configuration.load()

    argv_list = list(args)
    argv_list.insert(0, "julia-venv")  # will be ignored
    logger.debug("argv_list = %r", argv_list)

    # load libjulia but don't call jl_init_with_image yet:
    libjulia = LibJuliaInitializer.instance(config).uninitialized_libjulia

    libjulia.jl_parse_opts.argtypes = [POINTER(c_int),
                                       POINTER(POINTER(c_char_p))]
    argc = c_int(len(argv_list))
    argv = POINTER(c_char_p)(
        (c_char_p * len(argv_list))(*(a.encode("utf-8") for a in argv_list)))
    libjulia.jl_parse_opts(pointer(argc), pointer(argv))
    logger.debug("jl_parse_opts called")
    logger.debug("argc = %r", argc)

    n_ARGS = argc.value
    ARGS = [argv[i] for i in range(n_ARGS)]
    logger.debug("ARGS = %r", ARGS)

    jl = _get_simplejulia(config)

    # Copy ARGS here to Main.ARGS
    jl.eval("empty!(ARGS)")
    _append_strings(jl, "ARGS", ARGS)

    jl.include(os.path.join(here, "exec_repl.jl"))


def run_install_script(config, julia_cmd):
    command = list(julia_cmd) + [
        "--color=yes",
        "--startup-file=no",
        os.path.join(here, "build_pycall.jl"),
    ]
    julia = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        while True:
            julia.stdin.write(b"\r\n")
    except IOError:
        pass
    return julia.wait()


def build_pycall(config):
    from . import shim
    julia_cmd = [sys.executable, "-m", shim.__name__]
    return run_install_script(config, julia_cmd)


def install_deps(config):
    julia_cmd = [config.get_julia_executable()]
    return run_install_script(config, julia_cmd)


def print_deps_file(package, filename):
    files = package_files(package, "deps", filename)
    if files:
        print("{}/*/deps/{} found.".format(package, filename))
        for path in files:
            print("At:", path)
            print("Contents:")
            with open(path) as file:
                contents = file.read()
            print(contents)
    else:
        print("No {}/*/deps/{} is found!".format(package, filename))

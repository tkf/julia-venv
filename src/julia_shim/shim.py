from .core import Configuration, start_repl, get_julia, include


def shim(eval_, print_, interactive, programfile, args):
    config = Configuration.load()
    jl = get_julia(config)

    if not (eval_ or print_ or programfile):
        start_repl(config)
        return

    if eval_ or print_:
        args = list(args)
        if programfile:
            args.insert(0, programfile)
        jl.eval("""
        args -> append!(empty!(ARGS), args)
        """)(args)
        if eval_:
            jl.eval(eval_)
        elif print_:
            jl.eval("print")(jl.eval(print_))
    else:
        jl.eval("""
        args -> append!(empty!(ARGS), args)
        """)(args)
        include(jl, programfile)

    if interactive:
        start_repl(config)


def main(args=None):
    import argparse

    class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                          argparse.ArgumentDefaultsHelpFormatter):
        pass
    parser = argparse.ArgumentParser(
        formatter_class=CustomFormatter,
        description=__doc__)

    parser.add_argument(
        "--eval", "-e", metavar="<expr>", dest="eval_",
        help="Evaluate <expr>")
    parser.add_argument(
        "--print", "-E", metavar="<expr>", dest="print_",
        help="Evaluate <expr> and display the result")
    # TODO: Allow multiple --eval / --print and preserve their order.

    parser.add_argument(
        "-i", dest="interactive", action="store_true", default=None,
        help="Interactive mode; REPL runs and isinteractive() is true")
    parser.add_argument(
        "programfile", nargs="?",
        help="Julia script to be executed.")
    parser.add_argument(
        "args", nargs="*", default=[],
        help="Arguments passed to Julia script.")
    # TODO: handle arguments

    ns = parser.parse_args(args)
    shim(**vars(ns))


if __name__ == "__main__":
    main()

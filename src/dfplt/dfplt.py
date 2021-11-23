# from x2df import x2df
import argparse
from .__metadata__ import __version__


def main(argv):

    parser = argparse.ArgumentParser(
        "parses given glob-style paths and plots any found dataframes."
        + " Plots all the given dataframes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("srcs", nargs="*", help="glob-style paths that will be parsed")
    parser.add_argument(
        "-?", action="store_true", help="show this help message and exit"
    )
    parser.add_argument(
        "--nonblock",
        action="store_true",
        help="set to true to open figures in nonblocking mode for debugging "
        + "or batch exports.",
    )

    parser.add_argument("-v", "--version", action="store_true", help="prints version")
    args = argv[1:]
    args = vars(parser.parse_args(args))

    if args["version"]:
        print(__version__)
        return 0
    if args["?"] or not args["srcs"]:
        parser.print_help()
        return 0

    plots = (plot(x) for x in args["srcs"])
    plots = [x for x in plots if x]
    if not plots:
        parser.print_help()
        return 0

    for plot in plots:
        plot.show()
    return 0


def plot(src):
    return None

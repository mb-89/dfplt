try:  # pragma: no cover
    from dfplt.dfplt import main
except ModuleNotFoundError:  # pragma: no cover
    # we need this so the vscode debugger works better
    from dfplt import main
import sys  # pragma: no cover

main(sys.argv)  # pragma: no cover

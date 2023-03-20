__version__ = "0.0.1"
pkgname = "timewtui"

import sys
import os

extras = {"meta": {"dev": False}, "application": {}}
is_bad = False
if "-a" in sys.argv:
    print(f"Got arguments: {sys.argv}")
if "-v" in sys.argv:
    idx = sys.argv.index("-v")
    if (
        len(sys.argv) <= idx + 1
        or type(sys.argv[idx + 1]) != str
        or len(sys.argv[idx + 1]) != 1
        or not sys.argv[idx + 1].isnumeric()
    ):
        is_bad = True
        print("Argument -v must be followed by a number from 0 to 9!")
    else:
        extras["application"]["log_verbosity"] = int(sys.argv[idx + 1])
if "-d" in sys.argv:
    extras["meta"]["dev"] = True

if is_bad:
    raise ValueError("Bad argument(s) provided, exiting.")

from basetui_ncurses import mainLoop
from .application import timewTUI

mainLoop(
    metainfo={
        "version": __version__,
        "pkgname": pkgname,
        "program_config_dir": os.path.expanduser("~/.timewtui"),
    },
    extras=extras,
    pobj=timewTUI(),
)

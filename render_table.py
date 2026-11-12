#!/usr/bin/env python3
"""
Backward compatible shim. The logic lives in the geopick package.

    python render_table.py            # same as: python -m geopick table
    python render_table.py --write    # same as: python -m geopick write
    python render_table.py --check    # same as: python -m geopick check
"""
import sys

from geopick.cli import main

FLAGS = {"--write": "write", "--check": "check"}

if __name__ == "__main__":
    args = [FLAGS.get(a, a) for a in sys.argv[1:]] or ["table"]
    raise SystemExit(main(args))

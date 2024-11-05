#!/usr/bin/env python3
"""Support for using ProgressBar in pipes."""

import sys

from .ProgressBar import ProgressBar

if __name__ == "__main__":
    initial_value = 0
    if len(sys.argv) > 1:
        initial_value = int(sys.argv[1])

    progress_bar = ProgressBar(initial_value)
    print(initial_value)
    if initial_value > 0:
        with progress_bar as pb:
            try:
                for _ in iter(input, ""):
                    pb.increment()
            except KeyboardInterrupt:
                pb.complete()
                sys.exit(0)
            except EOFError:
                pass
            finally:
                sys.exit(0)
    else:
        sys.exit(1)

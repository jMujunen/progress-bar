#!/usr/bin/env python3
"""Support for using ProgressBar in pipes."""

import sys

from .ProgressBar import ProgressBar

if __name__ == "__main__":
    initial_value = 0

    # Parse stdin
    if len(sys.argv) > 1:
        initial_value = int(sys.argv[1])

    progress_bar = ProgressBar(initial_value)
    print(initial_value, file=sys.stderr)
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
        print(
            r"""Number of jobs/iterations are required
CLI Usage:
    command | python -m ProgressBar <jobs>

Example:
    find . -type f -exec echo "{}" /tmp/media/ \; | python -m ProgressBar $(find . -type f | wc -l)
    """,
            file=sys.stderr,
        )

#!/usr/bin/env python3
"""A simple progress bar object."""

import sys
import time

from ExecutionTimer import ExecutionTimer


class ProgressBar(ExecutionTimer):
    """A simple progress bar object.

    ### Attributes
    ----------
    `initial_value` : int
        The initial value of the progress bar

    `current_value` : int
        The current value of the progress bar.

    ### Methods
    -------
    | Method | Description |
    |--------|-------------|
    |`update(current_value=0)` |: Updates the progress bar with the given current value |
    |`increment(increment=1)` |: Increments the current value of the progress bar by the given amount |
    |`value(value)` |: Sets the current value of the progress bar to the given value |
    |`len()`| :  Returns the value of the progress bar for use in a for loop |

    ### Example:
    -----------
    >>> with ProgressBar(len(some_job)) as progress:
            spam()
            progress.increment()
    # [100.0%]==========================================[100.0%]
    # Execution time: 5 seconds

    """

    def __init__(self, initial_value: int, print_on_exit=True) -> None:
        """Initialize a new instance of the class.

        Parameters
        ----------
        - `initial_value` : int
            The initial value of the progress bar. Defaults to 100.
        """
        self.initial_value = initial_value
        self.print_on_exit = print_on_exit
        self._value = 0
        self.progress = 0
        self.errors = 0
        if self.initial_value == -1:
            sys.stdout.write("[%s] %i%%" % (" " * 40, 0))

    def increment(self, increment: int = 1) -> None:
        """Increment the current value of the progress bar by the given amount.

        Parameters
        ----------
            increment: The amount to increment the current value by
        """
        if self.start_time == 0:
            self.start_time = time.time()
        try:
            self.value += increment
            self.progress = self.value / self.initial_value * 100

            self.elapsed_time = time.time() - self.start_time
            remaining_time = (
                (self.elapsed_time / self.value) * (self.initial_value - self.value)
                if self.value > 0
                else None
            )
            transfer_speed = self.value / self.elapsed_time if self.elapsed_time > 0 else 0

            # Estimate time to complete and tranfer speed
            sys.stdout.write(
                "\r[%s] %i%% (ETA: %.2fs/%.2fs) %.2f MBits/s"
                % (
                    "=" * int(self.progress / 2),
                    self.progress,
                    self.elapsed_time,
                    remaining_time,
                    8 * transfer_speed,
                )
            )
            # sys.stdout.flush()

        except ZeroDivisionError:
            self.errors += 1
        sys.stdout.flush()
        if self.value == self.initial_value:
            print()

    @property
    def value(self) -> int:
        """Value getter property. Returns the current value."""
        return int(self._value)

    @value.setter
    def value(self, new_value: int) -> int:
        """Value setter."""
        self._value = new_value
        return self.value

    def __len__(self) -> int:
        """Return the length of the progress bar for use in a for loop."""
        return self.initial_value

    def __int__(self) -> int:
        """Int representation."""
        return int(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(initial_value={self.initial_value},\
current_value={self.value}, errors={self.errors}, progress={self.progress})"

    def update(self) -> None:
        """Force an update of the progress bar."""
        self.progress = self.value
        sys.stdout.write("\r[%s] %i%%" % ("=" * (50), 100))
        sys.stdout.flush()
        print("\n")

    def complete(self) -> None:
        """Manually set the bar to complete."""
        self.value = self.initial_value
        self.update()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.complete()
        return super().__exit__(exc_type, exc_value, traceback)

    def __enter__(self):
        return super().__enter__()


if __name__ == "__main__":
    import sys

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

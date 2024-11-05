#!/usr/bin/env python3
"""A simple progress bar object."""

import sys
import time
from enum import Enum


class TimeUnits(Enum):
    ms = 1e-3
    seconds = 1
    minutes = 60
    hours = 60**2
    days = 24 * 60**2


class ProgressBar:
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

    Out[2]: [100.0%]==========================================[100.0%]
    Out[2]: Execution time: 5 seconds

    >>> rsync -auv /mnt/ssd/ /tmp/ | python3 -m ProgressBar $(find /mnt/ssd | wc -l)

    [=] 2% (ETA: 2.99s/116.73s) 8.02 MBits/
    """

    start_time: float = 0.0
    end_time: float = 0.0
    execution_time: float = 0.0

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

    def __enter__(self):
        """Context manager method to start the execution timer."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.end_time = time.time()
        self.execution_time = self.end_time - self.start_time
        if self.print_on_exit:
            print(f"\n\033[34mExecution time: {self!s}\033[0m")

    def __str__(self) -> str:
        """Convert result from seconds to hours, minutes, seconds, and/or milliseconds."""
        time_seconds = self.execution_time
        template = "{minutes}{major_unit}{seconds} {minor_unit}"
        minutes, seconds = divmod(time_seconds, TimeUnits.minutes.value)
        for unit in TimeUnits:
            if time_seconds < TimeUnits.seconds.value:
                return template.format(
                    minutes="",
                    major_unit="",
                    seconds=f"{time_seconds/TimeUnits.ms.value:.0f}",
                    minor_unit=unit.name,
                )
            if unit.name == 'ms':
                continue
            if time_seconds < TimeUnits.minutes.value:
                return template.format(
                    minutes="", major_unit="", seconds=f"{seconds:.0f}", minor_unit=unit.name
                )
            minutes, seconds = divmod(self.execution_time, TimeUnits.minutes.value)
            time_seconds /= TimeUnits.minutes.value

        hours, minutes = divmod(time_seconds, TimeUnits.hours.value)
        return template.format(
            minutes=f"{hours:.0f} ",
            major_unit="hours ",
            seconds=f"{minutes:.0f}",
            minor_unit="minutes",
        )


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

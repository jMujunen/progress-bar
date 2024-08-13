#!/usr/bin/env python3
"""A simple progress bar object"""

import sys

from ExecutionTimer import ExecutionTimer


class ProgressBar(ExecutionTimer):
    """

    A simple progress bar object

    ### Attributes
    ----------
    `initial_value` : int
        The initial value of the progress bar. Defaults to 100.

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

    def __init__(self, initial_value: int) -> None:
        """Initializes a new instance of the class

        Parameters
        ----------
        - `initial_value` : int
            The initial value of the progress bar. Defaults to 100.
        """
        super().__init__()
        self.initial_value = initial_value
        self.value_ = 0
        self.progress = 0
        self.errors = 0

    def increment(self, increment=1) -> None:
        """Increments the current value of the progress bar by the given amount

        Parameters:
        ----------
            - `increment` (int): The amount to increment the current value by
        """
        try:
            self.value += increment
            self.progress = self.value / self.initial_value * 100
        except ZeroDivisionError:
            self.errors += 1
        output = f"[{self.progress:.1f}%]"
        sys.stdout.write("\r" + output.ljust(int(self.progress / 2), "=") + "[100.0%]")
        sys.stdout.flush()

    @property
    def value(self) -> int:
        """Value getter property. Returns the current value"""
        return int(self.value_)

    @value.setter
    def value(self, new_value: int) -> int:
        """Value setter"""
        self.value_ = new_value
        return self.value

    def __len__(self) -> int:
        """Returns the length of the progress bar for use in a for loop"""
        return self.initial_value

    def __int__(self) -> int:
        """Int representation"""
        return int(self.value)

    def __str__(self) -> str:
        """String representation"""
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(initial_value={self.initial_value},\
            current_value={self.value}, errors={self.errors}, progress={self.progress})"

    def update(self) -> None:
        """Force an update of the progress bar"""
        self.progress = self.value
        output = f"[{self.progress:.1f}%]"
        sys.stdout.write("\r" + output.ljust(int(self.progress / 2), "=") + "[100.0%]")
        sys.stdout.flush()

    def complete(self) -> None:
        """Sets the bar to complete manually"""
        self.value = self.initial_value
        self.update()

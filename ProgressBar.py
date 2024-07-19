#!/usr/bin/env python3
"""A simple progress bar object"""

from typing import Any
import sys


class ProgressBar:
    """
    A simple progress bar object

    Attributes
    ----------
    initial_value : int
        The initial value of the progress bar. Defaults to 100.

    current_value : int
        The current value of the progress bar.

    Methods
    -------
    update(current_value=0
        Updates the progress bar with the given current value
    increment(increment=1)
        Increments the current value of the progress bar by the given amount
    value(value)
        Sets the current value of the progress bar to the given value

    len()
        Returns the value of the progress bar for use in a for loop
    """

    def __init__(self, initial_value: int) -> None:
        """Initializes a new instance of the class

        Parameters
        ----------
        initial_value : int
            The initial value of the progress bar. Defaults to 100.
        """
        self.initial_value = initial_value
        self.value_ = 0
        self.progress = 1

    def increment(self, increment=1) -> None:
        """Increments the current value of the progress bar by the given amount

        Parameters:
        ----------
            increment (int): The amount to increment the current value by
        """
        self.value += increment
        self.progress = self.value / self.initial_value * 100
        output = f"[{self.progress:.1f}%]"
        sys.stdout.write("\r" + output.ljust(int(self.progress / 2), "=") + "[100.0%]")
        sys.stdout.flush()

    @property
    def value(self) -> int:
        """Value getter property. Returns the current value"""
        return int(self.value_)

    @value.setter
    def value(self, new_value: int) -> int:
        """
        Method which sets the value of the progress bar
        Args
        ------
        new_value : int
            The new value to set for the progress bar.
        """
        self.value_ = new_value
        return self.value

    def __len__(self) -> int:
        """Returns the length of the progress bar for use in a for loop"""
        return self.initial_value

    def __int__(self) -> int:
        return int(self.value)

    def __iter__(self) -> Any:
        yield (i for i in range(int(self.initial_value)))

    def __str__(self) -> str:
        return str(self.value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("\n")


# Example usage
if __name__ == "__main__":
    from ExecutionTimer import ExecutionTimer

    with ExecutionTimer():
        progress = ProgressBar(150000)
        for i in range(150000):
            progress.increment()

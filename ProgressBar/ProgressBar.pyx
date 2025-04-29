#cython: language_level=3
"""A simple progress bar object."""
import sys
import time
from enum import Enum
from typing import Optional, Iterable
cimport cython
from cpython cimport bool

from libc.math cimport fabs

class TimeUnits(Enum):
    ms = 1e-3
    seconds = 1
    minutes = 60
    hours = 60**2
    days = 24 * 60**2


cdef class ProgressBar:
    """A simple progress bar object."""
    def __init__(
        self, jobs: int | Iterable, str title='', bool print_on_exit=True, double print_interval=0.1
    ) -> None:
        """Initialize a new progress bar object.

        Parameters
        ----------
            - num_jobs (int): The number of jobs to be completed.
            - title (str): A string representing the name of the job.
            - print_on_exit (bool): Whether or not to print the final result after all tasks are completed.
            - print_interval (double): The interval (in seconds) at which to update the progress bar.

        """
        self.title = title.strip()
        if isinstance(jobs, int):
            num_jobs = jobs
        elif isinstance(jobs, Iterable):
            num_jobs = len(list(jobs))
            self.sequence = list(jobs)
        else:
            raise TypeError(f'Expected int or iterable, got {type(jobs)}')
        self._index = 0
        self.num_jobs = num_jobs
        self.start_time = time.time() # type: ignore
        self.print_on_exit = print_on_exit
        self.print_interval = print_interval
        self._value = 0
        self.progress = 0
        self.errors = 0
        self.last_print_time = 0.0 # type: ignore
        self.last_print_time = time.time() # type: ignore
        print(f'\033[1;4m{self.title.center(75)}\033[0m') if self.title else None
        if self.num_jobs == -1:
            sys.stdout.write("[%s] %i%%" % (" " * 40, 0))

    def __iter__(self) -> 'ProgressBar':
        """Return an iterator over the progress bar."""
        return self
    def __next__(self) -> 'ProgressBar':
        """Return the next value of the progress bar."""
        if self._index < len(self.sequence):
            item = self.sequence[self._index]
            self._index += 1
            self.increment()
            return item
        else:
            raise StopIteration

    def increment(self, unsigned int increment=1):
        """Increment the current value of the progress bar by the given amount."""
        cdef double current_time
        cdef double remaining_time

        if self.start_time == 0:
            self.start_time = time.time()
        try:
            self._value += increment
            self.progress = <int>(self._value / self.num_jobs * 100)
            current_time = time.time()

            if current_time - self.last_print_time > self.print_interval:
                self.last_print_time = current_time

                self.last_print_time = current_time
                self.execution_time = time.time() - self.start_time
                remaining_time = 0

                if self._value > 0:
                    remaining_time = (
                        (self.execution_time / self._value) * (self.num_jobs - self._value)
                    )

                self.throughput = (self._value / self.execution_time
                if self.execution_time > 0 else 0)

                # Estimate time to complete and transfer speed
                sys.stdout.write(
                    "\r[%.1f iter/s] [%s] %i%% (ETA: %.1fs/%.1fs)"
                    % (
                        self.throughput,
                        "=" * int(self.progress / 2),
                        self.progress,
                        remaining_time,
                        self.execution_time,
                    )
                )
                sys.stdout.flush()

            if self._value == self.num_jobs:
                sys.stdout.write(
                    "\r[%.1f iter/s] [%s] 100%% %s"
                    % (
                        self.throughput,
                        "=" * int(self.progress / 2),
                        " " * 20
                    )
                )
                sys.stdout.flush()
                print('\n')

        except ZeroDivisionError:
            self.errors += 1

    @property
    def value(self) -> int:
        """Value getter property. Returns the current value."""
        return self._value

    @value.setter
    def value(self, int new_value) -> None:
        """Value setter."""
        self._value = new_value

    def complete(self):
        """Complete the progress bar."""
        sys.stdout.write("\r[%s] 100%%\n" % ("=" * int(50)))
        sys.stdout.flush()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(initial_value={self.num_jobs}, current_value={self.value}, errors={self.errors}, progress={self.progress})"


    def __enter__(self):
        """Context manager method to start the execution timer."""
        self.start_time = time.time() # type: ignore
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> Optional[bool]:
        self.end_time = time.time() # type: ignore
        self.execution_time = self.end_time - self.start_time # type: ignore
        if self.print_on_exit is True:
            print(f"\n\033[34mExecution time: {self!s}\033[0m\n")

        return exc_type is not None

    def __str__(self) -> str:
        """Convert result from seconds to hours, minutes, seconds, and/or milliseconds."""
        cdef double time_seconds = self.execution_time
        cdef str template = "{minutes}{major_unit}{seconds} {minor_unit}"
        cdef double minutes, seconds, hours

        minutes = fabs(time_seconds / TimeUnits.minutes.value)
        seconds = fabs(time_seconds % TimeUnits.minutes.value)


        for unit in TimeUnits:
            if time_seconds < TimeUnits.seconds.value:
                return template.format(
                    minutes="",
                    major_unit="",
                    seconds=f"{time_seconds/TimeUnits.ms.value:.0f}",
                    minor_unit=TimeUnits.ms.name,
                )

            if unit.name == 'ms':
                continue
            time_seconds = time_seconds / unit.value
            if time_seconds < TimeUnits.minutes.value:
                return template.format(
                    minutes="", major_unit="", seconds=f"{seconds:.2f}", minor_unit=unit.name,
                )
            if time_seconds < TimeUnits.hours.value:
                return template.format(
                    minutes="", major_unit="", seconds=f"{seconds:.0f}", minor_unit=unit.name,
                )
            minutes = fabs(time_seconds / TimeUnits.hours.value)
            seconds = fabs(time_seconds % TimeUnits.hours.value)

        hours = fabs(time_seconds)
        return template.format(minutes=f"{hours:.0f} ", major_unit="", seconds=f"{minutes:.0f}",minor_unit="minutes")


def print_help():
    """Print help message."""
    print("Usage:\n\tcommand | python -m ProgressBar <num_jobs>")
    print('Example:\n\tfind . -exec stat --format="%s %n"| python -m ProgressBar $(find . | wc -l)')
    sys.exit(1)

def main():
    initial_value = 0
    # Parse stdin
    if '-h' in sys.argv[1]:
        print_help()

    if len(sys.argv) > 1:
        initial_value = int(sys.argv[1])

    # Below code is for supporting piping input from stdin.
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
        print_help()

if __name__ == "__main__":
    main()

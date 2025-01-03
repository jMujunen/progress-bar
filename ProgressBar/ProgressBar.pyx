#cython: language_level=3
"""A simple progress bar object."""
import sys
import time
from enum import Enum
from typing import Optional
cimport cython
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
        self, unsigned long int num_jobs, bint print_on_exit=1, double print_interval=0.1 # type: ignore
    ) -> None:
        self.num_jobs = num_jobs
        self.print_on_exit = print_on_exit
        self.print_interval = print_interval
        self._value = 0
        self.progress = 0
        self.errors = 0
        self.last_print_time = 0.0 # type: ignore
        if self.num_jobs == -1:
            sys.stdout.write("[%s] %i%%" % (" " * 40, 0))
    cpdef void increment(self, unsigned short int increment=1):
        """Increment the current value of the progress bar by the given amount."""
        cdef double current_time
        cdef double remaining_time
        cdef double transfer_speed

        if self.start_time == 0:
            self.start_time = time.time() # type: ignore
        try:
            self._value += increment
            self.progress = <int>(self._value / self.num_jobs * 100)

            current_time = time.time() # type: ignore
            if current_time - self.last_print_time > self.print_interval:
                self.last_print_time = current_time
                self.execution_time = time.time() - self.start_time # type: ignore
                remaining_time = 0 # type: ignore
                if self._value > 0:
                    remaining_time = (
                        (self.execution_time / self._value) # type: ignore
                        * (self.num_jobs - self._value)
                    )
                transfer_speed = (
                    self._value / self.execution_time if self.execution_time > 0 else 0 # type: ignore
                )

                # Estimate time to complete and transfer speed
                sys.stdout.write(
                    "\r[%s] %i%% (ETA: %.2fs/%.2fs) %.2f MBits/s"
                    % (
                        "=" * int(self.progress / 2),
                        self.progress,
                        self.execution_time,
                        remaining_time,
                        8 * transfer_speed,
                    )
                )
                sys.stdout.flush()
            elif self.progress == self.num_jobs:
                self.complete()
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

    cpdef void update(self):
        """Force an update of the progress bar."""
        self.progress = self._value
        sys.stdout.write("\r[%s] %i%%" % ("=" * (50), 100))
        sys.stdout.flush()
        print("\n")
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(initial_value={self.num_jobs}, current_value={self.value}, errors={self.errors}, progress={self.progress})"
    cpdef void complete(self):
        """Manually set the bar to complete."""
        self._value = self.num_jobs
        self.update()
        if self.print_on_exit == 1:
            print(f"\n\033[34mExecution time: {self!s}\033[0m\n")

    def __enter__(self):
        """Context manager method to start the execution timer."""
        self.start_time = time.time() # type: ignore
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> Optional[bool]:
        self.end_time = time.time() # type: ignore
        self.execution_time = self.end_time - self.start_time # type: ignore
        self.complete()
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


cdef void print_help():
    """Print help message."""
    print("Usage:\n\tcommand | python -m ProgressBar <num_jobs>")
    print('Example:\n\tfind . -exec stat --format="%s %n"| python -m ProgressBar $(find . | wc -l)')
    sys.exit(1)
if __name__ == "__main__":
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

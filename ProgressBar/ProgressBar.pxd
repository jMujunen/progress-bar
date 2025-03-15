import cython
from cpython cimport bool

cdef class ProgressBar:
    """A simple progress bar object."""
    cdef double start_time
    cdef double end_time
    cdef double execution_time
    cdef int num_jobs
    cdef int _value
    cdef int progress
    cdef int errors
    cdef double last_print_time
    cdef bool print_on_exit
    cdef double print_interval
    cdef str title
    cdef double throughput
    cpdef void increment(self, unsigned short int increment=?)

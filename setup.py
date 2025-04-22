from Cython.Build import cythonize
from setuptools import setup
from setuptools.extension import Extension

ext_modules = [
    Extension(
        "ProgressBar.ProgressBar",
        ["ProgressBar/ProgressBar.pyx"],
    )
]

setup(
    name="ProgressBar",
    version="0.1.0",
    packages=["ProgressBar"],
    ext_modules=cythonize(ext_modules),
)

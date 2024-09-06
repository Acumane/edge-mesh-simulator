from os import path, makedirs as makeDir
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

if not path.exists("bin"): makeDir("bin")

signal = [
    Pybind11Extension("bin.signal",
        ["core/bind.cpp"],
        include_dirs=["core"],
        extra_compile_args=["-std=c++17", "-O3"]
    ),
]

setup(
    name="signal",
    ext_modules=signal,
    cmdclass={"build_ext": build_ext},
)

# python build.py build_ext --inplace --force

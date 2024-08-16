from os import path, makedirs as makeDir
from setuptools import setup, Extension
import numpy as num

"""
MIT License

Copyright (c) 2021 Supawat Tamsri

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
"""

if not path.exists("bin"): makeDir("bin")

core_module = Extension("bin.core",
                        sources=["core/core.cpp"],
                        include_dirs=[num.get_include(), "core"],
                        extra_compile_args=["-std=c++11"])

calc_module = Extension("bin.calc",
                        sources=["core/calc.cpp"],
                        include_dirs=[num.get_include(), "core"],
                        extra_compile_args=["-std=c++11"])

setup(license="MIT", ext_modules=[core_module, calc_module])

"""Explicit build script for pydensecrf.

Upstream's setup.py calls cythonize() whenever Cython is importable, and Cython then
defaults to language_level=2 for these old .pyx files, emitting Python-2 C-API access
(tp_print, tstate->exc_type) that no longer compiles on CPython 3.10. We already
pre-generated the wrappers with `cython --cplus -3`, so this script declares the two
extensions directly (same names, sources and include dirs as upstream's fallback branch)
and never invokes Cython. Upstream sources are untouched.

Usage:  python setup_local.py build_ext --inplace
"""
from setuptools import setup
from setuptools.extension import Extension

ext_modules = [
    Extension(
        "pydensecrf.eigen",
        ["pydensecrf/eigen.cpp", "pydensecrf/eigen_impl.cpp"],
        language="c++",
        include_dirs=["pydensecrf/densecrf/include"],
    ),
    Extension(
        "pydensecrf.densecrf",
        [
            "pydensecrf/densecrf.cpp",
            "pydensecrf/densecrf/src/densecrf.cpp",
            "pydensecrf/densecrf/src/unary.cpp",
            "pydensecrf/densecrf/src/pairwise.cpp",
            "pydensecrf/densecrf/src/permutohedral.cpp",
            "pydensecrf/densecrf/src/optimization.cpp",
            "pydensecrf/densecrf/src/objective.cpp",
            "pydensecrf/densecrf/src/labelcompatibility.cpp",
            "pydensecrf/densecrf/src/util.cpp",
            "pydensecrf/densecrf/external/liblbfgs/lib/lbfgs.c",
        ],
        language="c++",
        include_dirs=[
            "pydensecrf/densecrf/include",
            "pydensecrf/densecrf/external/liblbfgs/include",
        ],
    ),
]

setup(
    name="pydensecrf",
    version="1.0",
    ext_modules=ext_modules,
    packages=["pydensecrf"],
)

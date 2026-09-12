# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import os.path

from spack_repo.builtin.build_systems.compiler import CompilerPackage
from spack_repo.builtin.build_systems.generic import Package

from spack.package import *


class Fj(Package, CompilerPackage):
    """The Fujitsu compiler system is a high performance, production quality
    code generation tool designed for high performance parallel
    computing workloads.

    This is a site-local override of the builtin ``fj`` package. It is
    identical to the builtin definition except that ``headers`` is
    overridden to expose no headers.

    Reason: since Spack models compilers as ordinary dependencies, the
    builtin package's default ``headers`` handler walks
    ``prefix/include`` (i.e. the Fujitsu compiler installation's own
    include directory, e.g. ``/opt/FJSVxtclanga/tcsds-*/include``) and
    the resulting directory is injected as an extra ``-I`` flag
    (via SPACK_INCLUDE_DIRS) into every package built ``%fj``. That
    directory also contains Fujitsu/Clang's special ACLE header
    ``arm_sve.h``, which must only be picked up through the compiler's
    own implicit header search path. Passing it explicitly via ``-I``
    breaks recognition of the compiler-internal SVE builtin types
    (e.g. ``__builtin_v256u1x2``), which made fujitsu-fftw's SVE
    codelets (``double/dft/simd/sve/*.c``) fail with
    "unknown type name" errors. gcc-runtime works around the same
    class of problem the same way (see its ``headers`` property).
    """

    homepage = "https://www.fujitsu.com/us/"

    maintainers("t-karatsu")

    provides("c", "cxx")
    provides("fortran")

    has_code = False

    def install(self, spec, prefix):
        raise InstallError(
            "Fujitsu compilers are not installable yet, but can be "
            "detected on a system where they are supplied by vendor"
        )

    compiler_languages = ["c", "cxx", "fortran"]
    c_names = ["fcc"]
    cxx_names = ["FCC"]
    fortran_names = ["frt"]
    compiler_version_regex = r"\((?:FCC|FRT)\) ([a-z\d.]+)"
    compiler_version_argument = "--version"

    debug_flags = ["-g"]
    opt_flags = ["-O0", "-O1", "-O2", "-O3", "-Ofast"]

    pic_flag = "-KPIC"
    openmp_flag = "-Kopenmp"

    compiler_wrapper_link_paths = {
        "c": os.path.join("fj", "fcc"),
        "cxx": os.path.join("fj", "case-insensitive", "FCC"),
        "fortran": os.path.join("fj", "frt"),
    }

    implicit_rpath_libs = ["libfj90i", "libfj90f", "libfjsrcinfo"]

    def _standard_flag(self, *, language, standard):
        flags = {
            "cxx": {
                "98": "-std=c++98",
                "11": "-std=c++11",
                "14": "-std=c++14",
                "17": "-std=c++17",
            },
            "c": {"99": "-std=c99", "11": "-std=c11"},
        }
        return flags[language][standard]

    @property
    def headers(self):
        # Don't leak the compiler installation's own include directory
        # (which holds Fujitsu/Clang-internal headers such as
        # arm_sve.h) into dependents' -I search paths.
        return HeaderList([])

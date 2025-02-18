"""setup.py to generate distributable"""

#
# Copyright 2023 ZestFinance All Rights Reserved
#
#
#
# It is prohibited to copy, in whole or in part, modify, directly or
# indirectly reverse engineer, disassemble, decompile, decode or adapt
# this code or any portion or aspect thereof, or otherwise attempt to
# derive or gain access to any part of the source code or algorithms
# contained herein as provided in your ZAML agreement.
#
import os
import shutil
import sysconfig
from pathlib import Path

from setuptools import Extension, find_packages, setup
from setuptools.command.install_lib import install_lib

CYTHONIZE = os.environ.get("CYTHONIZE", "False").lower() == "true"
SKIP_CLEAN = os.environ.get("SKIP_CLEAN", "False").lower() == "true"

MODULE_NAME = "example_package"

# clean up old egg-info & temp build folder to prevent interfering with builds
shutil.rmtree(Path(f"{MODULE_NAME}.egg-info"), True)
if CYTHONIZE and not SKIP_CLEAN:
    shutil.rmtree(Path("build"), True)

current_directory = Path(__file__).parent

with open(current_directory / "requirements.txt", "r", encoding="utf-8") as fp:
    REQUIRED = fp.read().splitlines()

VERSION_FILE = current_directory / MODULE_NAME / "VERSION"

with open(VERSION_FILE, "r", encoding="utf-8") as f:
    __version__ = f.read().strip()

with open(current_directory / "requirements-dev.txt", "r", encoding="utf-8") as file:
    dev_req = file.read().splitlines()

extras_require = {"dev": dev_req}

all_extras_require = []
for key, extras in extras_require.items():
    if key != "dev":
        all_extras_require.extend(extras)

extras_require["all"] = all_extras_require

ext_modules = []

if CYTHONIZE:
    import Cython.Compiler.Options
    from Cython.Build import cythonize

    cython_module = Extension(f"{MODULE_NAME}/*", [f"{MODULE_NAME}/**/*.py"])

    # Disable the inclusion of docstrings in the generated code
    Cython.Compiler.Options.docstrings = False

    cython_module.cython_c_in_temp = True
    ext_modules = cythonize(
        [cython_module],
        compiler_directives={"language_level": "3", "emit_code_comments": False},
        build_dir="build",
    )


class InstallLibFilter(install_lib):
    """override class to keep python wheel free of .py files that have associated .so files"""

    def get_exclusions(self):
        exclusions: set = super().get_exclusions()

        # ext_suffix is platform-specific .so suffix, like '.cpython-310-darwin.so'
        ext_suffix = sysconfig.get_config_var("EXT_SUFFIX")

        build_dir = Path(self.build_dir)

        for py_file in build_dir.glob("**/*.py"):
            if py_file.with_suffix(ext_suffix).exists():
                # if an .so file exists for the .py file, exclude the .py file
                # using os.path.join to get same path forming behavior as install_lib
                exclusions.add(os.path.join(self.install_dir, py_file.relative_to(build_dir)))

        return exclusions


setup(
    name="example-package",
    version=__version__,
    description="Example Package Library",
    url="https://github.com/Katlean/backend-services-python-template",
    packages=find_packages(include=[f"{MODULE_NAME}*"]),
    python_requires=">=3.10",
    install_requires=REQUIRED,
    extras_require=extras_require,
    zip_safe=False,
    include_package_data=True,
    ext_modules=ext_modules,
    cmdclass={"install_lib": InstallLibFilter if CYTHONIZE else install_lib},
)

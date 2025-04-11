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

MODULE_NAME = "ztestdata"

# clean up old egg-info & temp build folder to prevent interfering with builds
shutil.rmtree(Path(f"{MODULE_NAME}.egg-info"), True)

current_directory = Path(__file__).parent

with open(current_directory / "requirements.txt", "r", encoding="utf-8") as fp:
    REQUIRED = fp.read().splitlines()

VERSION_FILE = current_directory / MODULE_NAME / ".VERSION"

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
    cmdclass={"install_lib": install_lib},
)

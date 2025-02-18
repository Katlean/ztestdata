"""houses utility functions"""
# Copyright 2023 Zest AI All Rights Reserved
##
##
##
# It is prohibited to copy, in whole or in part, modify, directly or indirectly
# reverse engineer, disassemble, decompile, decode or adapt this code or any portion
# or aspect thereof, or otherwise attempt to derive or gain access to any part of
# the source code or algorithms contained herein as provided in your ZAML agreement.
##

from pathlib import Path


def get_version():
    """Gets the version of the example_package

    :return: version
    :rtype: str
    """
    version_file = Path(__file__).parent / "VERSION"
    with open(version_file, encoding="utf-8") as file:
        return file.read().strip()

#
# Copyright 2024 Zest AI All Rights Reserved
#
#
#
# It is prohibited to copy, in whole or in part, modify, directly or
# indirectly reverse engineer, disassemble, decompile, decode or adapt
# this code or any portion or aspect thereof, or otherwise attempt to
# derive or gain access to any part of the source code or algorithms
# contained herein as provided in your ZAML agreement.
#
import logging
import os
import warnings

from pathlib import Path

VERSION_FILE = os.path.join(os.path.dirname(__file__), '.VERSION')
with open(VERSION_FILE) as f:
    __version__ = f.read().strip()

logger = logging.getLogger('ztestdata')

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def user():
    username = os.environ.get('USER')
    if username is not None:
        return username
    else:
        logger.debug(
            "Username could not be determined from USER environment variable. Using home directory name."
        )
        return os.path.basename(str(Path.home()))


home = str(Path.home())

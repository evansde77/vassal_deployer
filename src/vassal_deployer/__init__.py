#!/usr/bin/env python
"""
vassal_deployer

"""
__version__="0.0.1"

import os

from .logger import get_logger

logger = get_logger(
    os.environ.get('VASSAL_DEPLOYER_LOG'),
    os.environ.get('VASSAL_DEPLOYER_STDOUT', False)
)

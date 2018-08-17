# -*- coding: utf-8 -*-

import logging
import shlex
import subprocess


LOGGER = logging.getLogger(__name__)


def sh(command):
    LOGGER.debug("Shell command: {}".format(command))
    subprocess.check_call(shlex.split(command))

# -*- coding: utf-8 -*-
"""Blah blah balh..."""

import logging

from . import utils


LOGGER = logging.getLogger("__name__")


class Gateway(object):
    """Wrapper around the 'cangw' tool from Linux can-utils.


    """

    def __init__(self):
        pass

    def add_rule(self, src_netdev, dst_netdev):
        utils.sh("cangw -A -s {} -d {} -e".format(src_netdev, dst_netdev))

    def remove_rule(self, src_netdev, dst_netdev):
        utils.sh("cangw -D -s {} -d {} -e".format(src_netdev, dst_netdev))

    def rules(self):
        utils.sh("cangw -L")

    def flush(self):
        """Flush the cangw table.


        .. warning:: This flushed the table **system-wide**.
        """
        utils.sh("cangw -F")

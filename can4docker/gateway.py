# -*- coding: utf-8 -*-
"""Blah blah balh..."""

import logging

from . import utils


LOGGER = logging.getLogger("__name__")


class Gateway(object):
    """Wrapper around the 'cangw' tool from Linux can-utils.


    """

    def __init__(self):
        self.rules = {}

    def add_rule(self, src_netdev, dst_netdev):
        if (not self.rules.get(src_netdev, None)):
            self.rules[src_netdev] = []
        if not dst_netdev in self.rules[src_netdev]:
            utils.sh("cangw -A -s {} -d {} -e".format(src_netdev, dst_netdev))
            self.rules[src_netdev].append(dst_netdev)

    def remove_rule(self, src_netdev, dst_netdev):
        rules = self.rules.get(src_netdev, None)
        if rules and dst_netdev in rules:
            utils.sh("cangw -D -s {} -d {} -e".format(src_netdev, dst_netdev))
            self.rules.remove(dst_netdev)

# -*- coding: utf-8 -*-

import logging

import pyroute2

from . import utils


LOGGER = logging.getLogger(__name__)


class EndPoint(object):

    def __init__(self, endpoint_id):
        self.endpoint_id = endpoint_id
        self.if_name = "vcan{}".format(endpoint_id[:8])
        self.peer_if_name = "{}p".format(self.if_name)

    def create_resource(self):
        LOGGER.debug("Creating resource for enpoint {}...".format(self.endpoint_id))
        with pyroute2.IPDB() as ipdb:
            with ipdb.create(kind='vxcan', ifname=self.if_name,
                             peer=self.peer_if_name) as link:
                link.up()
        LOGGER.debug("Created resource for enpoint {}.".format(self.endpoint_id))

    def delete_resource(self):
        LOGGER.debug("Deleting resource for enpoint {}...".format(self.endpoint_id))
        with pyroute2.IPDB() as ipdb:
            with ipdb.interfaces[self.if_name] as link:
                link.down()
                link.remove()
        LOGGER.debug("Deleted resource for enpoint {}.".format(self.endpoint_id))

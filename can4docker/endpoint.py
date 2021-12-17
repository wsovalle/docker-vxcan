# -*- coding: utf-8 -*-

import logging

import pyroute2

from . import utils


LOGGER = logging.getLogger(__name__)


class EndPoint(object):

    def __init__(self, endpoint_id, can_dev, can_id):
        self.endpoint_id = endpoint_id
        self.if_name = "vcan{}".format(endpoint_id[:8])
        self.peer_if_name = can_dev + str(can_id)
        self.peer_namespace = None

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

    def attach(self, namespace):
        LOGGER.debug("Attaching enpoint {} to namespace {}...".format(
            self.endpoint_id, namespace))
        LOGGER.debug("Changing namespace...")
        with pyroute2.IPDB() as ipdb:
            with ipdb.interfaces[self.peer_if_name] as link:
                link.net_ns_fd = namespace
        LOGGER.debug("Bringing up...")
        with pyroute2.IPDB(nl=pyroute2.NetNS(namespace)) as ipdb:
            with ipdb.interfaces[self.peer_if_name] as link:
                link.up()
        self.peer_namespace = namespace
        LOGGER.debug("Attached enpoint {} to namespace {}.".format(
            self.endpoint_id, namespace))

    def detach(self):
        LOGGER.debug("Detaching enpoint {} from namespace {}...".format(
            self.endpoint_id, self.peer_namespace))
        with pyroute2.IPDB(nl=pyroute2.NetNS(self.peer_namespace)) as ipdb:
            with ipdb.interfaces[self.peer_if_name] as link:
                link.down()
                link.net_ns_fd = ""
        LOGGER.debug("Detached enpoint {} from namespace {}.".format(
            self.endpoint_id, self.peer_namespace))

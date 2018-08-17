# -*- coding: utf-8 -*-

import logging

import docker

from . import utils
from .network import Network
from .endpoint import EndPoint

LOGGER = logging.getLogger(__name__)


class NetworkManager(object):
    """A CAN network manager."""

    def __init__(self):
        self.networks = {}

    def activate(self):
        utils.sh("mkdir -p /var/run/netns/")
        client = docker.from_env()
        for network in client.networks.list():
            network.reload()
            if network.attrs['Driver'] != 'vxcan':
                continue
            network_id = network.attrs['Id']
            LOGGER.info("Adding network {}".format(network_id))
            can_network = Network(network_id)
            self.networks[network_id] = can_network
            for container_id, container_attrs in network.attrs['Containers'].items():
                endpoint_id = container_attrs['EndpointID']
                LOGGER.info("Adding endpoint {}".format(endpoint_id))
                can_endpoint = EndPoint(endpoint_id)
                can_network.add_endpoint(can_endpoint)

    def desactivate(self):
        """ Cleanup done during shutdown of server."""
        pass

    def create_network(self, network_id, options):
        network = Network(network_id)
        network.create_resource()
        self.networks[network_id] = network

    def delete_network(self, network_id):
        network = self.networks.pop(network_id)
        network.delete_resource()

    def create_endpoint(self, network_id, endpoint_id, options):
        endpoint = EndPoint(endpoint_id)
        self.networks[network_id].add_endpoint(endpoint)
        endpoint.create_resource()

    def delete_endpoint(self, network_id, endpoint_id):
        endpoint = self.networks[network_id].remove_endpoint(endpoint_id)
        endpoint.delete_resource()

    def attach_endpoint(self, network_id, endpoint_id, sandbox_key, options):
        namespace_id = sandbox_key.split('/')[-1]
        self.networks[network_id].attach_endpoint(endpoint_id, namespace_id)

    def detach_endpoint(self, network_id, endpoint_id):
        self.networks[network_id].detach_endpoint(endpoint_id)

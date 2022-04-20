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

    def create_network(self, network_id, options):
        can_dev = options['com.docker.network.generic'].get('vxcan.dev', 'vcan')
        can_peer = options['com.docker.network.generic'].get('vxcan.peer', 'vxcanp')
        can_id = options['com.docker.network.generic'].get('vxcan.id', network_id)
        network = Network(network_id, can_dev, can_id, can_peer)
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
        can_peer = options.get('vxcan.peer', None)
        return self.networks[network_id].attach_endpoint(endpoint_id, namespace_id, can_peer)

    def detach_endpoint(self, network_id, endpoint_id):
        self.networks[network_id].detach_endpoint(endpoint_id)

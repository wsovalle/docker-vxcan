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
        LOGGER.info("Activating plugin..")
        return  # FIXME: load from env
        client = docker.from_env()
        for network in client.networks.list():
            network.reload()
            if network.attrs['Driver'] != 'chgans/can4docker':
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
        can_dev = options['com.docker.network.generic'].get('vxcan.dev', 'vxcan')
        can_peer = options['com.docker.network.generic'].get('vxcan.peer', 'vcan')
        can_id = options['com.docker.network.generic'].get('vxcan.id', network_id)
        network = Network(network_id, can_dev, can_id, can_peer)
        network.create_resource()
        self.networks[network_id] = network

    def delete_network(self, network_id):
        network = self.networks.pop(network_id)
        network.delete_resource()

    def create_endpoint(self, network_id, endpoint_id, options):
        can_dev = options.get('vxcan.dev', self.networks[network_id].can_peer)
        can_id = options.get('vxcan.id', self.networks[network_id].can_id)
        endpoint = EndPoint(endpoint_id, can_dev, can_id)
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

# -*- coding: utf-8 -*-

from . import utils
from .gateway import Gateway

class Network(object):

    def __init__(self, network_id):
        self.network_id = network_id
        self.if_name = "vcan{}".format(network_id[:8])
        self.endpoints = {}
        self.gateway = Gateway()

    def create_resource(self):
        utils.sh("ip link add dev {0} type vcan".format(self.if_name))
        utils.sh("ip link set dev {0} alias 'CAN Bus for Docker Network {1}'".format(self.if_name, self.network_id))
        utils.sh("ip link set {0} up".format(self.if_name))

    def delete_resource(self):
        utils.sh("ip link del {0}".format(self.if_name))

    def add_endpoint(self, endpoint):
        self.endpoints[endpoint.endpoint_id] = endpoint

    def remove_endpoint(self, endpoint_id):
        return self.endpoints.pop(endpoint_id)
    
    def attach_endpoint(self, endpoint_id, namespace_id):
        endpoint = self.endpoints[endpoint_id]
        endpoint.attach(namespace_id)
        for other_id, other in self.endpoints.items():
            if other_id != endpoint_id:
                self.gateway.add_rule(other.if_name, endpoint.if_name)
                self.gateway.add_rule(endpoint.if_name, other.if_name)

    def detach_endpoint(self, endpoint_id):
        endpoint = self.endpoints[endpoint_id]
        for other_id, other in self.endpoints.items():
            if other_id != endpoint_id:
                self.gateway.remove_rule(other.if_name, endpoint.if_name)
                self.gateway.remove_rule(endpoint.if_name, other.if_name)
        endpoint.detach()
        

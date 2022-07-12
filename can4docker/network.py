# -*- coding: utf-8 -*-

import pyroute2

from .gateway import Gateway

class Network(object):

    def __init__(self, network_id, can_dev, can_id, can_peer):
        self.network_id = network_id
        self.can_id = can_id
        self.can_peer = can_peer
        self.if_name = "{}{}".format(can_dev, can_id)
        self.endpoints = {}
        self.gateway = Gateway()

    def create_resource(self):
        with pyroute2.NDB(db_provider='sqlite3', db_spec=':memory:') as ndb:
            if self.if_name not in ndb.interfaces:
                ndb.interfaces.create(kind='vcan', ifname=self.if_name).set('state', 'up').commit()

    def delete_resource(self):
        with pyroute2.NDB(db_provider='sqlite3', db_spec=':memory:') as ndb:
            if self.if_name in ndb.interfaces:
                ndb.interfaces[self.if_name].set('state', 'down').remove().commit()

    def add_endpoint(self, endpoint):
        self.endpoints[endpoint.endpoint_id] = endpoint

    def remove_endpoint(self, endpoint_id):
        return self.endpoints.pop(endpoint_id)

    def attach_endpoint(self, endpoint_id, namespace_id, can_peer):
        endpoint = self.endpoints[endpoint_id]
        self.gateway.add_rule(self.if_name, endpoint.if_name)
        self.gateway.add_rule(endpoint.if_name, self.if_name)
        for other_id, other in self.endpoints.items():
            if other_id != endpoint_id:
                self.gateway.add_rule(other.if_name, endpoint.if_name)
                self.gateway.add_rule(endpoint.if_name, other.if_name)
        if not can_peer:
            can_peer = self.can_peer
        return {
            "InterfaceName": {
                "SrcName": endpoint.peer_if_name,
                "DstPrefix": can_peer
            }
        }

    def detach_endpoint(self, endpoint_id):
        endpoint = self.endpoints[endpoint_id]
        for other_id, other in self.endpoints.items():
            if other_id != endpoint_id:
                self.gateway.remove_rule(other.if_name, endpoint.if_name)
                self.gateway.remove_rule(endpoint.if_name, other.if_name)
        self.gateway.remove_rule(endpoint.if_name, other.if_name)
        self.gateway.remove_rule(other.if_name, endpoint.if_name)

# -*- coding: utf-8 -*-
""" Module providing the FIXME and Flask methods.
Following Docker Network endpoints are routed below:

    '/Plugin.Activate'
    '/NetworkDriver.GetCapabilities'
    '/NetworkDriver.CreateNetwork'
    '/NetworkDriver.DeleteNetwork'
    '/NetworkDriver.CreateEndpoint'
    '/NetworkDriver.EndpointOperInfo'
    '/NetworkDriver.DeleteEndpoint'
    '/NetworkDriver.Join'
    '/NetworkDriver.Leave'
    '/NetworkDriver.DiscoverNew'
    '/NetworkDriver.DiscoverDelete'

"""
from __future__ import unicode_literals

import argparse
import logging
import os
import shlex
import subprocess
import sys

import docker
# import pyroute2

from flask import Flask
from flask import jsonify
from flask import request

assert sys.version_info[0] >= 3

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 1331
APPLICATION = Flask("can4docker")
LOGGER = logging.getLogger("can4docker")


def sh(command):
    LOGGER.debug("Shell command: {}".format(command))
    subprocess.check_call(shlex.split(command))

class Gateway(object):

    def __init__(self):
        pass

    def add_rule(self, src_netdev, dst_netdev):
        sh("cangw -A -s {} -d {} -e".format(src_netdev, dst_netdev))

    def remove_route(self, src_netdev, dst_netdev):
        sh("cangw -D -s {} -d {} -e".format(src_netdev, dst_netdev))

    def rules(self):
        sh("cangw -L")

    def flush(self):
        sh("cangw -F")
    
class EndPoint(object):

    def __init__(self, endpoint_id):
        self.endpoint_id = endpoint_id
        self.if_name = "vcan{}".format(endpoint_id[:8])
        self.peer_if_name = "{}p".format(self.if_name)
        self.peer_namespace = None

    def create_resource(self):
        sh("ip link add {0} type vxcan peer name {0}p".format(self.if_name, self.peer_if_name))
        sh("ip link set {0} up".format(self.if_name))

    def delete_resource(self):
        sh("ip link set {0} down".format(self.if_name))
        sh("ip link del {0}".format(self.if_name))
        
    def attach(self, namespace):
        self.peer_namespace = namespace
        sh("rm -f /var/run/netns/{0}".format(self.peer_namespace))
        sh("ln -s /var/run/docker/netns/{0} /var/run/netns/".format(self.peer_namespace))
        sh("ip link set {0} netns {1}".format(self.peer_if_name, self.peer_namespace))
        sh("ip netns exec {0} ip link set {1} up".format(self.peer_namespace, self.peer_if_name))
        pass

    def detach():
        # if_name = "vcan{}".format(network_id[:8])
        # ep_name = "vcan{}".format(endpoint_id[:8])
        # net_ns = sandbox_key.split('/')[-1]
        # sh("ip netns exec {net_ns} ip link set {ep_name} down".format(net_ns=net_ns, ep_name=ep_name))
        # sh("ip netns exec {net_ns} ip link set {ep_name} netns 1".format(ep_name=ep_name, net_ns=net_ns))
        # sh("unlink /var/run/netns/{net_ns}")
        return

class Network(object):

    def __init__(self, network_id):
        self.network_id = network_id
        self.if_name = "vcan{}".format(network_id[:8])
        self.endpoints = {}
        self.gateway = Gateway()

    def create_resource(self):
        sh("ip link add dev {0} type vcan".format(self.if_name))
        sh("ip link set {0} up".format(self.if_name))

    def delete_resource(self):
        sh("ip link del {0}".format(self.if_name))

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
        
class NetworkManager(object):
    """A CAN network manager."""

    def __init__(self):
        self.networks = {}
        pass

    def activate(self):
        sh("mkdir -p /var/run/netns/")
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
    
def dispatch(data):
    """ To jsonify the response with correct HTTP status code.

    Status codes:
        200: OK
        400: Error

    Err in JSON is non empty if there is an error.

    """
    if ('Err' in data and data['Err'] != ""):
        code = 400
    else:
        code = 200
    resp = jsonify(data)
    resp.status_code = code
    LOGGER.debug("{}, {}".format(code, data))
    return resp


@APPLICATION.route('/Plugin.Activate', methods=['POST'])
def activate():
    """ Routes Docker Network '/Plugin.Activate'."""
    # TODO: Load existing OS resources
    return dispatch({"Implements": ["NetworkDriver"]})

@APPLICATION.route('/NetworkDriver.GetCapabilities', methods=['POST'])
def capabilities():
    """ Routes Docker Network '/NetworkDriver.GetCapabilities'."""
    return dispatch({"Scope": "local"})

@APPLICATION.route('/NetworkDriver.CreateNetwork', methods=['POST'])
def create_network():
    """ Routes Docker Network '/NetworkDriver.CreateNetwork'."""
    manager = APPLICATION.config['network_manager']
    data = request.get_json(force=True)
    LOGGER.debug("/NetworkDriver.CreateNetwork: {}".format(data))
    net_id = data['NetworkID']
    options = data['Options']
    try:
        manager.create_network(net_id, options)
    except Exception as e:
        return dispatch({
            "Err": "Failed to create the network {0} : {1}".format(
                net_id, str(e))
        })

    return dispatch({"Err": ""})

@APPLICATION.route('/NetworkDriver.DeleteNetwork', methods=['POST'])
def delete_network():
    """ Routes Docker Network '/NetworkDriver.DeleteNetwork'."""
    manager = APPLICATION.config['network_manager']
    data = request.get_json(force=True)
    LOGGER.debug("/NetworkDriver.DeleteNetwork: {}".format(data))
    net_id = data['NetworkID']
    try:
        manager.delete_network(net_id)
    except Exception as e:
        return dispatch({
            "Err": "Failed to delete the network {0} : {1}".format(
                net_id, str(e))
        })

    return dispatch({"Err": ""})

@APPLICATION.route('/NetworkDriver.CreateEndpoint', methods=['POST'])
def create_endpoint():
    """ Routes Docker Network '/NetworkDriver.CreateEndpoint'."""
    manager = APPLICATION.config['network_manager']
    data = request.get_json(force=True)
    LOGGER.debug("/NetworkDriver.CreateEndpoint: {}".format(data))
    network_id = data['NetworkID']
    endpoint_id = data['EndpointID']
    options = data['Options']
    try:
        manager.create_endpoint(network_id, endpoint_id, options)
    except Exception as e:
        return dispatch({
            "Err": "Failed to create the network endpoint {0}:{1} : {2}".format(
                network_id, endpoint_id, str(e))
        })

    return dispatch({"Err": ""})

@APPLICATION.route('/NetworkDriver.DeleteEndpoint', methods=['POST'])
def delete_endpoint():
    """ Routes Docker Network '/NetworkDriver.DeleteEndpoint'."""
    manager = APPLICATION.config['network_manager']
    data = request.get_json(force=True)
    LOGGER.debug("/NetworkDriver.DeleteEndpoint: {}".format(data))
    network_id = data['NetworkID']
    endpoint_id = data['EndpointID']
    try:
        manager.delete_endpoint(network_id, endpoint_id)
    except Exception as e:
        return dispatch({
            "Err": "Failed to delete the network endpoint {0}:{1} : {2}".format(
                network_id, endpoint_id, str(e))
        })

    return dispatch({"Err": ""})

@APPLICATION.route('/NetworkDriver.EndpointOperInfo', methods=['POST'])
def endpoint_operational_info():
    """ Routes Docker Network '/NetworkDriver.EndpointOperInfo'."""
    manager = APPLICATION.config['network_manager']
    data = request.get_json(force=True)
    LOGGER.debug("/NetworkDriver.EndpointOperInfo: {}".format(data))
    network_id = data['NetworkID']
    endpoint_id = data['EndpointID']
    try:
        pass
    except Exception as e:
        return dispatch({
            "Err": "Failed to retreive enpot orperational info: {}".format(
                x=str(e))
        })

    return dispatch({"Err": ""})

@APPLICATION.route('/NetworkDriver.Join', methods=['POST'])
def join():
    """ Routes Docker Network '/NetworkDriver.Join'."""
    manager = APPLICATION.config['network_manager']
    data = request.get_json(force=True)
    LOGGER.debug("/NetworkDriver.Join: {}".format(data))
    network_id = data['NetworkID']
    endpoint_id = data['EndpointID']
    sandbox_key = data['SandboxKey']
    options = data['Options']
    try:
        manager.attach_endpoint(network_id, endpoint_id, sandbox_key, options)
    except Exception as e:
        return dispatch({
            "Err": "Failed to join {c} to the network endpoint {n}:{e} : {x}".format(
                n=network_id, e=endpoint_id, x=str(e), c=sandbox_key)
        })

    return dispatch({"Err": ""})

@APPLICATION.route('/NetworkDriver.Leave', methods=['POST'])
def leave():
    """ Routes Docker Network '/NetworkDriver.Leave'."""
    manager = APPLICATION.config['network_manager']
    data = request.get_json(force=True)
    LOGGER.debug("/NetworkDriver.Leave: {}".format(data))
    network_id = data['NetworkID']
    endpoint_id = data['EndpointID']
    try:
        manager.detach_endpoint(network_id, endpoint_id)
    except Exception as e:
        return dispatch({
            "Err": "Failed to leave network endpoint {n}:{e} : {x}".format(
                n=network_id, e=endpoint_id, x=str(e))
        })

    return dispatch({"Err": ""})

def shutdown_server():
    """ Utility method for shutting down the server."""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@APPLICATION.route('/shutdown', methods=['POST'])
def shutdown():
    """ API end point exposed to shutdown the server."""
    shutdown_server()
    return 'Server shutting down...'


parser = argparse.ArgumentParser(description='Arguments to CAN ')

parser.add_argument('-H', '--host', default=DEFAULT_HOST, help='Host to listen on')
parser.add_argument('-p', '--port', default=DEFAULT_PORT, help='Port to listen on')


def start():

    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    network_manager = NetworkManager()
    network_manager.activate()
    APPLICATION.config['network_manager'] = network_manager

    try:
        APPLICATION.run(host=args.host, port=args.port)
    finally:
        network_manager.cleanup()


if __name__ == '__main__':
    start()

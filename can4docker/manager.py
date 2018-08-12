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

from flask import Flask
from flask import jsonify
from flask import request

assert sys.version_info[0] >= 3

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 1331
APPLICATION = Flask(__name__)
LOGGER = logging.getLogger(__name__)


def sh(command):
    LOGGER.debug("Shell command: {}".format(command))
    subprocess.check_call(shlex.split(command))

class NetworkManager(object):
    """A CAN network manager."""

    def __init__(self):
        pass

    def cleanup(self):
        """ Cleanup done during shutdown of server."""
        pass

    def create_network(self, network_id, options):
        if_name = "vcan{}".format(network_id[:8])
        sh("ip link add dev {dev} type vcan".format(dev=if_name))
        sh("ip link set {dev} up".format(dev=if_name))

    def delete_network(self, network_id):
        if_name = "vcan{}".format(network_id[:8])
        sh("ip link del {dev}".format(dev=if_name))

    def create_endpoint(self, network_id, endpoint_id, options):
        if_name = "vcan{}".format(network_id[:8])
        ep_name = "vcan{}".format(endpoint_id[:8])
        sh("ip link add {ep} type vxcan peer name {ep}p".format(ep=ep_name))
        sh("ip link set {ep} up".format(ep=ep_name))

    def delete_endpoint(self, network_id, endpoint_id):
        if_name = "vcan{}".format(network_id[:8])
        ep_name = "vcan{}".format(endpoint_id[:8])
        sh("ip link set {ep} down".format(ep=ep_name))
        sh("ip link del {ep}".format(ep=ep_name))

    def join(self, network_id, endpoint_id, sandbox_key, options):
        if_name = "vcan{}".format(network_id[:8])
        ep_name = "vcan{}".format(endpoint_id[:8])
        net_ns = sandbox_key.split('/')[-1]
        sh("mkdir -p /var/run/netns/")
        sh("ln -s {sandbox_key} /var/run/netns/".format(sandbox_key=sandbox_key))
        sh("ip link set {ep_name} netns {net_ns}".format(ep_name=ep_name, net_ns=net_ns))
        sh("ip netns exec {net_ns} ip link set {ep_name} up".format(net_ns=net_ns, ep_name=ep_name))

    def leave(self, network_id, enpoint_id):
        return
        # if_name = "vcan{}".format(network_id[:8])
        # ep_name = "vcan{}".format(endpoint_id[:8])
        # net_ns = sandbox_key.split('/')[-1]
        # sh("ip netns exec {net_ns} ip link set {ep_name} down".format(net_ns=net_ns, ep_name=ep_name))
        # sh("ip netns exec {net_ns} ip link set {ep_name} netns 1".format(ep_name=ep_name, net_ns=net_ns))
        # sh("unlink /var/run/netns/{net_ns}")
    
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
    LOGGER.debug("{}".format(data))
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
    LOGGER.debug("{}".format(data))
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
    LOGGER.debug("{}".format(data))
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
    LOGGER.debug("{}".format(data))
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
    LOGGER.debug("{}".format(data))
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
    LOGGER.debug("{}".format(data))
    network_id = data['NetworkID']
    endpoint_id = data['EndpointID']
    sandbox_key = data['SandboxKey']
    options = data['Options']
    try:
        manager.join(network_id, endpoint_id, sandbox_key, options)
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
    LOGGER.debug("{}".format(data))
    network_id = data['NetworkID']
    endpoint_id = data['EndpointID']
    try:
        manager.leave(network_id, endpoint_id)
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

    logging.basicConfig(level=logging.DEBUG)
    args = parser.parse_args()
    network_manager = NetworkManager()
    APPLICATION.config['network_manager'] = network_manager

    try:
        APPLICATION.run(host=args.host, port=args.port)
    finally:
        network_manager.cleanup()


if __name__ == '__main__':
    start()

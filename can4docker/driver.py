# -*- coding: utf-8 -*-
"""Blah blah blah..."""

import logging

from .manager import NetworkManager
from flask import Flask
from flask import jsonify
from flask import request


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

APPLICATION = Flask("can4docker")
NETWORK_MANAGER = NetworkManager()
APPLICATION.config['network_manager'] = NETWORK_MANAGER


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


@APPLICATION.route('/NetworkDriver.GetCapabilities', methods=['POST'])
def capabilities():
    """ Routes Docker Network '/NetworkDriver.GetCapabilities'."""
    LOGGER.debug("/NetworkDriver.GetCapabilities")
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
                str(e))
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
        res = manager.attach_endpoint(network_id, endpoint_id, sandbox_key, options)
    except Exception as e:
        return dispatch({
            "Err": "Failed to join {c} to the network endpoint {n}:{e} : {x}".format(
                n=network_id, e=endpoint_id, x=str(e), c=sandbox_key)
        })

    return dispatch(res)


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

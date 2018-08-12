# -*- coding: utf-8 -*-

from . import utils


class EndPoint(object):

    def __init__(self, endpoint_id):
        self.endpoint_id = endpoint_id
        self.if_name = "vcan{}".format(endpoint_id[:8])
        self.peer_if_name = "{}p".format(self.if_name)
        self.peer_namespace = None

    def create_resource(self):
        utils.sh("ip link add {0} type vxcan peer name {0}p".format(self.if_name, self.peer_if_name))
        utils.sh("ip link set dev {0} alias 'CAN Bus for Docker EndPoint {1}'".format(self.if_name, self.endpoint_id))
        utils.sh("ip link set {0} up".format(self.if_name))

    def delete_resource(self):
        utils.sh("ip link set {0} down".format(self.if_name))
        utils.sh("ip link del {0}".format(self.if_name))
        
    def attach(self, namespace):
        self.peer_namespace = namespace
        utils.sh("rm -f /var/run/netns/{0}".format(self.peer_namespace))
        utils.sh("ln -s /var/run/docker/netns/{0} /var/run/netns/".format(self.peer_namespace))
        utils.sh("ip link set dev {0} alias 'CAN Bus for Docker Sandbox {1}'".format(self.peer_if_name, self.endpoint_id))
        utils.sh("ip link set {0} netns {1}".format(self.peer_if_name, self.peer_namespace))
        utils.sh("ip netns exec {0} ip link set {1} up".format(self.peer_namespace, self.peer_if_name))
        pass

    def detach():
        # if_name = "vcan{}".format(network_id[:8])
        # ep_name = "vcan{}".format(endpoint_id[:8])
        # net_ns = sandbox_key.split('/')[-1]
        # utils.sh("ip netns exec {net_ns} ip link set {ep_name} down".format(net_ns=net_ns, ep_name=ep_name))
        # utils.sh("ip netns exec {net_ns} ip link set {ep_name} netns 1".format(ep_name=ep_name, net_ns=net_ns))
        # utils.sh("unlink /var/run/netns/{net_ns}")
        return

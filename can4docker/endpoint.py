# -*- coding: utf-8 -*-

import logging

import pyroute2

from . import utils


LOGGER = logging.getLogger(__name__)


class EndPoint(object):

    def __init__(self, endpoint_id):
        self.endpoint_id = endpoint_id
        self.if_name = "vcan{}".format(endpoint_id[:8])
        self.peer_if_name = "{}p".format(self.if_name)

    def create_resource(self):
        LOGGER.debug("Creating resource for endpoint {}...".format(self.endpoint_id))
        with pyroute2.NDB(db_provider='sqlite3',db_spec=':memory:') as ndb:
            ndb.interfaces.create(kind='vxcan', ifname=self.if_name,
                                  peer=self.peer_if_name).set('state','up').commit()
        LOGGER.debug("Created resource for endpoint {}.".format(self.endpoint_id))

    def delete_resource(self):
        LOGGER.debug("Deleting resource for endpoint {}...".format(self.endpoint_id))
        with pyroute2.NDB(db_provider='sqlite3',db_spec=':memory:') as ndb:
            ndb.interfaces[self.if_name].set('state','down').remove().commit()
        LOGGER.debug("Deleted resource for endpoint {}.".format(self.endpoint_id))

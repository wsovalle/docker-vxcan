API Reference
=============

Overall architecture
--------------------

The plugin is implemented as a `Flask <http://flask.pocoo.org/>`_ application that handle the following HTTP RPCs:

 - ``/Plugin.Activate``
 - ``/NetworkDriver.GetCapabilities``
 - ``/NetworkDriver.CreateNetwork``
 - ``/NetworkDriver.DeleteNetwork``
 - ``/NetworkDriver.CreateEndpoint``
 - ``/NetworkDriver.EndpointOperInfo``
 - ``/NetworkDriver.DeleteEndpoint``
 - ``/NetworkDriver.Join``
 - ``/NetworkDriver.Leave``

.. note:: For more information about these RPCs, see `Docker's libnetwork Remote Drivers <https://github.com/docker/libnetwork/blob/master/docs/remote.md>`_

In a nutshell:
 - The :class:`~can4docker.manager.NetworkManager` manages :class:`~can4docker.network.Network` 's that represent virtual CAN busses.
 - The :class:`~can4docker.network.Network` manages attachable :class:`~can4docker.endpoint.EndPoint` and inter-connect them to a CAN bus using a :class:`~can4docker.gateway.Gateway`.
 - The :class:`~can4docker.endpoint.EndPoint` encapsulates the underlying network interface(s) used to attach containers to the virtual CAN bus.
 - The :class:`~can4docker.gateway.Gateway` is a very simple-and-stupid wrapper around the ``cangw`` command line utility.
 - Finally, the :mod:`~can4docker.driver` contains the Flask application whose sole purpose is to route RPC to the :class:`~can4docker.manager.NetworkManager`.

Pretty boring stuff really...


Manager
-------

.. automodule:: can4docker.manager
    :members:
    :undoc-members:
    :show-inheritance:


Network
-------

.. automodule:: can4docker.network
    :members:
    :undoc-members:
    :show-inheritance:

EndPoint
--------

.. automodule:: can4docker.endpoint
    :members:
    :undoc-members:
    :show-inheritance:

Gateway
-------

.. automodule:: can4docker.gateway
    :members:
    :undoc-members:
    :show-inheritance:

Driver
------

.. automodule:: can4docker.driver
    :members:
    :undoc-members:
    :show-inheritance:


Utils
-----

.. automodule:: can4docker.utils
    :members:
    :undoc-members:
    :show-inheritance:

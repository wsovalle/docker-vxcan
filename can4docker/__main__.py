import argparse
import logging

from . import NetworkManager
from .driver import APPLICATION

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 1331
LOGGER = logging.getLogger("can4docker")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Arguments to can4docker')
    parser.add_argument('-H', '--host', default=DEFAULT_HOST, help='Host to listen on')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT, help='Port to listen on')
    args = parser.parse_args()

    network_manager = NetworkManager()
    APPLICATION.config['network_manager'] = network_manager
    APPLICATION.run(host=args.host, port=args.port)

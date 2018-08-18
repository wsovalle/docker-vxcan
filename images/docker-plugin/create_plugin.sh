#!/bin/bash

set -euxo pipefail

DATADIR=_build/docker-plugin
ROOTFS=$DATADIR/rootfs
CONFIG=$DATADIR/config.json

#tag=$(python -c "import random; print('{:x}'.format(random.getrandbits(128)));")
tag=chgans/can4docker
docker build -t "$tag" -f images/docker-plugin/Dockerfile .
id=$(docker create "$tag" true)
rm -Rf $ROOTFS
mkdir -p $ROOTFS
docker export "$id" | tar -x -C $ROOTFS
docker rm -vf "$id"
#docker rmi "$tag"
cp images/docker-plugin/config.json $CONFIG
docker plugin rm -f chgans/can4docker || :
docker plugin create chgans/can4docker _build/docker-plugin/


# Validate docker works inside the container
# docker run -it --rm \
#        -v /var/run/docker.sock:/var/run/docker.sock \
#        "$tag" \
#        python -c 'import docker;docker.from_env().containers.run("hello-world")'

# Entrypoint:
# gunicorn -b unix:/var/run/can4docker.sock can4docker.driver:APPLICATION

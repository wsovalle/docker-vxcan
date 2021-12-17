#!/bin/bash -e

docker plugin ls --filter enabled=true | grep wsovalle/vxcan > /dev/null && \
    docker plugin disable wsovalle/vxcan
docker plugin ls | grep wsovalle/vxcan > /dev/null && \
    docker plugin rm wsovalle/vxcan
make build_package
images/docker-plugin/create_plugin.sh
docker plugin create wsovalle/vxcan _build/docker-plugin/
docker plugin enable wsovalle/vxcan

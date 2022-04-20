#!/bin/bash -e

USERNAME=$(git remote get-url origin | awk '{split($0,a,"[:/]*"); print a[2]}')
PLUGINNAME=$USERNAME/vxcan

# Remove active networks
docker network ls | grep can && \
    docker network ls | grep can | cut -f 1 -d ' ' | tr '\n' '\0' | xargs -0 -n1 docker network rm

# Disable the plugin
docker plugin ls --filter enabled=true | grep $PLUGINNAME > /dev/null && \
    docker plugin disable $PLUGINNAME

# Remove the plugin
docker plugin ls | grep $PLUGINNAME > /dev/null && \
    docker plugin rm $PLUGINNAME

# Build the can4docker Python package (make build_package)
python3 setup.py bdist_wheel

# Create the plugin rootfs and config.json
images/docker-plugin/create_plugin.sh

# Create and enable the plugin
docker plugin create $PLUGINNAME _build/docker-plugin/
docker plugin enable $PLUGINNAME

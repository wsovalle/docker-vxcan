# Overview

**VXCAN** Network Plugin provides ability to create CAN bus/networking for Docker containers.

It is based on original code from https://gitlab.com/chgans/can4docker, with some (minor) updates and fixes.

# Installation

Plugin doesn't need any specific steps to install, although it depends on kernel modules (available out-of-the-box in Ubuntu 20.04)

## Prerequisites

```
$ sudo modprobe vxcan
$ sudo modprobe can-gw
```

## Install plugin

```
$ docker plugin install wsovalle/vxcan
```

# Usage

This plugin fully supports `docker-compose`, eg.:

```
version: "3"
services:
  app_hub:
    image: ubuntu:20.04
    tty: true
    networks: 
      - canbus0
      - canbus1
  app_can0:
    image: ubuntu:20.04
    tty: true
    networks: [ canbus0 ]
  app_can1:
    image: ubuntu:20.04
    tty: true
    networks: [ canbus1 ]
networks:
  canbus0:
    driver: wsovalle/vxcan:latest
    driver_opts:
      vxcan.dev: can_host
      vxcan.peer: can_docker
      vxcan.id: 0
  canbus1:
    driver: wsovalle/vxcan:latest
    driver_opts:
      vxcan.dev: can_host
      vxcan.peer: can_docker
      vxcan.id: 1  
```

`$ docker-compose up`

## Driver options

### Network

On network level (`docker network create --opts `):
- `vxcan.dev` - CAN interface name on host, in example `can_hostX`
- `vxcan.id` - interface enumeration on host, in example `can_host0` for `canbus0` and `can_host1` for `canbus1`
- `vxcan.peer` - CAN interface name in a container, in example `can_dockerX`, where X is automatic enumeration provided by docker

Endpoint level (`docker network connect --driver-opts `, not supported by `compose`):
- `vxcan.peer` - CAN interface name in a container

# Development

## Manual build

Simple way of rebuilding plugin from sources is to use an attached script:

`$ images/docker-plugin/rebuild-plugin.sh`

It removes existing plugin, rebuilds from sources and enables freshly built version.

For separate steps refer to the contents of above script.

## References

Links to resources used while creating and fixing this plugin

- https://wiki.automotivelinux.org/_media/agl-distro/agl2018-socketcan.pdf
- https://www.spinics.net/lists/linux-can/msg00297.html
- https://www.lagerdata.com/articles/forwarding-can-bus-traffic-to-a-docker-container-using-vxcan-on-raspberry-pi
- https://chemnitzer.linux-tage.de/2021/media/programm/folien/210.pdf
- https://github.com/docker/go-plugins-helpers
- https://github.com/moby/libnetwork/blob/master/docs/remote.md

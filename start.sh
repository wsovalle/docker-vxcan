#!/bin/bash

set -euxo pipefail

docker network create --driver vxcan vx_can_bus
docker run -it --detach --name mfd2 vxcan_demo cat
docker run -it --detach --name mfd1 vxcan_demo cat
docker network connect vx_can_bus mfd1
docker network connect vx_can_bus mfd2

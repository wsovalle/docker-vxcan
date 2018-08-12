#!/bin/bash

set -euxo pipefail

docker network disconnect vx_can_bus mfd2 || :
docker kill mfd2 || :
docker rm mfd2 || :
docker network disconnect vx_can_bus mfd1 || :
docker kill mfd1 || :
docker rm mfd1 || :
docker network remove vx_can_bus || :

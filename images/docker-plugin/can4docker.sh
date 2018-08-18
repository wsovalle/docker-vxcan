#!/bin/sh

set -eu

gunicorn -b unix:/run/docker/plugins/can4docker.sock can4docker.driver:APPLICATION

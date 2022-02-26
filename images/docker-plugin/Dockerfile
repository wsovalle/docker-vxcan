# Current image size: 133MB
# Size reduction:
# - The important terminfo files are installed by ncurses-terminfo-base into
#   /etc/terminfo.  The ncurses-terminfo package creates symlinks to those
#   files in /usr/share/terminfo.  Everything else that ncurses-terminfo
#   installs in /usr/share/terminfo is a regular file we don't care about.
#   ref: https://raw.githubusercontent.com/nbgallery/jupyter-alpine/6117cd010be2c2862cf11cc41406bbfc9b97dff9/util/clean-terminfo
#   => 6+ MB
# - /root/.cache => 2 MB
# - pyc/pyo => 3 MB
# - python:3.5 is 917MB ?!?, python:3.5-alpine is 75.3 MB
# - Moving to python:3.9.10-alpine and updated dependencies grew image

FROM python:3.9.10-alpine

# Install base dependencies
RUN set -ex; \
  apk update; \
  apk upgrade; \
  apk add --no-cache can-utils

# # Update PIP
RUN set -ex; \
  python -m pip --no-cache-dir install --upgrade pip gunicorn

# Copy over the necessary files
ADD dist/can4docker-*.whl \
  images/docker-plugin/can4docker.sh \
  images/docker-plugin/pyroute2-0000-fix-vxcan-peer.patch \
  /

# Install application and dependencies
RUN set -ex; \
  pip --no-cache-dir install can4docker-*.whl

# Patch pyroute2
RUN set -ex; \
  apk add --no-cache patch && \
  (cd /usr/local/lib/python3.9/site-packages/pr2modules && \
  patch -p2 </pyroute2-0000-fix-vxcan-peer.patch)

# Cleanup
RUN set -ex; \
  apk del patch && \
  rm -f can4docker-*.whl && \
  rm -f pyroute2-*.patch && \
  rm -Rf /root/.cache /var/cache/apk/* && \
  find /usr/local/lib \( -name '*.pyc' -o -name '*.pyo' \) -delete

CMD ["can4docker.sh"]

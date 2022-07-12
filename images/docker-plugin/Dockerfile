# Current image size: 79.9MB
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

FROM python:3.9.13-alpine

WORKDIR /

COPY dist/can4docker-*.whl \
    images/docker-plugin/can4docker.sh \
    images/docker-plugin/pyroute2-0000-fix-vxcan-peer.patch \
    /

RUN apk add --no-cache can-utils && \
    python -m pip install --upgrade pip gunicorn && \
    \
    pip install gunicorn can4docker-*.whl && \
    \
    (cd /usr/local/lib/python3.9/site-packages/pr2modules && \
      patch -p2 </pyroute2-0000-fix-vxcan-peer.patch) && \
    \
    rm -f can4docker-*.whl && \
    rm -Rf /root/.cache /var/cache/apk/* && \
    find /usr/local/lib \( -name '*.pyc' -o -name '*.pyo' \) -delete

CMD ["can4docker.sh"]

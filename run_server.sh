#!/usr/bin/env sh

SOURCE_DIR=flaskapp
export FLASK_APP="$(pwd)/$SOURCE_DIR/wsgi.py"
export FLASK_SETTINGS="$(pwd)/server.cfg"

flask "$@"

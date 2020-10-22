#!/usr/bin/env bash
set -eu

source venv/bin/activate
pip install -r requirements.txt

sudo uwsgi --uid 33 --gid 33 --ini edufinder_uwsgi.ini
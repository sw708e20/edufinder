#!/usr/bin/env bash
set -eu

source venv/bin/activate
pip install -r requirements.txt

sudo uwsgi --reload /tmp/project-master.pid
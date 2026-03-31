#!/bin/bash
export PYTHONPATH="/usr/share/fedora-app-store/src:$PYTHONPATH"
python3 /usr/share/fedora-app-store/src/main.py "$@"

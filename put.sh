#!/bin/sh
PORT=/dev/ttyUSB0

# filter directories, and create relevant ones on board
find . -mindepth 1 -type d | grep -v -E "(.(git|idea|vscode)|__pycache__)" | xargs -n1 ampy --port ${PORT} mkdir
# put medea files
find medea -name '*.py' | grep -v auth.py | xargs -n1 -I {} ampy --port ${PORT} put {} {}
# put script example files
find examples -name '*.py' | xargs -n1 -I {} ampy --port ${PORT} put {} {}
# put script data files
find examples -name '*.json' | xargs -n1 -I {} ampy --port ${PORT} put {} {}


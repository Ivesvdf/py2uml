#!/usr/bin/env bash

../../py2uml.py --names-only *.py | dot -T png -o output.png

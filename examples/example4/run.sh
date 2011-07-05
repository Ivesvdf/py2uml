#!/usr/bin/env bash

../../py2uml.py --max-methods=2 *.py | dot -T png -o output.png

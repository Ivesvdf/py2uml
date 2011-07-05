#!/usr/bin/env bash

../../py2uml.py *.py | dot -T png -o output.png

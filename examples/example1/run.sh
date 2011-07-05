#!/usr/bin/env bash

../../py2uml.py animals.py | dot -T png -o output.png

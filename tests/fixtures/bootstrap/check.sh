#!/usr/bin/env bash
python3 -B -m unittest discover -s checks -v
printf 'Checks finished.\n'

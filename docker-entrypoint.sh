#!/bin/sh

gunicorn --chdir app app:app --timeout 150 -w 2 --threads 2 -b "${HOST}:${PORT}"

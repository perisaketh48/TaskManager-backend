#!/usr/bin/env bash
# .render-build.sh

python manage.py collectstatic --noinput
python manage.py migrate
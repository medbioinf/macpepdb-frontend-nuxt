#!/bin/sh

echo "startet with ${@}"

# Prepend 'python ./run.py' arguments given by 'CMD' (dockerfile) or 'command' (docker-compose)
set -- python ./run.py "$@"
exec "$@"
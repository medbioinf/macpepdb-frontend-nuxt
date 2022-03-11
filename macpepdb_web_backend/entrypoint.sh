#!/bin/sh

echo "startet with ${@}"

# Prepend 'python -m macpepdb_web_backend' arguments given by 'CMD' (dockerfile) or 'command' (docker-compose)
set -- python -m macpepdb_web_backend "$@"
exec "$@"
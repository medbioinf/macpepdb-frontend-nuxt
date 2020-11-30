#!/bin/sh

echo "startet with ${@}"

if [ "$RUN_MIGRATIONS" = "true" ]
then
    alembic upgrade head
fi

# Prepend 'python ./run.py' arguments given by 'CMD' (dockerfile) or 'command' (docker-compose)
set -- python ./run.py "$@"
exec "$@"
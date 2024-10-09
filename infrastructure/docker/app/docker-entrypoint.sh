#!/bin/sh
set -e

echo "$@";

if [ $1 = "todoapp" ];
then
    exec /var/app/todoapp "$@";
fi

exec "$@"

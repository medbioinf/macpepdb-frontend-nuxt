#!/bin/sh

# Write settings to file
echo "MACPEPDB_BACKEND_BASE_URL=$MACPEPDB_BACKEND_BASE_URL" > current_settings.env
echo "MACPEPDB_FRONTEND_INTERFACE=$MACPEPDB_FRONTEND_INTERFACE" >> current_settings.env
echo "MACPEPDB_FRONTEND_PORT=$MACPEPDB_FRONTEND_PORT" >> current_settings.env

# Check if there is an file with old settings if not create an empty one
if [ ! -f last_settings.env ]
then
    echo "NO OLD SETTINGS"
    echo "" > last_settings.env
fi

# Read both files
current_settings=$(cat current_settings.env)
last_settings=$(cat last_settings.env)

# If old and current settings differ rebuild app
if [ "$last_settings" != "$current_settings" ]
then
    echo "(RE)BUILD"
    # (Re-)Build application and apply new settings
    yarn build
    cp current_settings.env last_settings.env
fi


# Start application
yarn start
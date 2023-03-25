#!/usr/bin/env bash
app="/home/wumbl3vps/Dev-23/discord-bot"
cd $app
source venv/bin/activate

# if secret file doesn't exist, create it with a 24 byte random string
if [ ! -f $app/environment_vars/secret_key ]; then
    dd if=/dev/urandom bs=24 count=1 2>/dev/null | base64 >$app/environment_vars/secret_key
fi

# set secret environment variable to secret_key file contents
export SECRET=$(cat $app/environment_vars/secret_key)

export DISCORD_TOKEN=$(cat $app/environment_vars/discord_token)

gunicorn --error-logfile "${app}/logging/gunicorn-error.log" -w 1 --bind unix:"${app}/server/sock.sock" -m 007 main:app

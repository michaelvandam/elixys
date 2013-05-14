#!/bin/bash

if [ "$(whoami)" != "root" ]; then
	echo "Elixys server install require root priveleges"
	exit 1
fi
source elixys_paths.sh
# Grab the source


touch /opt/elixys/demomode

cd $ELIXYS_SRC/server/config

python ImportDatabase.py demodata

service mysql restart
service apache2 restart
service ElixysFakePLC restart
service ElixysCoreServer restart
service ElixysValidation restart
#service ElixysRtmpd restart

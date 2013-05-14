#!/bin/bash

if [ "$(whoami)" != "root" ]; then
	echo "Elixys server install require root priveleges"
	exit 1
fi
source elixys_paths.sh
# Grab the source

if [ -d $ELIXYS_SRC ] 
then
# Git pull most up-to-date code
	echo "Update the Elixys repo"
	cd $ELIXYS_SRC
	git remote update
	git pull origin
else
	# Git Clone the Repo
	echo "Clone the Elixys Repo"
	git clone --depth 1 -b deb-install $ELIXYS_REPO $ELIXYS_SRC
	cd $ELIXYS_SRC
fi

# Update the static web content
rm -rf /var/www/http/*
cp -Rf $ELIXYS_SRC/server/web/http/* /var/www/http/

# Update the web server
rm -rf /var/www/wsgi/*
cp -Rf $ELIXYS_SRC/server/web/wsgi/* /var/www/wsgi

# Update the core server
rm -rf $ELIXYS_INSTALL_PATH/cli
rm -rf $ELIXYS_INSTALL_PATH/core
rm -rf $ELIXYS_INSTALL_PATH/hardware
rm -rf $ELIXYS_INSTALL_PATH/database
cp -R $ELIXYS_SRC/server/cli $ELIXYS_INSTALL_PATH 
cp -R $ELIXYS_SRC/server/core $ELIXYS_INSTALL_PATH
cp -R $ELIXYS_SRC/server/hardware $ELIXYS_INSTALL_PATH
cp -R $ELIXYS_SRC/server/database $ELIXYS_INSTALL_PATH

cp -R $ELIXYS_SRC/server/config/init.d/ElixysCoreServer /etc/init.d/
cp -R $ELIXYS_SRC/server/config/init.d/ElixysFakePLC /etc/init.d/
cp -R $ELIXYS_SRC/server/config/init.d/ElixysRtmpd /etc/init.d/
cp -R $ELIXYS_SRC/server/config/init.d/ElixysValidation /etc/init.d/

chmod 755 /etc/init.d/ElixysCoreServer
chmod 755 /etc/init.d/ElixysValidation
chmod 755 /etc/init.d/ElixysFakePLC
chmod 755 /etc/init.d/ElixysRtmpd


update-rc.d ElixysFakePLC defaults 90
update-rc.d ElixysCoreServer defaults 91
update-rc.d ElixysValidation defaults 91
#update-rc.d ElixysRtmpd defaults 92
update-rc.d apache2 defaults

service mysql restart
service apache2 restart
service ElixysFakePLC restart
service ElixysCoreServer restart
service ElixysValidation restart
#service ElixysRtmpd restart

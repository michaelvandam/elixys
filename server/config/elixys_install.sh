#!/bin/bash

if [ "$(whoami)" != "root" ]; then
	echo "Elixys server install require root priveleges"
	exit 1
fi

# Global Paths and Variable
export ELIXYS_SRC=/usr/local/src/elixys
export ELIXYS_REPO=https://github.com/henryeherman/elixys.git
export ELIXYS_INSTALL_PATH=/opt/elixys
export ELIXYS_CONFIG_PATH=$ELIXYS_INSTALL_PATH/config
export ELIXYS_LOG_PATH=$ELIXYS_INSTALL_PATH/log
export ELIXYS_RTMPD_PATH=$ELIXYS_INSTALL_PATH/rtmpd
# Remove old src
rm -Rf $ELIXYS_SRC
# Remove old configs
rm -Rf $ELIXYS_INSTALL_PATH/*

# Grab the source
if [ -d $ELIXYS_SRC ] 
then
# Git pull most up-to-date code
	echo "Update the Elixys repo"
	cd $ELIXYS_SRC
	git remote update
else
	# Git Clone the Repo
	echo "Clone the Elixys Repo"
	git clone --depth 1 -b deb-install $ELIXYS_REPO $ELIXYS_SRC
	cd $ELIXYS_SRC
fi

# Create the Elixys Install Directory
mkdir -p $ELIXYS_INSTALL_PATH
mkdir -p $ELIXYS_LOG_PATH
mkdir -p $ELIXYS_CONFIG_PATH

# Copy the default configuration and setup scripts
cp -R server/config/* $ELIXYS_CONFIG_PATH 
cd $ELIXYS_CONFIG_PATH

# Make the setup scripts executable
chmod u+x *.sh

# Initialize Apache directory tree
rm -rf /var/www/*
mkdir -p /var/www/adobepolicyfile
mkdir -p /var/www/http
mkdir -p /var/www/wsgi

# Copy Adobe Policy XML
cp $ELIXYS_SRC/server/config/adobepolicyfile/crossdomain.xml \
	/var/www/adobepolicyfile
chmod 444 /var/www/adobepolicyfile/crossdomain.xml

# Install mysql config
if [ -f /etc/mysql/my.cnf ]; then
	mv /etc/mysql/my.cnf /etc/mysql/my.cnf.bkup
fi
cp my.cnf /etc/mysql/
service mysql restart
./InitializeDatabase.sh

# Copy over the crtmp server scripts
#cp $ELIXYS_SRC/server/rtmpd/* $ELIXYS_RTMPD_PATH



#!/bin/bash

if [ "$(whoami)" != "root" ]; then
	echo "Elixys server install require root priveleges"
	exit 1
fi
./elixys_install_deps.sh
source elixys_paths.sh

# Remove old src
#rm -Rf $ELIXYS_SRC
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
mkdir -p $ELIXYS_RTMPD_PATH

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

./elixys_install_database.sh

# Copy over the crtmp server scripts
cp $ELIXYS_SRC/server/rtmpd/*.lua $ELIXYS_RTMPD_PATH
cp $ELIXYS_SRC/server/rtmpd/*.py $ELIXYS_RTMPD_PATH
mkdir -p $ELIXYS_RTMPD_PATH/media
cp -R $ELIXYS_SRC/server/rtmpd/applications/flvplayback/media/* $ELIXYS_RTMPD_PATH/media



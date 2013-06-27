#!/bin/bash

if [ "$(whoami)" != "root" ]; then
	echo "Elixys server install require root priveleges"
	exit 1
fi

#./elixys_install_deps.sh
if [ ! -f elixys_paths.sh ];
then
	echo "elixys_paths.sh does not exist"
	exit 1
fi

source elixys_paths.sh

SCRIPTPATH=`realpath $0`
ELIXYS_SRC=`dirname $SCRIPTPATH`/../..

echo "Installing from $ELIXYS_SRC"

# Create the Elixys Install Directory
mkdir -p $ELIXYS_INSTALL_PATH
rm -rf $ELIXYS_INSTALL_PATH/*
mkdir -p $ELIXYS_LOG_PATH

# Link the default configuration and setup scripts
ln -sf  $ELIXYS_SRC/server/config $ELIXYS_INSTALL_PATH

# Link core
ln -sf  $ELIXYS_SRC/server/core $ELIXYS_INSTALL_PATH

# Link database
ln -sf  $ELIXYS_SRC/server/database $ELIXYS_INSTALL_PATH

# Link cli
ln -sf  $ELIXYS_SRC/server/cli $ELIXYS_INSTALL_PATH

# Link hardware
ln -sf $ELIXYS_SRC/server/hardware $ELIXYS_INSTALL_PATH

# Initialize Apache directory tree
rm -rf /var/www/*
mkdir -p /var/www/adobepolicyfile

# Link wsgi
ln -sf $ELIXYS_SRC/server/web/wsgi /var/www

# Link html
ln -sf $ELIXYS_SRC/server/web/http /var/www


# Copy Adobe Policy XML
mkdir -p /var/www/adobepolicyfile
cp -f $ELIXYS_SRC/server/config/adobepolicyfile/crossdomain.xml \
	/var/www/adobepolicyfile
chmod 444 /var/www/adobepolicyfile/crossdomain.xml

#cd $ELIXYS_CONFIG_PATH
#./elixys_install_database.sh

# Copy over the Apache config
ln -sf $ELIXYS_SRC/server/config/elixys-web /etc/apache2/sites-available
a2dissite default
a2ensite elixys-web

#Install Services
cp -R $ELIXYS_SRC/server/config/init.d/ElixysCoreServer /etc/init.d/
cp -R $ELIXYS_SRC/server/config/init.d/ElixysFakePLC /etc/init.d/
cp -R $ELIXYS_SRC/server/config/init.d/ElixysValidation /etc/init.d/

chmod 755 /etc/init.d/ElixysCoreServer
chmod 755 /etc/init.d/ElixysValidation
chmod 755 /etc/init.d/ElixysFakePLC

update-rc.d ElixysFakePLC defaults 90
update-rc.d ElixysCoreServer defaults 91
update-rc.d ElixysValidation defaults 91
update-rc.d apache2 defaults

service mysql restart
service apache2 restart
service ElixysFakePLC restart
service ElixysCoreServer restart
service ElixysValidation restart
#./elixys_setup_demo.sh

chgrp sofiebio $ELIXYS_LOG_PATH
usermod -a -G sofiebio www-data
chmod 664 $ELIXYS_LOG_PATH/*


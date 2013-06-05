#!/bin/bash

if [ "$(whoami)" != "root" ]; then
	echo "Elixys server install require root priveleges"
	exit 1
fi

# Global Paths and Variable
cd ../..
export ELIXYS_SRC=`/usr/bin/env pwd`
export ELIXYS_INSTALL_PATH=/opt/elixys
export ELIXYS_CONFIG_PATH=$ELIXYS_INSTALL_PATH/config
export ELIXYS_LOG_PATH=$ELIXYS_INSTALL_PATH/logs
export ELIXYS_RTMPD_PATH=$ELIXYS_INSTALL_PATH/rtmpd


# Create the Elixys Install Directory
mkdir -p $ELIXYS_INSTALL_PATH
mkdir -p $ELIXYS_LOG_PATH
mkdir -p $ELIXYS_CONFIG_PATH
mkdir -p $ELIXYS_RTMPD_PATH

# Setup Logs
touch $ELIXYS_LOG_PATH/elixysweb.log
touch $ELIXYS_LOG_PATH/elixyscore.log
touch $ELIXYS_LOG_PATH/elixysvalid.log
touch $ELIXYS_LOG_PATH/elixys.log
touch $ELIXYS_LOG_PATH/elixyshw.log

chmod 777 $ELIXYS_LOG_PATH/elixysweb.log
chmod 777 $ELIXYS_LOG_PATH/elixyscore.log
chmod 777 $ELIXYS_LOG_PATH/elixysvalid.log
chmod 777 $ELIXYS_LOG_PATH/elixys.log
chmod 777 $ELIXYS_LOG_PATH/elixyshw.log

cd $ELIXYS_SRC

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

cd $ELIXYS_CONFIG_PATH
./elixys_install_database.sh

# Copy over the crtmp server scripts
cp $ELIXYS_SRC/server/rtmpd/*.lua $ELIXYS_RTMPD_PATH
cp $ELIXYS_SRC/server/rtmpd/*.py $ELIXYS_RTMPD_PATH
# Copy over the application directory and media
mkdir -p $ELIXYS_RTMPD_PATH/applications/flvplayback/media
cp -R $ELIXYS_SRC/server/rtmpd/applications/flvplayback/media/*  \
	$ELIXYS_RTMPD_PATH/applications/flvplayback/media

# Copy over the Apache config
cp $ELIXYS_SRC/server/config/elixys-web /etc/apache2/sites-available
a2dissite default
a2ensite elixys-web

cd $ELIXYS_CONFIG_PATH
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
rm -rf $ELIXYS_INSTALL_PATH/config
cp -R $ELIXYS_SRC/server/config $ELIXYS_INSTALL_PATH 
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
update-rc.d ElixysRtmpd defaults 92
update-rc.d apache2 defaults

service mysql restart
service apache2 restart
service ElixysFakePLC restart
service ElixysCoreServer restart
service ElixysValidation restart
service ElixysRtmpd restart
cd $ELIXYS_CONFIG_PATH
./elixys_setup_demo.sh

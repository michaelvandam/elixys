#!/bin/bash

if [ "$(whoami)" != "root" ]; then
	echo "Elixys server install require root priveleges"
	exit 1
fi

#Install Elixys Dependencies
apt-get update
export DEBIAN_FRONTEND=noninteractive
apt-get -q -y install python python-mysqldb python-mysql.connector \
		 python-configobj python-setuptools python-pip \
		 ipython ipython-notebook-common ipython-qtconsole
pip install rpyc
pip install twilio
apt-get -q -y install vim git-core binutils
apt-get -q -y install autojump
echo "source /usr/share/autojump/autojump.bash" >> ~/.bashrc
apt-get -q -y install mysql-common mysql-server
apt-get -q -y install apache2 apache2-utils \
			libapache2-mod-wsgi apache2-threaded-dev \
			libapache2-mod-auth-mysql \
			libaprutil1-dbd-mysql 
			# \ apache2-prefork-dev

sudo apt-get -q -y install crtmpserver

export ADOBE_POL_PATH_SRC=/usr/local/src/mod_adobe_crossdomainpolicy
rm -Rf $ADOBE_POL_PATH_SRC
mkdir -p $ADOBE_POL_PATH_SRC
cd $ADOBE_POL_PATH_SRC
wget http://www.beamartyr.net/projects/mod_adobe_crossdomainpolicy.c
apxs2 -cia mod_adobe_crossdomainpolicy.c

a2enmod adobe_crossdomainpolicy
a2enmod wsgi
a2enmod authn_dbd
a2enmod authz_host
a2enmod authz_user
a2enmod rewrite
a2enmod auth_mysql

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
	git pull
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

cd $ELIXYS_CONFIG_PATH/deb_install
./elixys_install_database.sh

# Copy over the crtmp server scripts
cp $ELIXYS_SRC/server/rtmpd/*.lua $ELIXYS_RTMPD_PATH
cp $ELIXYS_SRC/server/rtmpd/*.py $ELIXYS_RTMPD_PATH
mkdir -p $ELIXYS_RTMPD_PATH/media
cp -R $ELIXYS_SRC/server/rtmpd/applications/flvplayback/media/* $ELIXYS_RTMPD_PATH/media

# Copy over the Apache config
cp $ELIXYS_SRC/server/config/elixys-web /etc/apache2/sites-available
a2dissite default
a2ensite elixys-web

cd $ELIXYS_CONFIG_PATH/deb_install
./elixys_update.sh
cd $ELIXYS_CONFIG_PATH/deb_install
./elixys_setup_demo.sh

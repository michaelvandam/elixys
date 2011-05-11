#!/bin/sh

### This script updates an Elixys production server with the latest system from source control ###

# Make sure we're running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root."
   exit 1
fi

# Get the current git repository
git clone --depth 1 git://github.com/michaelvandam/elixys.git

# Update the Apache configuration file
mv -f elixys/config/httpd.conf /etc/httpd/conf
chcon --user=system_u --role=object_r --type=httpd_config_t -R /etc/httpd/conf/httpd.conf

# Update the static web content
rm -rf /var/www/https/*
mv -f elixys/bin/WebContent/* /var/www/https/
chcon --user=user_u --role=object_r --type=httpd_sys_content_t -R /var/www/https/*

# Update the current dummy server
mv -f elixys/server/DummyServer.py /var/www/wsgi
chcon --user=user_u --role=object_r --type=httpd_sys_content_t -R /var/www/wsgi/*

# Restart Apache
/usr/sbin/apachectl restart

# Remove the git repository
rm -rf elixys


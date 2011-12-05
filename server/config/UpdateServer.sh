#!/bin/sh

### This script updates an Elixys production server with the latest system from source control ###

# Make sure we're running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root."
   exit 1
fi

# Get the current git repository
git clone --depth 1 http://github.com/michaelvandam/elixys.git

# Update the Apache configuration file
mv -f elixys/server/config/httpd.conf /etc/httpd/conf
chcon --user=system_u --role=object_r --type=httpd_config_t -R /etc/httpd/conf/httpd.conf

# Update the static web content
rm -rf /var/www/http/*
mv -f elixys/bin/WebContent/* /var/www/http/
chcon --user=user_u --role=object_r --type=httpd_sys_content_t -R /var/www/http/*

# Update the web server
rm -rf /var/www/wsgi/*
mv -f elixys/server/web/* /var/www/wsgi
chcon --user=user_u --role=object_r --type=httpd_sys_content_t -R /var/www/wsgi/*

# Restart Apache
service httpd restart

# Update the core server
rm -rf /opt/elixys/cli
rm -rf /opt/elixys/core
rm -rf /opt/elixys/hardware
rm -rf /opt/elixys/database
cp -R elixys/server/cli /opt/elixys
cp -R elixys/server/core /opt/elixys
cp -R elixys/server/hardware /opt/elixys
cp -R elixys/server/database /opt/elixys

# Remove the git repository
rm -rf elixys


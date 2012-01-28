#!/bin/sh

### This script updates an Elixys production server with the latest system from source control ###

# Make sure we're running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root."
   exit 1
fi

# Stop the services
service ElixysCoreServer stop
service ElixysFakePLC stop
service httpd stop

# Get the current git repository
git clone --depth 1 http://github.com/michaelvandam/elixys.git

# Update the static web content
rm -rf /var/www/http/*
mv -f elixys/server/web/http/* /var/www/http/
restorecon /var/www/http/*
#chcon --user=user_u --role=object_r --type=httpd_sys_content_t -R /var/www/http/*

# Update the web server
rm -rf /var/www/wsgi/*
mv -f elixys/server/web/wsgi/* /var/www/wsgi
restorecon /var/www/wsgi/*
#chcon --user=user_u --role=object_r --type=httpd_sys_content_t -R /var/www/wsgi/*

# Update the core server
rm -rf /opt/elixys/cli
rm -rf /opt/elixys/core
rm -rf /opt/elixys/hardware
rm -rf /opt/elixys/database
cp -R elixys/server/cli /opt/elixys
cp -R elixys/server/core /opt/elixys
cp -R elixys/server/hardware /opt/elixys
cp -R elixys/server/database /opt/elixys

# Start the services
service httpd start
service ElixysFakePLC start
service ElixysCoreServer start

# Remove the git repository
rm -rf elixys


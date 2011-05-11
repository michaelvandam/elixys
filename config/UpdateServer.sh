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
#mv -f elixys/bin/Web\ Server\ Content/* /var/www/html/

# Update the static web content
rm -rf /var/www/https/*
mv -f elixys/bin/Web\ Server\ Content/* /var/www/html/
chcon --user=user_u --role=object_r --type=httpd_sys_content_t -R /var/www/html/*

# Restart Apache
/usr/sbin/apachectl restart

# Remove the git repository
rm -rf elixys

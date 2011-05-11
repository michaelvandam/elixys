#!/bin/sh

### This script turns a fresh CentOS installation into an Elixys production server ###

# Make sure we're running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root."
   exit 1
fi

# Start in the home directory
cd ~

# Install git from the EPEL repository
wget http://download.fedoraproject.org/pub/epel/5/i386/epel-release-5-4.noarch.rpm
rpm -Uhv epel-release-5-4.noarch.rpm
rm -f epel-release-5-4.noarch.rpm
yum -y install git

# Get the current git repository
git clone --depth 1 git://github.com/michaelvandam/elixys.git

# Install and configure MySQL
yum -y install mysql mysql-server apr-util-mysql
/sbin/service mysqld start
mysql -e "CREATE DATABASE Elixys;"
mysql -e "GRANT USAGE ON *.* TO Apache@localhost IDENTIFIED BY 'devel';"
mysql -e "GRANT ALL PRIVILEGES ON Elixys.* TO Apache@localhost;"
mysql Elixys < CreateDatabase.sql

# Install Apache and Python WSGI
yum -y install mod_wsgi python-wgsiref

# Set Apache and MySQL to start at boot
echo "/usr/sbin/apachectl start" >> /etc/rc.local
echo "/sbin/service mysqld start" >> /etc/rc.local

# Generate the CA key and certificate
mkdir /root/CA
chmod 770 /root/CA
cd /root/CA
openssl genrsa -des3 -out ElixysCA.key -passout pass:elixys 2048
openssl req -new -x509 -days 3650 -key ElixysCA.key -out ElixysCA.crt -passin pass:elixys -config ~/elixys/config/openssl.conf

# Generate the server key and certificate
openssl genrsa -des3 -out Elixys.key -passout pass:elixys 1024
openssl req -new -key Elixys.key -out Elixys.csr -passin pass:elixys -config ~/elixys/config/openssl.conf
openssl x509 -req -in Elixys.csr -out Elixys.crt -sha1 -CA ElixysCA.crt -CAkey ElixysCA.key -CAcreateserial -days 3650 -passin pass:elixys
chmod 400 *.key

# Copy the keys and certificates to the appropriate directory
mkdir /etc/httpd/conf/ssl.crt
mkdir /etc/httpd/conf/ssl.key
cp Elixys.key /etc/httpd/conf/ssl.key/Elixys.key.orig
cp Elixys.crt /etc/httpd/conf/ssl.crt
cp ElixysCA.crt /etc/httpd/conf/ssl.crt

# Remove the Apache startup TLS password
openssl rsa -in /etc/httpd/conf/ssl.key/Elixys.key.orig -out /etc/httpd/conf/ssl.key/Elixys.key -passin pass:elixys
chmod 400 /etc/httpd/conf/ssl.key/Elixys.key

# Remove the default SSH config
mv /etc/httpd/conf.d/ssh.conf /etc/httpd/conf.d/ssh.conf.unused

# Initialize Apache directory tree
rm -rf /var/www/*
mkdir /var/www/http
mkdir /var/www/https
mkdir /var/www/wsgi

# Remove the git repository
rm -rf elixys

# Do the initial pull from source control
./UpdateServer.sh

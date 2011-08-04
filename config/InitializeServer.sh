#!/bin/sh

### This script turns a fresh CentOS installation into an Elixys production server ###

# Make sure we're running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root."
   exit 1
fi

# Start in the root directory
cd /root

# Install git from the EPEL repository
wget http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-5.noarch.rpm
rpm -Uhv epel-release-6-5.noarch.rpm
rm -f epel-release-6-5.noarch.rpm
yum -y install git

# Get the current git repository
git clone --depth 1 http://github.com/michaelvandam/elixys.git

# Install and configure MySQL
yum -y install mysql mysql-server apr-util-mysql
/sbin/service mysqld start
mysql -e "CREATE DATABASE Elixys;"
mysql -e "GRANT USAGE ON *.* TO Apache@localhost IDENTIFIED BY 'devel';"
mysql -e "GRANT ALL PRIVILEGES ON Elixys.* TO Apache@localhost;"
mysql Elixys < elixys/config/CreateDatabase.sql

# Install mod_wsgi
yum -y install mod_wsgi

# Install configobj
wget http://www.voidspace.org.uk/downloads/configobj-4.7.2.zip
unzip configobj-4.7.2.zip
cd configobj-4.7.2
python setup.py install
cd ..
rm -rf configobj-4.7.2*

# Set Apache and MySQL to start at boot - Use upstart
#echo "/usr/sbin/apachectl start" >> /etc/rc.local
#echo "/sbin/service mysqld start" >> /etc/rc.local

# Initialize Apache directory tree
rm -rf /var/www/*
mkdir /var/www/adobepolicyfile
mkdir /var/www/http
mkdir /var/www/wsgi

# Install the Adobe policy module and file
cp elixys/config/adobepolicyfile/mod_adobe_crossdomainpolicy.so /usr/lib64/httpd/modules/
chmod 755 /usr/lib64/httpd/modules/mod_adobe_crossdomainpolicy.so
cp elixys/config/adobepolicyfile/crossdomain.xml /var/www/adobepolicyfile
chmod 444 /var/www/adobepolicyfile/crossdomain.xml

# Allow Apache to save the server state to files in the WSGI directory.  This is temporary and will go away once we get the
# WSGI interface integrated with MySQL
chmod 777 /var/www/wsgi
chown apache:apache /var/www/wsgi

# Update the firewall settings
mv -f elixys/config/iptables /etc/sysconfig/
chcon --user=system_u --role=object_r --type=etc_t /etc/sysconfig/iptables

# Remove the git repository
rm -rf /root/elixys


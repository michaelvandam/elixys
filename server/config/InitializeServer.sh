#!/bin/sh

### This script turns a fresh CentOS installation into an Elixys production server ###

# Make sure we're running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root."
   exit 1
fi

# Start in the root directory
cd /root

# Install git and do a pull
yum -y install git
git clone --depth 1 http://github.com/michaelvandam/elixys.git

# Create the root application directory
mkdir /opt/elixys

# Make an application copy of the config directory
cp -R elixys/server/config /opt/elixys
cd /opt/elixys/config
chmod 755 *.sh

# Install, start and initialize MySQL
yum -y install mysql mysql-server apr-util-mysql
cp my.cnf /etc
restorecon /etc/my.cnf
/sbin/service mysqld start
./InitializeDatabase.sh
cd /root

# Make an application copy of the rtmpd directory
chmod 711 elixys/server/rtmpd/crtmpserver
cp -R elixys/server/rtmpd /opt/elixys

# Create the log directory
mkdir /opt/elixys/logs

# Install mod_wsgi
yum -y install mod_wsgi

# Install configobj for Python
mkdir configobj
unzip -d configobj elixys/server/config/packages/configobj-4.7.2.zip
cd configobj/configobj-4.7.2
python setup.py install
cd ../..
rm -rf configobj*

# Install RPyC for Python
unzip elixys/server/config/packages/RPyC-3.1.0.zip
cd RPyC-3.1.0
python setup.py install
cd ..
rm -rf RPyC-3.1.0*

# Install setuptools for Python
python elixys/server/config/packages/ez_setup.py

# Install MySQL for Python
yum -y install python-devel mysql-devel
tar -xf elixys/server/config/packages/MySQL-python-1.2.3.tar.gz
cd MySQL-python-1.2.3
python setup.py build
python setup.py install
cd ..
rm -rf MySQL-python-1.2.3*

# Install Twilio for Python
git clone --depth=1 https://github.com/twilio/twilio-python.git
cd twilio-python
python setup.py install
cd ..
rm -rf twilio-python

# Add the services scripts
cp elixys/server/config/init.d/ElixysCoreServer /etc/init.d
cp elixys/server/config/init.d/ElixysFakePLC /etc/init.d
cp elixys/server/config/init.d/ElixysRtmpd /etc/init.d
cp elixys/server/config/init.d/ElixysValidation /etc/init.d
chcon --user=system_u --role=object_r --type=initrc_exec_t /etc/init.d/ElixysCoreServer
chcon --user=system_u --role=object_r --type=initrc_exec_t /etc/init.d/ElixysFakePLC
chcon --user=system_u --role=object_r --type=initrc_exec_t /etc/init.d/ElixysRtmpd
chcon --user=system_u --role=object_r --type=initrc_exec_t /etc/init.d/ElixysValidation
chmod 755 /etc/init.d/ElixysCoreServer
chmod 755 /etc/init.d/ElixysFakePLC
chmod 755 /etc/init.d/ElixysRtmpd
chmod 755 /etc/init.d/ElixysValidation
chkconfig --add ElixysCoreServer
chkconfig --add ElixysFakePLC
chkconfig --add ElixysRtmpd
chkconfig --add ElixysValidation

# Set the services to start at boot
echo "service httpd start" >> /etc/rc.local
echo "service mysqld start" >> /etc/rc.local
echo "service ElixysCoreServer start" >> /etc/rc.local
echo "service ElixysFakePLC start" >> /etc/rc.local
echo "service ElixysRtmpd start" >> /etc/rc.local
echo "service ElixysValidation start" >> /etc/rc.local

# Initialize Apache directory tree
rm -rf /var/www/*
mkdir /var/www/adobepolicyfile
mkdir /var/www/http
mkdir /var/www/wsgi

# Install the Apache configuration file
mv -f elixys/server/config/httpd.conf /etc/httpd/conf
restorecon /etc/httpd/conf/httpd.conf

# Create a directory where Apache has write permissions for Python Eggs 
mkdir /var/www/eggs
chmod 777 /var/www/eggs
chown apache:apache /var/www/eggs

# Install SELinux management tools and define the RPC port
yum -y install policycoreutils-python
semanage port -a -t http_port_t -p tcp 18862

# Install the Adobe policy module and file
cp elixys/server/config/adobepolicyfile/mod_adobe_crossdomainpolicy.so /usr/lib64/httpd/modules/
chmod 755 /usr/lib64/httpd/modules/mod_adobe_crossdomainpolicy.so
cp elixys/server/config/adobepolicyfile/crossdomain.xml /var/www/adobepolicyfile
chmod 444 /var/www/adobepolicyfile/crossdomain.xml

# Update the firewall settings
mv -f elixys/server/config/iptables /etc/sysconfig/
restorecon /etc/sysconfig/iptables
/sbin/service iptables restart

# Put shortcuts on the user's desktop
chmod 755 elixys/server/config/shortcuts/*.sh
cp elixys/server/config/shortcuts/* /home/$USER/Desktop

# Give all users the ability to run the update script as root
echo "ALL ALL=(ALL) NOPASSWD:/opt/elixys/config/UpdateServer.sh" >> /etc/sudoers

# Remove the git repository
rm -rf /root/elixys

# Restore SELinux permissions
restorecon -R /opt/elixys

# Run the update script to perform the initial pull of the source code
cd /home/$USER/Desktop
./UpdateServer.sh


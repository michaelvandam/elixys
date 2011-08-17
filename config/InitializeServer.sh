#!/bin/sh

### This script turns a fresh CentOS installation into an Elixys production server ###

# Make sure we're running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root."
   exit 1
fi

# The following lines shouldn't be necessary but they are.  Something strange is going on with the networking in my VMs and disabling IPv6
# is a quick fix.  Hopefully it can be removed at some point in the future.  All of the "-4" arguments on the following wget commands are part
# of this hack and should be remove in the future as well
if lsmod | grep ipv6 > /dev/null
then
   echo "Disabling IPv6..."
   /sbin/service ip6tables stop
   /sbin/chkconfig ip6tables off
   echo "install ipv6 /bin/true" > /etc/modprobe.d/blacklist-ipv6.conf
   echo "blacklist ipv6" >> /etc/modprobe.d/blacklist-ipv6.conf
   echo "NETWORKING_IPV6=no" >> /etc/sysconfig/network
   echo "Done.  Press any key to reboot the computer and then run this script again"
   read CONTINUE
   shutdown -r now
fi

# Start in the root directory
cd /root

# Install git and do a pull
yum -y install git
git clone --depth 1 http://github.com/michaelvandam/elixys.git

# Install and configure MySQL
yum -y install mysql mysql-server apr-util-mysql
/sbin/service mysqld start
mysql -e "CREATE DATABASE Elixys;"
mysql -e "GRANT USAGE ON *.* TO Apache@localhost IDENTIFIED BY 'Apache';"
mysql -e "GRANT ALL PRIVILEGES ON Elixys.* TO Apache@localhost;"
mysql -e "GRANT USAGE ON *.* TO Elixys@localhost IDENTIFIED BY 'Elixys';"
mysql -e "GRANT ALL PRIVILEGES ON Elixys.* TO Elixys@localhost;"
mysql Elixys < elixys/config/DatabaseTables.sql
mysql Elixys < elixys/config/DatabaseProcedures.sql
mkdir /opt/elixys
cp -R elixys/server/database /opt/elixys

# Install mod_wsgi
yum -y install mod_wsgi

# Install configobj for Python
wget -4 http://www.voidspace.org.uk/downloads/configobj-4.7.2.zip
mkdir configobj
unzip -d configobj configobj-4.7.2.zip
cd configobj/configobj-4.7.2
python setup.py install
cd ../..
rm -rf configobj*

# Install RPyC for Python
wget -4 http://downloads.sourceforge.net/project/rpyc/main/3.1.0/RPyC-3.1.0.zip
unzip RPyC-3.1.0.zip
cd RPyC-3.1.0
python setup.py install
cd ..
rm -rf RPyC-3.1.0*

# Install setuptools for Python
wget -4 http://peak.telecommunity.com/dist/ez_setup.py
python ez_setup.py
rm -f ez_setup.py

# Install MySQL for Python
yum -y install python-devel mysql-devel
wget -4 http://sourceforge.net/projects/mysql-python/files/mysql-python/1.2.3/MySQL-python-1.2.3.tar.gz/download
tar -xf MySQL-python-1.2.3.tar.gz
cd MySQL-python-1.2.3
python setup.py build
python setup.py install
cd ..
rm -rf MySQL-python-1.2.3*

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
#chmod 777 /var/www/wsgi
#chown apache:apache /var/www/wsgi

# Update the firewall settings
mv -f elixys/config/iptables /etc/sysconfig/
chcon --user=system_u --role=object_r --type=etc_t /etc/sysconfig/iptables
/sbin/service iptables restart

# Install FFmpeg
#wget -4 http://packages.sw.be/rpmforge-release/rpmforge-release-0.5.2-2.el6.rf.x86_64.rpm
#rpm -Uhv rpmforge-release-0.5.2-2.el6.rf.x86_64.rpm
#rm -f rpmforge-release-0.5.2-2.el6.rf.x86_64.rpm
#yum -y install ffmpeg
#cp elixys/config/ffserver.conf /etc

# Install openRTSP
#cp -R elixys/bin/openRTSP /opt/elixys
#chmod +x /opt/elixys/openRTSP/openRTSP

# Put shortcuts on the user's desktop
mkdir /opt/elixys/config
cp elixys/config/UpdateServer.sh /opt/elixys/config
chmod 755 /opt/elixys/config/UpdateServer.sh
cp elixys/config/shortcuts/* /home/$USER/Desktop
chmod 755 /home/$USER/Desktop/ElixysCLI.sh
chmod 755 /home/$USER/Desktop/StateMonitor.sh
chmod 755 /home/$USER/Desktop/UpdateServer.sh

# Give all users the ability to run the update script as root
echo "ALL ALL=(ALL) NOPASSWD:/opt/elixys/config/UpdateServer.sh" >> /etc/sudoers

# Remove the git repository
rm -rf /root/elixys


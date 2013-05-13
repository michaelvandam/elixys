#!/bin/bash

### This script initializes the Elixys database ###



if [ "$(whoami)" != "root" ]; then
	echo "Elixys server DB install require root priveleges"
	exit 1
fi

source elixys_paths.sh 

cd $ELIXYS_CONFIG_PATH

# Install mysql config
if [ -f /etc/mysql/my.cnf ]; then
	mv /etc/mysql/my.cnf /etc/mysql/my.cnf.bkup
fi
cp my.cnf /etc/mysql/

# Create the database, tables and stored procedures
echo "Recreating database..."
mysql -e "DROP DATABASE IF EXISTS Elixys;"
mysql -e "CREATE DATABASE Elixys;"
mysql Elixys < SetDatabasePrivileges.sql
mysql Elixys < CreateDatabaseTables.sql
mysql Elixys < CreateDatabaseProcedures.sql

# Restart the database
echo "Restarting database..."
/sbin/service mysqld restart
echo "Done"


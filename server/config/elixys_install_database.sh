#!/bin/bash

### This script initializes the Elixys database ###



if [ "$(whoami)" != "root" ]; then
	echo "Elixys server DB install require root priveleges"
	exit 1
fi

source elixys_paths.sh 

cd $ELIXYS_CONFIG_PATH

service mysql stop
mysqld --skip-grant-tables &
SQLPID=$!
echo $SQLPID > mysql_nopw.pid
sleep 3
# Create the database, tables and stored procedures
echo "Recreating database..."
mysql -e "DROP DATABASE IF EXISTS Elixys;"
mysql -e "CREATE DATABASE Elixys;"
mysql < AllowRootAccess.sql
kill -KILL $SQLPID
killall mysqld
service mysql start
sleep 3
mysql Elixys < SetDatabasePrivileges.sql
mysql Elixys < CreateDatabaseTables.sql
mysql Elixys < CreateDatabaseProcedures.sql

# Restart the database
echo "Restarting database..."
service mysql restart
echo "Done With DB Config"


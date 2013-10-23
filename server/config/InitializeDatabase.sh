#!/bin/sh

### This script initializes the Elixys database ###

# Make sure we're running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root."
   exit 1
fi

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


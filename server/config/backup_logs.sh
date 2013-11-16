#!/bin/bash

if [ "$(whoami)" != "root" ]; then
    echo "Backup logs requires root priveleges"
    exit
fi

echo "Backing up all .log files..."
if [ ! -d "/opt/elixys/logs" ]; then
    echo "Could not find directory '/opt/elixys/logs'"
    exit
fi

# Switch directories and create the name of zip file.
cd /opt/elixys/logs
now="backup_$(date '+%Y_%m_%d_%H_%M_%S')"

zip $now *.log

echo "Sucessfully backed up the current log files!"
echo "Directory located in '/opt/elixys/logs/$now'"

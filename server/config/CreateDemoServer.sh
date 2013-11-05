#!/bin/sh

### This script puts this Elixys server in demo mode ###

# Make sure we're running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root."
   exit 1
fi

echo "Putting system in demo mode..."

# Create the demo mode file
touch /opt/elixys/demomode

# Initialize the database
./InitializeDatabase.sh

# Import demo data
python ImportDatabase.py demodata

echo "Done"


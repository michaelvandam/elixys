#!/bin/sh

### This script loads the demo data set onto an Elixys production server ###

# Get the current git repository
git clone --depth 1 git://github.com/michaelvandam/elixys.git

# Load the demo data into the Elixys database
mysql Elixys < elixys/config/DemoData.sql

# Remove the git repository
rm -rf elixys

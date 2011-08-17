#!/bin/sh

### This script loads the demo data set onto an Elixys production server ###

# Get the current git repository
git clone --depth 1 http://github.com/michaelvandam/elixys.git

# Run the Python script to load the demo data
cd elixys/config
python LoadDemoData.py
cd ../..

# Remove the git repository
rm -rf elixys


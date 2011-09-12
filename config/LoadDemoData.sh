#!/bin/sh

### This script loads the demo data set onto an Elixys production server ###

# Run the Python script to load the demo data
cd /opt/elixys/config
python LoadDemoData.py
cd ~

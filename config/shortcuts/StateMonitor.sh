#!/bin/sh

echo Starting state monitor...
cd /opt/elixys/cli
python StateMonitor.py
echo Done!
read continue


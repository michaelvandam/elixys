#!/usr/bin/env python
# (C) 2011-2012 Henry Herman (hherman at ucla dot edu)
# Elixys Radiochem System
# license available in license.txt
""" Elixys Default Module
    Export Classes:
        Reactor
"""


__author__="henry"
__date__ ="$Mar 25, 2011 4:45:17 PM$"

from util.device import Device

class Default(Device):
    """Reactor Class"""
    def __init__(self, config=None):
        pass
    


if __name__ == "__main__":
    print "Reactor Test"

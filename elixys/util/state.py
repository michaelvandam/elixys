#!/usr/bin/env python
# (C) 2011-2012 Henry Herman (hherman at ucla dot edu)
# Elixys Radiochem System
# license available in license.txt
""" Elixys state Module
    Export Classes:
        State
"""


__author__="henry"
__date__ ="$Mar 25, 2011 4:45:17 PM$"

class State(self):
    """State Class"""
    def __init__(self, description="None"):
        self.description = description

if __name__ == "__main__":
    print "Test State"

#!/usr/bin/env python
# (C) 2011-2012 Henry Herman (hherman at ucla dot edu)
# Elixys Radiochem System
# license available in license.txt

__author__="henry"
__date__ ="$Mar 25, 2011 4:45:17 PM$"


import config
import devicetypes

devices = {}
def factory():
    for deviceid,deviceconf in config.deviceconfigs.items():
        class_name = deviceconf['type']
        klass = getattr(devicetypes, class_name)
        devices[deviceid] = klass(deviceconf)
    return devices


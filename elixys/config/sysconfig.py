"""Elixys sysconfig module
"""
from configobj import ConfigObj
from validate import Validator

class ConfigError(Exception):
    pass

configpath = "config/sysconfig.ini"
configspecpath = "config/sysconfigspec.ini"

config = ConfigObj(configpath, configspec=configspecpath)
validator = Validator()

result = config.validate(validator)

if not result:
    raise ConfigError("Invalid Config syntax")

deviceconfigs = {}
for devicename,devicesettings in config['Devices'].items():
    deviceconfigs[devicename] = ConfigObj(devicesettings) #, configspec=config['Settings']['devicespecpath'])
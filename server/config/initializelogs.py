#!/usr/bin/env python

import sys
import os
import glob
import itertools
import ConfigParser
import pwd

uid = pwd.getpwnam("sofiebio").pw_uid
gid = pwd.getpwnam("sofiebio").pw_gid

fname = "/opt/elixys/config/elixyslog.conf"

cnf = ConfigParser.RawConfigParser(allow_no_value=True)
fcnf = open(fname)
cnf.readfp(fcnf)
hdlrs = [sec for sec in cnf.sections() if "File" in sec or "file" in sec]
fs = [eval(cnf.get(hdlr,'args'))[0] for hdlr  in hdlrs]  

(os.remove(f) for f in fs)
fz = [open(f,"w") for f in fs]
[f.close() for f in fz]
[os.chmod(f,0666) for f in fs]
[os.chown(f,uid,gid) for f in fs]



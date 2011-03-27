import logging
# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="henry"
__date__ ="$Mar 26, 2011 12:37:22 AM$"

from config import config
import logging.config

logging.config.fileConfig(config['Logging']['configpath'])

logger = logging.getLogger()

if __name__ == "__main__":
    print "Debug Logger"

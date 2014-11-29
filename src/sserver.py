# Simple socket server
#
# Deryk Barker, April 13, 2006
#

import socket
import ConfigParser

#
# The socket server class
#

class SServer:                          # Simple constructor
    def __init__ (self, basedir):
        import os
        self.basedir = basedir

        config = ConfigParser.ConfigParser()
        config.read(os.path.join(self.basedir, 'config.ini'))

        self.jobs = dict()

        self.weburl = config.get('settings', 'manager url')
        self.max_jobs = config.get('settings', 'max jobs')
        self.host = ''
        self.port = int(config.get('settings', 'port'))
        self.addr = (self.host, self.port)

    def handleconnection (self, newsock):         # Handle one incoming connection, from birth to death
        pass                      # defined in derived class

    def handlemsg (self, data):           # Handle one incoming message
        pass

    def serve (self):                   # Serve the port
        pass

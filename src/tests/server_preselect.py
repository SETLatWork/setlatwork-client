# -*- coding: iso-8859-1 -*-

import socket
import sys
import urllib, urllib2
import threading
import multiprocessing
import cPickle
import logging

#import job

log = logging.getLogger(__package__)

class Job_Thread(threading.Thread):
    """
    Creates a thread for the job. Allowing multiple jobs to be run on a machine
    """
    def __init__(self, data, basedir):
        threading.Thread.__init__(self)
        self.data = data
        self.basedir = basedir
        self.new_job = None

    def run(self):
        """
        """
        log.info('+- Starting thread %s %s'  %(self.data[0]['job']['id'], self.data[0]['job']['repository']))
        self.new_job = job.Job(self.data, self.basedir)
        self.new_job.run()
        log.info('+- Closing Thread %s %s' %(self.data[0]['job']['id'] , self.data[0]['job']['repository']))


    def terminate(self):
        """
        Sends a message to kill the job
        """
        log.info( 'Terminating: %s' % self.new_job)
        self.new_job.kill()


class Stream_Server(threading.Thread): #
    """
    Receive data from the etl manager and execute
    """

    def __del__(self):
        self.stop()

    def __init__ (self, basedir):
        super(Stream_Server, self).__init__() #threading.Thread.__init__(self)
        self._stop = threading.Event()

        import os
        import ConfigParser

        self.basedir = basedir

        config = ConfigParser.ConfigParser()
        config.read(os.path.join(self.basedir, 'config.ini'))

        self.jobs = dict()
        self.running = True

        self.weburl = config.get('settings', 'manager url')
        self.max_jobs = config.get('settings', 'max jobs')
        self.host = ''
        self.port = int(config.get('settings', 'port'))
        self.addr = (self.host, self.port)

    def run(self):
        import modules.pybonjour as pybonjour

        self.ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ssock.setblocking(0)
        self.ssock.bind(self.addr)
        self.ssock.listen(5)
        log.info('Server started!')

        """
        def register_callback(sdRef, flags, errorCode, name, regtype, domain):
            if errorCode == pybonjour.kDNSServiceErr_NoError:
                log.debug( 'Registered service:')
                log.debug( '  name    =%s' % name)
                log.debug( '  regtype =%s' % regtype)
                log.debug( '  domain  =%s' % domain)

        server_info = pybonjour.TXTRecord(dict(licens='Professional', max_jobs=2))
        self.sdRef = pybonjour.DNSServiceRegister(name = '',
                                             regtype = '_etlondemend._tcp',
                                             port = self.port,
                                             txtRecord = server_info,
                                             callBack = register_callback)
        return self.sdRef
        """
        self.status()
        self.serve()

    def stop(self):
        self.running = False
        self._stop.set()

        self.ssock.close()
        #self.sdRef.close()

    def stopped(self):
        return self._stop.isSet()

    def handleconnection(self):
        """
        Handle one incoming connection, from birth to death
        """
        try:
            while 1:
                data = self.newsock.recv(4096)
                #log.debug(data)
                if not self.handlemsg(data):
                    break
        except:
            self.newsock.close()

    def handlemsg(self, data):
        if not data:
            log.info("Client has exited!")
        else:
            self.sendmsg(cPickle.dumps('received'))
            try:
                data = cPickle.loads(data)

                log.debug(data)

                if data[-1] == 'terminate':
                    self.terminate(data[0])
                elif data[-1] == 'prod':
                    pass
                else:
                    self.status(status='Busy')

                    #job = Job_Thread(data, self.basedir)
                    #self.jobs[data[0]['job']['repository']] = job
                    #job.daemon = True
                    #job.start()

                    self.status(status='Available')
            except:
                log.critical(data)
                data = None

    def sendmsg(self, data):
        """
        Send an acknowledgment back to the website
        """
        self.newsock.send(data)

    def serve(self):
        try:
            while self.running:
                log.info('\n+- WAITING FOR CONNECTION...\n')
                self.newsock, self.raddr  = self.ssock.accept()
                log.debug('made connection')
                self.handleconnection()
                self.newsock.close()
            else:
                log.info('connection ended')
                return
        except:
            self.ssock.close()

    def terminate(self, name):
        log.info('Terminating Job %s' % name)
        try:
            self.supplies[name].terminate()
        except KeyError:
            log.error('Error: ' , KeyError , ' - No Job Found')


    def status(self, status='Available'):
        """
        Update the status of the job
        """
        svcURL = ''
        if self.weburl[-1] == '/':
            svcURL = "%sinit/server/status" % self.weburl
        else:
            svcURL = "%s/init/server/status" % self.weburl

        fme_license = 'Professional'

        params = {
            'server':socket.gethostname(),
            'status':status,
            'license':fme_license,
            'max_jobs':self.max_jobs,
            'jobs_running':threading.active_count()-2
        }
        log.debug(svcURL)
        log.debug('Params: %s' % params)

        site_conn = urllib2.urlopen(svcURL, urllib.urlencode(params))
        site_conn.close()


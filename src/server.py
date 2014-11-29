# -*- coding: iso-8859-1 -*-

import socket
import sys
import urllib, urllib2
import threading
import multiprocessing
import cPickle
import logging
import datetime

log = logging.getLogger(__package__)

class Job_Thread(threading.Thread):
    """
    Creates a thread for the job. Allowing multiple jobs to be run on a machine
    """
    def __init__(self, data, root, basedir):
        threading.Thread.__init__(self)
        self.data = data
        self.root = root
        self.basedir = basedir
        self.new_job = None

    def run(self):
        """
        """
        import job
        import time

        log.info('+- Starting thread %s %s'  %(self.data[0]['job']['id'], self.data[0]['repository']['name']))
        self.root.insert_job('end', dict(id=self.data[0]['job']['id'], name=self.data[0]['repository']['name'], started=datetime.datetime.now().strftime('%Y/%m/%d %H:%M'), user=self.data[0]['user']))
        #self.new_job = job.Job(self.data, self.root, self.basedir)
        #self.new_job.run()
        time.sleep(5)
        log.info('+- Closing Thread %s %s' %(self.data[0]['job']['id'] , self.data[0]['repository']['name']))
        self.root.history.insert('end', (self.data[0]['job']['id'], self.data[0]['repository']['name'], self.root.get_job(self.data[0]['job']['id'])['started'], datetime.datetime.now().strftime('%Y/%m/%d %H:%M'), self.data[0]['user']))
        self.root.delete_job(self.data[0]['job']['id'])

    def terminate(self):
        """
        Sends a message to kill the job
        """
        log.info( 'Terminating: %s' % self.new_job)
        self.new_job.kill()
        #self.close()



class Stream_Server(threading.Thread): #
    """
    Receive data from the etl manager and execute
    """

    def __del__(self):
        self.stop()

    def __init__ (self, root, basedir):
        super(Stream_Server, self).__init__()

        import os
        import ConfigParser

        self.root = root
        self.basedir = basedir

        self.jobs = dict()
        self.running = True

        config = ConfigParser.ConfigParser()
        config.read(os.path.join(self.basedir, 'config.ini'))
        self.weburl = config.get('settings', 'manager url')
        self.max_jobs = config.get('settings', 'max jobs')
        self.host = ''
        self.port = int(config.get('settings', 'port'))

    def run(self):
        """
        Start the server - enable jobs to be received
        """
        import modules.pybonjour as pybonjour

        self.ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ssock.bind((self.host, self.port))
        self.ssock.listen(5)
        log.info('Server started!')
        self.status()
        self.serve()

    def stop(self):
        """
        Stop the server from running/being able to receive jobs
        """
        self.running = False
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('localhost', self.port))
        self.ssock.close()


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
                    self.terminate(data[1]) # used to be 0 - name
                elif data[-1] == 'prod':
                    pass
                elif data[-1] == 'job':
                    self.status(status='Busy')

                    job = Job_Thread(data, self.root, self.basedir)
                    self.jobs[data[0]['job']['id']] = job
                    job.daemon = True
                    job.start()

                    self.status(status='Available')
            except Exception as e:
                log.error(e, exc_info=True)
                log.error(data)
                data = None

    def sendmsg(self, data):
        """
        Send an acknowledgment back to the website
        """
        self.newsock.send(data)

    def serve(self):
        try:
            while self.running:
                try:
                    log.info('\n+- WAITING FOR CONNECTION...\n')
                    self.newsock, self.raddr  = self.ssock.accept()
                    log.debug('made connection')
                    self.handleconnection()
                    self.newsock.close()
                except socket.timeout:
                    pass
            else:
                log.info('connection ended')
        except:
            self.ssock.close()

    def terminate(self, id):
        log.info('Terminating Job %s' % id)
        try:
            self.jobs[id].terminate()
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


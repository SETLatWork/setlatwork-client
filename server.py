# -*- coding: utf-8 -*-#
import threading
import logging
import job
import json
import time
import requests
import socket
import wx
import os
import datetime

log = logging.getLogger(__name__)

class Job_Thread(threading.Thread):

    def __init__(self, data, basedir, user):
        threading.Thread.__init__(self)
        self.data = data
        self.basedir = basedir
        self.new_job = None
        self.user = user

    def run(self):
        log.info("#--------------------------------------------------------------------")
        log.info('+- Starting Job {}'.format(self.data['name']))
        log.info("#--------------------------------------------------------------------")
        try:
            self.new_job = job.Job(self.data, self.basedir, self.user)
            self.new_job.run()
        except Exception as e:
            log.error(e, exc_info=True)
        log.info("#--------------------------------------------------------------------")
        log.info('+- Closing Job {}'.format(self.data['name']))
        log.info("#--------------------------------------------------------------------")

    def terminate(self):
        log.info( 'Terminating: {}'.formatself.new_job)
        self.new_job.kill()



class Server_Thread(threading.Thread):

    def __del__(self):
        self._stop.set()

    def __init__ (self, basedir, user):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.running = True
        
        self.basedir = basedir

        self.jobs = dict()
        self.user = user

    def stop(self):
        self.running = False
        self._stop.set()

    def refresh_token(self):
        
        try:
            r = requests.get("%s/default/user/jwt" % self.user['manager'], params={'token':self.user['token']}, headers=self.user['bearer'], verify=self.user['cert_path'])
            log.info('GET:User - Status Code: %s' % r.status_code)

            self.user['token'] = json.loads(r.text)['token']
            self.user['bearer'] = {"Authorization":"Bearer %s" % json.loads(r.text)['token']}
            self.user['token_created'] = datetime.datetime.now()
        except (ValueError, requests.ConnectionError):
            try:
                r = requests.get("%s/default/user/jwt" % self.user['manager'], params={'username':self.user['email'], 'password':self.user['password']}, verify=self.user['cert_path'])
                log.info('GET:User - Status Code: %s' % r.status_code)
            except requests.ConnectionError as e:
                log.error(e)
                return

            try:
                self.user['token'] = json.loads(r.text)['token']
                self.user['bearer'] = {"Authorization":"Bearer %s" % json.loads(r.text)['token']}
                self.user['token_created'] = datetime.datetime.now()
            except ValueError:
                # change the system tray icon to red
                log.error('Unable to connect to the server')

        
        log.debug('Token updated: after %s' % (datetime.datetime.now() - self.user['token_created']).seconds)

    def run(self):
        check_delay = 10
        while self.running:
            try:
                r = requests.get("%s/api/job.json" % self.user['manager'], params={'computer':socket.gethostname()}, headers=self.user['bearer'], verify=self.user['cert_path'])
                log.info('GET:Job - Status Code: %s' % r.status_code)
                #print (datetime.datetime.now() - self.user['token_created']).seconds
                if (datetime.datetime.now() - self.user['token_created']).seconds > 300:
                    self.refresh_token()
            except requests.ConnectionError as e:
                log.error(e)
                log.info('Attempt reconnect')
                self.refresh_token()
                #wx.MessageBox('Unable to connect to the server at this time', 'Server Connection Error', wx.OK | wx.ICON_ERROR)
                #exit(1)

            if r.status_code == 200:
                if r.json()['new_job']:
                    self.create_new_job(r.json()['new_job'])
                if r.json()['current_jobs']:
                    self.check_jobs(r.json()['current_jobs'])
                check_delay = 5
            elif r.status_code == 204:
                check_delay = 10
            elif r.status_code == 503:
                check_delay = 10
            elif r.status_code == 400:
                print '400 - Attempt reconnect'
                #self.refresh_token()
                #wx.MessageBox('Login timeout, please login again.', 'Server Connection Error', wx.OK | wx.ICON_ERROR)
                #exit(1)


            time.sleep(check_delay)
        else:
            log.info('connection ended')

    def check_jobs(self, current_jobs):
        for job in current_jobs:
            if job['id'] not in self.jobs:
                self.terminate(job['id'])

    def create_new_job(self, data):
        if not data:
            log.info("Client has exited!")
        else:
            try:
                for k, v in data.iteritems():
                    log.info('%s : %s' %(k, v))

                job = Job_Thread(data, self.basedir, self.user)
                self.jobs[data['id']] = job
                job.daemon = True
                job.start()
            except Exception as e:
                log.error(e, exc_info=True)
                log.error(data)
                data = None


    def terminate(self, id):
        log.info('Terminating Job {}'.format(id))
        try:
            self.jobs[id].terminate()
        except KeyError:
            log.error('Error: Job not found - could not be terminated')


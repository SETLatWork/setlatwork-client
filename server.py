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

# from wx.lib.pubsub import setuparg1
# from wx.lib.pubsub import pub as Publisher

log = logging.getLogger(__name__)

class Job_Thread(threading.Thread):

    def __init__(self, data, basedir, user, jobs):
        threading.Thread.__init__(self)
        self.data = data
        self.basedir = basedir
        self.new_job = None
        self.user = user
        self.jobs = jobs

    def run(self):
        log.info("#--------------------------------------------------------------------")
        log.info('+- Starting Job {}'.format(self.data['name']))
        log.info("#--------------------------------------------------------------------")
        try:
            self.new_job = job.Job(self.data, self.basedir, self.user, self.jobs)
        except Exception as e:
            log.error(e, exc_info=True)
        log.info("#--------------------------------------------------------------------")
        log.info('+- Closing Job {}'.format(self.data['name']))
        log.info("#--------------------------------------------------------------------")

    def terminate(self):
        log.info('Terminating: {}'.format(self.new_job))
        log.info(self.jobs)
        self.new_job.kill()



class Server_Thread(threading.Thread):

    def __del__(self):
        self._stop.set()

    def __init__ (self, basedir, user):
        threading.Thread.__init__(self)

        self.basedir = basedir
        self.user = user

        self._stop = threading.Event()
        self.running = True
        
        self.jobs = dict()
        

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
                
                if (datetime.datetime.now() - self.user['token_created']).seconds > 300:
                    self.refresh_token()

            except requests.ConnectionError as e:
                log.error(e)
                log.info('Attempt reconnect')
                self.refresh_token()

            if r.status_code == 200:
                new_job_id = None
                if r.json()['new_job']:
                    new_job = r.json()['new_job']
                    new_job_id = new_job['id']
                    self.create_new_job(new_job)
                if r.json()['current_jobs']:
                    self.check_jobs(new_job_id, r.json()['current_jobs'])
                check_delay = 5
            elif r.status_code == 204:
                check_delay = 10
            elif r.status_code == 503:
                check_delay = 10
            elif r.status_code == 400:
                print '400 - Attempt reconnect'

            time.sleep(check_delay)
        else:
            log.info('connection ended')


    def create_new_job(self, new_job):
        if not new_job:
            log.info("Client has exited!")
        else:
            try:
                for k, v in new_job.iteritems():
                    log.info('%s : %s' %(k, v))

                job = Job_Thread(new_job, self.basedir, self.user, self.jobs)
                job.daemon = True
                job.start()

                self.jobs[new_job['id']] = job
            except Exception as e:
                log.error(e, exc_info=True)
                log.error(new_job)
                new_job = None

    def check_jobs(self, new_job_id, current_jobs):
        current_jobs = [v['id'] for v in current_jobs] + [new_job_id]
        log.debug(current_jobs)
        for k, v in self.jobs.iteritems():
            log.debug(k)
            if k not in current_jobs:
                log.info('Terminating Job {}'.format(k))
                v.terminate()


    # def terminate(self, job_id):
    #     log.info('Terminating Job {}'.format(job_id))
    #     try:
    #         self.jobs[job_id].terminate()
    #     except KeyError:
    #         log.error('Error: Job not found - could not be terminated')


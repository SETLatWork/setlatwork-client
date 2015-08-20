# -*- coding: iso-8859-1 -*-
import threading
import logging
import job

log = logging.getLogger(__name__)

class Job_Thread(threading.Thread):
    """
    Creates a thread for the job. Allowing multiple jobs to be run on a machine
    """
    def __init__(self, data, basedir, user):
        threading.Thread.__init__(self)
        self.data = data
        self.basedir = basedir
        self.new_job = None
        self.user = user

    def run(self):
        """
        Start Thread
        """
        import time

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
        """
        Sends a message to kill the job
        """
        log.info( 'Terminating: {}'.formatself.new_job)
        self.new_job.kill()



class Server_Thread(threading.Thread):
    """
    Receive data from the etl manager and execute
    """

    def __del__(self):
        self.stop()

    def __init__ (self, basedir, user):
        threading.Thread.__init__(self)

        import os
        import ConfigParser, getpass

        self.basedir = basedir

        self.jobs = dict()

        config = ConfigParser.ConfigParser()
        config.read(os.path.join(self.basedir, 'setup'))
        self.user = user
        #self.email = config.get(getpass.getuser(), 'email')
        #self.password = config.get(getpass.getuser(), 'password').decode('base64')
        #self.fme_location = config.get(getpass.getuser(), 'fme location')

    def run(self):
        """
        Start checking SETL Ondemand Manager for Jobs periodically
        """
        import time
        import requests, json
        import sys, os
        from requests.auth import HTTPBasicAuth



        """
        try:
            fme_path, filename = os.path.split(self.fme_location)
            sys.path.append(os.path.join(fme_path, 'fmeobjects\python27'))
            import fmeobjects

            licMan = fmeobjects.FMELicenseManager()
            log.info('FME License Type :', licMan.getLicenseType())
            fme_license = licMan.getLicenseType()
        except fmeobjects.FMEException as e:
            log.error(e.message)
        except Exception as e:
            log.error(e)
        """


        while 1:
            log.info('\n+- WAITING FOR CONNECTION...\n')

            params = {
                'computer':os.environ['COMPUTERNAME']
            }

            r = requests.get("http://www.setlondemand.com/manager/api/job.json", params=params, auth=HTTPBasicAuth(self.user['email'], self.user['password']))

            if r.status_code == 200:
                new_job = r.json()['new_job']
                log.info(new_job)

                self.create_new_job(new_job)

            time.sleep(10)
        else:
            log.info('connection ended')

    def create_new_job(self, data):
        """
        Create a thread for the new job received
        """
        if not data:
            log.info("Client has exited!")
        else:
            try:
                log.debug(data)

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
            log.error('Error: {} - No Job Found'.format(KeyError))


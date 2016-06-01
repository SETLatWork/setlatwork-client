# -*- coding: utf-8 -*-#
import os
import sys
import string
import shutil
import json
from collections import OrderedDict
import logging
import socket
import requests
from requests.auth import HTTPBasicAuth
import subprocess

log = logging.getLogger(__package__)

class Job():

    def __init__(self, data, basedir, user):
        self.basedir = basedir
        self.data = data
        self.user = user

        self.terminate = False
        self.execute = None

        self.workspace_dir = self.basedir + '/temp/' + str(self.data['id']) + '_' + self.data['name'][0:-4] + '/'
        os.makedirs(self.workspace_dir)

        log.debug(basedir)
        log.info(self.workspace_dir)

        self.token = self.user['token']
        self.fme_location = self.user['fme']

        log.info(self.fme_location)


    def kill(self):
        try:
            log.info('Delete PID: %s' % self.execute.pid)
            self.execute.terminate()
        except:
            log.error('Failed to terminate workspace - supply will terminate on completion')

        self.terminate = True
        self.error = 'Terminated'


    def status(self, status='Running', workspace=None, error=None):
        params = {
            'job':self.data['id'],
            'status':status,
            'workspace':workspace,
            'error':error
        }

        log.debug(params)

        response = requests.put('%s/api/job' % self.user['manager'] , params=params, headers=self.token)
        log.info("PUT:Job - Status Code - %s: " % response.status_code)
        
        # if the update returns a bad response then kill the job


    def run_workspace(self, workspace_path, workspace, parameters=None):
        parameters = []
        log.debug(type(workspace['parameters']))
        log.debug(workspace['parameters'])
        for k, v in workspace['parameters'].iteritems():
            log.debug(k)
            log.debug(v)
            parameters.append('--{0} "{1}"'.format(k,v))

        # Run workspace
        run_arg = [self.fme_location, workspace_path] + parameters
        log.info('Running {}'.format(run_arg))

        self.execute = subprocess.Popen(run_arg, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        log.info('Run PID: {}'.format(self.execute.pid))

        while True:
            line = self.execute.stdout.readline()
            if not line:
                break
            log.debug(line)
            sys.stdout.flush()
            if 'FME floating license system failure: cannot connect to license server(-15)' in line:
                return "Could not obtain an FME license"

        log.debug(workspace)
        #features = []
        log_file = ''
        if '$(FME_MF_DIR)' in workspace['log_file']:
            log_file = workspace['log_file'].replace('$(FME_MF_DIR)', self.workspace_dir)
        else:
            log_file = workspace['log_file']

        log.debug(log_file)

        # Create Log Counts
        log.debug('Log File Exists: %s' % os.path.exists(log_file))

        if os.path.exists(log_file):

            # upload file to setl ondemand
            r = requests.post("%s/api/log" % self.user['manager'], params=dict(workspace=workspace['id'], job=self.data['id']), files={'file': open(log_file)}, headers=self.token)
            log.info('POST:Log - Status Code: %s' % r)

        else:
            log.error('Could not locate workspace log file')
            return "Could not locate workspace log file."


        ##################################
        ## Return Result
        self.status(workspace=workspace['id'])

        if self.terminate == True:
            return "Job was Terminated"
        else:
            return



    def run(self):
        status = ''
        workspace_name = ''

        log.debug(type(self.data['workspaces']))
        if isinstance(self.data['workspaces'], dict):
            pass
        elif isinstance(self.data['workspaces'], basestring):
            self.data['workspaces'] = json.loads(self.data['workspaces'])

        for workspace in self.data['workspaces']:
            log.debug(workspace)

            if isinstance(workspace, dict):
                pass
            elif isinstance(workspace, basestring):
                workspace = json.loads(workspace)
            else:
                log.error('Could not recognise data passed')
                status = "Could not recognise data passed"
                break
            
            workspace_name = workspace['name']

            # Check if the Kill command issued
            if self.terminate:
                status = 'Job has been Terminated'
                break

            # download the workspace
            with open(os.path.join(self.workspace_dir, workspace['name']), 'wb') as handle:
                r = requests.get('{0}/default/download/db/{1}'.format(self.user['manager'], workspace['file']), stream=True, headers=self.token)
                log.info('GET:File - Status Code: %s' % r)
                if not r.ok:
                    status='Could not retrieve %s' % workspace['name']
                    break

                for block in r.iter_content(1024):
                    if not block:
                        break

                    handle.write(block)

            ## Run the WORKSPACE
            if os.path.exists(os.path.join(self.workspace_dir, workspace['name'])):
                status = self.run_workspace(os.path.join(self.workspace_dir, workspace['name']), workspace)
            else:
                log.error('Unable to locate {}'.format(workspace['name']))
                status = 'Unable to locate {}'.format(workspace['name'])
                break

        ## Delete workspace and log on completion
        shutil.rmtree(self.workspace_dir)

        if status:
            log.debug('failed')
            log.error('{0} {1}'.format(workspace_name, status))
            self.status(status='Failed', error='Failed - {}'.format(status))
            return
        else:
            log.debug('completed')
            self.status(status='Completed')
            return

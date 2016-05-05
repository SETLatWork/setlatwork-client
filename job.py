# -*- coding: utf-8 -*-#
import os
import string
import shutil
import json
from collections import OrderedDict
import logging
import requests
from requests.auth import HTTPBasicAuth

log = logging.getLogger(__package__)

class Job():

    def __init__(self, data, basedir, user):
        self.basedir = basedir
        self.data = data
        log.debug(type(data))
        self.user = user

        self._counts = OrderedDict()
        self.terminate = False
        self.execute = None

        self.workspace_dir = self.basedir + '/temp/' + str(self.data['id']) + '_' + self.data['name'][0:-4] + '/'
        os.makedirs(self.workspace_dir)

        log.debug(basedir)
        log.debug(self.workspace_dir)

        import ConfigParser, getpass

        config = ConfigParser.ConfigParser()
        config.read(os.path.join(self.basedir, 'setup'))

        self.manager_url = "127.0.0.1:8000/api/v1"
        self.token = self.user['token']
        self.fme_location = self.user['fme']


    def kill(self):
        try:
            log.info('Delete PID: %s' % self.execute.pid)
            self.execute.terminate()
        except:
            log.error('Failed to terminate workspace - supply will terminate on completion')

        self.terminate = True
        self.error = 'Terminated'


    def status(self, status='Running', error=None, counts=None):
        import socket

        params = {
            'job':self.data['id'],
            'status':status,
            'counts':counts,
            'error':error
        }

        log.debug(params)
        response = requests.post('http://%s/job' % self.manager_url , params=params, headers=self.token)

        log.info("PUT:Job - Status Code - %s: " % response.status_code)

        # if the update returns a bad response then kill the job


    def run_workspace(self, workspace_path, workspace, parameters=None):
        import subprocess

        parameters = ' '
        log.debug(type(workspace['parameters']))
        log.debug(workspace['parameters'])
        for k, v in workspace['parameters'].iteritems():
            log.debug(k)
            log.debug(v)
            parameters += '--{0} "{1}"'.format(k,v)

        features = []
        log_file = ''

        with open(workspace_path) as f:
            for line in f.readlines():
                if string.count(line, "LOG_FILENAME \""):
                    if '$(FME_MF_DIR)' in line:
                        log_file = line.split(' ')[-1].replace('$(FME_MF_DIR)', self.workspace_dir)
                    else:
                        log_file = line.split(' ')[-1]

                # Create list of Features output in workspace
                if string.count(line, '__wb_out_feat_type__,'): #@SupplyAttributes(__wb_out_feat_type__,

                    # Add to list of Features
                    if string.split(line)[-1].split(',')[-1][0:-1] not in features:
                        features.append(string.split(line)[-1].split(',')[-1][0:-1])

                # Check output dir exists
                if string.count(line, 'DEFAULT_MACRO DestDataset_'):
                    output_dir = line.split('{')[-1].split('}')[0].split()[-1]
                    log.debug(output_dir)

                    if output_dir[0] == '$':
                        output_param = output_dir.replace('$(','').replace(')','')
                        log.debug(output_param)
                        if output_param in workspace['parameters']:
                            log.debug('Output Dir: {}'.format(workspace['parameters'][output_param]))
                        else:
                            log.error('Output parameter not given!')
                            log.debug(parameters)


        log.debug('Features: {}'.format(features))

        execute_params = workspace_path + parameters

        # Run workspace
        log.info('Running {0} {1}'.format(self.fme_location, execute_params))
        error = False

        #startupinfo = subprocess.STARTUPINFO()
        #startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.execute = subprocess.Popen("{0} {1}".format(self.fme_location, execute_params), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False) # , startupinfo=startupinfo
        log.debug('Run PID: {}'.format(self.execute.pid))

        import sys
        while True:
            line = self.execute.stdout.readline()
            if not line:
                break
            log.debug(line)
            sys.stdout.flush()
            if 'FME floating license system failure: cannot connect to license server(-15)' in line:
                return 'Could not obtain a license'

        # Create Log Counts
        workspace_counts = OrderedDict()

        if os.path.exists(log_file):

            # upload file to setl ondemand
            r = requests.post("http://%s/log" % self.manager_url, params=dict(workspace=workspace['id'], job=self.data['id']), files={'file': open(log_file)}, headers=self.token)
            log.debug(r.text)

            with open(log_file) as f:
                for line in f.readlines():
                    if string.count(line,'|STATS |'):
                        for feature in features:

                            if string.count(line,'|STATS |{} '.format(feature)):
                                table_name = line.split('|')[4].split()[0]
                                table_count = line.split('|')[4].split()[-1]

                                log.debug(line)
                                if table_name in workspace_counts:
                                    try:
                                        if int(workspace_counts[table_name]) > int(table_count):
                                            workspace_counts[table_name] = table_count
                                    except:
                                        pass
                                else:
                                    try:
                                        table_count = int(table_count)
                                        workspace_counts[table_name] = table_count
                                    except:
                                        pass

                    elif string.count(line, '|ERROR |'):
                        log.critical(line)
                        log.debug(line.split('|')[-1].strip())
                        error = True

        self._counts.update(workspace_counts)

        ##################################
        ## Return Result
        self.status(counts=workspace_counts)

        if self.terminate == True:
            return
        elif error or len(workspace_counts) == 0:
            log.error('No features written')
            return 'Error - no features were written.'
        else:
            log.info('|=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
            log.info('|                           Features Written Summary')
            log.info('|=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
            for feature, count in workspace_counts.items():
                try:
                    log.info('|{0:29s}                                     {1:9d}'.format(feature, int(count)))
                except:
                    log.info('|{0}                                             {1}'.format(feature, count))
            log.info('|==============================================================================')
            log.info('Completed {}'.format(workspace['name']))
            return



    def run(self):
        status = ''
        workspace_name = ''

        try:
            for workspace in self.data['workspaces']:
                log.debug(workspace)
  
                if isinstance(workspace, dict):
                    pass
                elif isinstance(workspace, basestring):
                    workspace = json.loads(workspace)
                else:
                    log.error('Not recognised format')
                    raise ValueError
                
                # Check if the Kill command issued
                workspace_name = workspace['name']
                if self.terminate:
                    return 'Terminated'

                # download the workspace
                with open(os.path.join(self.workspace_dir, workspace['name']), 'wb') as handle:
                    response = requests.get('http://{0}/download/db/{1}'.format(self.manager_url, workspace['file']), stream=True, headers=self.token)

                    if not response.ok:
                        # Something went wrong
                        pass

                    for block in response.iter_content(1024):
                        if not block:
                            break

                        handle.write(block)

                log.debug(workspace)

                ## Check if workspace exists
                workspace_path = os.path.join(self.workspace_dir, workspace['name'])
                if os.path.exists(workspace_path):
                    status = self.run_workspace(workspace_path, workspace)
                else:
                    log.error('Unable to locate {}'.format(workspace['name']))
                    status = 'Unable to locate {}'.format(workspace['name'])

        except Exception as e:
            log.error(e, exc_info=True)
            status = e

        ## Store which workspaces failed
        shutil.rmtree(self.workspace_dir)

        if status:
            log.error('{0} {1}'.format(workspace_name, status))
            self.status(status='Failed', error='Failed - {}'.format(status))
            return
        elif self.terminate:
            self.status(status='Failed', error='Terminated')
            return
        else:
            self.status(status='Completed')
            return



    @property
    def counts(self):
        return self._counts

# -*- coding: utf-8 -*-#
import os
import sys
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

        self.manager_url = "127.0.0.1:8000/manager"
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
        response = requests.put('http://%s/api/job' % self.manager_url , params=params, headers=self.token)
        log.info("PUT:Job - Status Code - %s: " % response.status_code)

        # if the update returns a bad response then kill the job


    def run_workspace(self, workspace_path, workspace, parameters=None):
        import subprocess
        import time

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

        #startupinfo = subprocess.STARTUPINFO()
        #startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.execute = subprocess.Popen(run_arg, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False) # , startupinfo=startupinfo
        log.info('Run PID: {}'.format(self.execute.pid))

        while True:
            line = self.execute.stdout.readline()
            if not line:
                break
            log.debug(line)
            sys.stdout.flush()
            if 'FME floating license system failure: cannot connect to license server(-15)' in line:
                return 'Could not obtain a license'


        features = []
        log_file = ''

        with open(workspace_path) as f:
            for line in f.readlines():
                # locate the log file output location
                # LOG_FILENAME "$(FME_MF_DIR)esrishape2ogckml.log"
                if string.count(line, "LOG_FILENAME \""):
                    if '$(FME_MF_DIR)' in line:
                        log_file = line.split(' ')[-1].replace('$(FME_MF_DIR)', self.workspace_dir).replace('"', '').strip()
                    else:
                        log_file = line.split(' ')[-1].replace('"', '').strip()
                    log.debug(log_file)

                # Create list of Features output in workspace
                if string.count(line, '__wb_out_feat_type__,'): #@SupplyAttributes(__wb_out_feat_type__,
                    # Add to list of Features
                    if string.split(line)[-1].split(',')[-1][0:-1] not in features:
                        features.append(string.split(line)[-1].split(',')[-1][0:-1])
                elif string.count(line, '__wb_out_feat_type__<comma>'):
                    feature = filter(lambda d: '<comma>' in d ,string.split(line))[-1].split('<comma>')[-1].split('<')[0]
                    if feature not in features:
                        features.append(feature)

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


        # Create Log Counts
        workspace_counts = OrderedDict()
        error = False
        log.debug('Log File Exists: %s' % os.path.exists(log_file))

        #if os.path.exists(log_file):

        # upload file to setl ondemand
        r = requests.post("http://%s/api/log" % self.manager_url, params=dict(workspace=workspace['id'], job=self.data['id']), files={'file': open(log_file)}, headers=self.token)
        log.info('POST:Log - Status Code: %s' % r)
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
        #else:
        #    log.error('Could not locate workspace log file')
        #    return 'Error - could not locate workspace log file.'

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

        log.debug(type(self.data['workspaces']))
        if isinstance(self.data['workspaces'], dict):
            pass
        elif isinstance(self.data['workspaces'], basestring):
            self.data['workspaces'] = json.loads(self.data['workspaces'])

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
                    r = requests.get('http://{0}/default/download/db/{1}'.format(self.manager_url, workspace['file']), stream=True, headers=self.token)
                    log.info('GET:File - Status Code: %s' % r)
                    if not r.ok:
                        status = 'Could not retrieve %s' % workspace['name']
                        break

                    for block in r.iter_content(1024):
                        if not block:
                            break

                        handle.write(block)

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
        #shutil.rmtree(self.workspace_dir)

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

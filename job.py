# -*- coding: iso-8859-1 -*-
import os, string, shutil
from collections import OrderedDict
import logging
import requests
from requests.auth import HTTPBasicAuth

log = logging.getLogger(__package__)

class Job():
    """
    """

    def __init__(self, data, basedir, user):
        self.basedir = basedir
        self.data = data
        self.user = user

        self._counts = OrderedDict()
        self.terminate = False
        self.execute = None

        self.workbench_dir = self.basedir + '\\temp\\' + str(self.data['id']) + '_' + self.data['name'][0:-4] + '/'
        os.makedirs(self.workbench_dir)

        log.debug(basedir)
        log.debug(self.workbench_dir)

        import ConfigParser, getpass

        config = ConfigParser.ConfigParser()
        config.read(os.path.join(self.basedir, 'setup'))
        self.email = self.user['email'] #config.get(getpass.getuser(), 'email')
        self.password = self.user['password'] #config.get(getpass.getuser(), 'password').decode('base64')
        self.fme_location = self.user['fme'] #config.get(getpass.getuser(), 'fme location')


    def kill(self):
        """
        Set the supply to self terminate.
        """
        try:
            print 'Delete PID:' , self.execute.pid
            self.execute.terminate()
        except:
            log.error('Failed to terminate workbench - supply will terminate on completion')

        self.terminate = True
        self.error = 'Terminated'


    def status(self, status='Running', error=None, counts=None):
        import socket
        """
        Send job status to the web-server

        parameters
        ----------
        Status:
            String - Running, Completed, Error
        Counts:
            Dict - key=feature name, value=count value
        """

        params = {
            'job':self.data['id'],
            'status':status,
            'counts':counts,
            'error':error
        }

        log.debug(params)
        response = requests.post('http://www.setlondemand.com/manager/api/job', params=params, auth=HTTPBasicAuth(self.email, self.password))

        print response.status_code

        # if the update returns a bad response then kill the job


    def run_workbench(self, workbench_path, workbench, parameters=None):
        """
        Run a workbench with the given parameters

        Parameters
        ----------
        workbench:
            string - the path of the workbench to be run.
        parameters:
            string - the parameters to be used to run the workbench.


        Returns
        -------
            None:
                Success
            String
                The Error message.
        """
        import subprocess

        parameters = ' '
        log.debug(type(workbench['parameters']))
        log.debug(workbench['parameters'])
        for k, v in workbench['parameters'].iteritems():
            log.debug(k)
            log.debug(v)
            parameters += '--{0} "{1}"'.format(k,v) # parameter['name'], parameter['value']

        features = []
        log_file = ''

        with open(workbench_path) as f:
            for line in f.readlines():
                if string.count(line, "LOG_FILENAME \""):
                    if '$(FME_MF_DIR)' in line:
                        log_file = line.split(' ')[-1].replace('$(FME_MF_DIR)', self.workbench_dir)
                    else:
                        log_file = line.split(' ')[-1]

                # Create list of Features output in Workbench
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
                        if output_param in workbench['parameters']:
                            log.debug('Output Dir: {}'.format(workbench['parameters'][output_param]))
                        else:
                            log.error('Output parameter not given!')
                            log.debug(parameters)

                    """
                    # Check if data is output to parameterised location
                    if output_dir == '$(DataDest)':
                        if not os.path.exists(self.supply_info['output_dir']):
                            print('test1 ' + line.split('{')[-1].split('}')[0])

                    # Check if data is output to D:\ location
                    elif 'D:\\' in output_dir:
                        if not os.path.exists('\\'.join(output_dir.split('\\')[0:-1])):
                            print('Creating Directory: ' + '\\'.join(output_dir.split('\\')[0:-1]))
                            os.makedirs('\\'.join(output_dir.split('\\')[0:-1]))

                    # If output to ORACLE do nothing
                    elif 'ORACLE' in output_dir:
                        pass

                    # Otherwise not setup to handle so output to screen.
                    else:
                        if not 'puts {' in line:
                            log.error('Invalid directory {}'.format(output_dir))
                    """

        log.debug('Features: {}'.format(features))

        #multiple_files = [('file', (log_file, open(log_file, 'r'), 'text/log')),]
        #r = requests.post("http://www.setlondemand.com/manager/api/log", params=dict(repository=self.data['repository']), files=multiple_files)
        #log.info(r.text)

        execute_params = workbench_path + parameters

        # Test upload log file
        #r = requests.post("http://www.setlondemand.com/manager/api/log", params=dict(workbench=workbench['id'], job=self.data['id']), files={'file': open(self.workbench_dir + "\\Exercise3.log")}, auth=HTTPBasicAuth(self.email, self.password))
        #log.debug(r.text)

        # Run workbench
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
        workbench_counts = OrderedDict()

        if os.path.exists(log_file):

            # upload file to setl ondemand
            r = requests.post("http://www.setlondemand.com/manager/api/log", params=dict(workbench=workbench['id'], job=self.data['id']), files={'file': open(log_file)}, auth=HTTPBasicAuth(self.email, self.password))
            log.debug(r.text)

            with open(log_file) as f:
                for line in f.readlines():
                    if string.count(line,'|STATS |'):
                        for feature in features:

                            if string.count(line,'|STATS |{} '.format(feature)):
                                table_name = line.split('|')[4].split()[0]
                                table_count = line.split('|')[4].split()[-1]

                                print(line)
                                if table_name in workbench_counts:
                                    try:
                                        if int(workbench_counts[table_name]) > int(table_count):
                                            workbench_counts[table_name] = table_count
                                    except:
                                        pass
                                else:
                                    try:
                                        table_count = int(table_count)
                                        workbench_counts[table_name] = table_count
                                    except:
                                        pass

                    elif string.count(line, '|ERROR |'):
                        log.critical(line)
                        print(line.split('|')[-1].strip())
                        error = True

        self._counts.update(workbench_counts)

        ##################################
        ## Return Result
        self.status(counts=workbench_counts)

        if self.terminate == True:
            return
        elif error or len(workbench_counts) == 0:
            log.error('No features written')
            return 'Error - no features were written.'
        else:
            log.info('|=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
            log.info('|                           Features Written Summary')
            log.info('|=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
            for feature, count in workbench_counts.items():
                try:
                    log.info('|{0:29s}                                     {1:9d}'.format(feature, int(count)))
                except:
                    log.info('|{0}                                             {1}'.format(feature, count))
            log.info('|==============================================================================')
            log.info('Completed {}'.format(workbench['name']))
            return



    def run(self):
        """
        """
        status = ''

        try:
            for workbench in self.data['workbenches']:
                workbench = eval(workbench)
                # Check if the Kill command issued
                if self.terminate:
                    return 'Terminated'

                # download the workbench
                with open(os.path.join(self.workbench_dir, workbench['name']), 'wb') as handle:
                    response = requests.get('http://www.setlondemand.com/manager/default/download/db/{}'.format(workbench['workbench']), stream=True, auth=HTTPBasicAuth(self.email, self.password))

                    if not response.ok:
                        # Something went wrong
                        pass

                    for block in response.iter_content(1024):
                        if not block:
                            break

                        handle.write(block)

                log.debug(workbench)

                # Test log file upload
                #with open(self.workbench_dir + "\\Exercise3.log", 'w') as t_log:
                #    t_log.write('test test\n')

                ## Check if workbench exists
                workbench_path = os.path.join(self.workbench_dir, workbench['name'])
                if os.path.exists(workbench_path):
                    status = self.run_workbench(workbench_path, workbench)
                else:
                    log.error('Unable to locate {}'.format(workbench['name']))
                    status = 'Unable to locate {}'.format(workbench['name'])

        except Exception as e:
            log.error(e, exc_info=True)
            status = e

        ## Store which workbenches failed
        shutil.rmtree(self.workbench_dir)

        if status:
            log.error('{0} {1}'.format(workbench['name'], status))
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
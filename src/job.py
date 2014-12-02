# -*- coding: iso-8859-1 -*-
import os, string, datetime, sys, time, Queue
import shutil, glob
import urllib, urllib2
import subprocess
from Tkinter import *
from collections import OrderedDict
import logging

log = logging.getLogger(__package__)

class Job():
    """
    """

    def __init__(self, data, root):
        self.app = root

        try:
            self.job = data[0]['job']
            self.repository = data[0]['repository']
            self.repository['location'] = r'C:\Users\James\Documents\etlondemand\etlmanager\applications\init\uploads'
            self.workbenches = data[0]['job']['workbenches']
        except:
            log.error('Failed to decode data', exc_info=True)
            self.error = 'Failed to decode data'
            self.status(status='Failed')


        log.debug('job: %s' % self.job)
        log.debug('repository: %s' % self.repository)
        log.debug('workbenches: %s' % self.workbenches)

        self._counts = OrderedDict()
        self.terminate = False
        self.execute = None


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


    def status(self, status, error=None, counts=None):
        """
        Send job status to the web-server

        parameters
        ----------
        Status:
            String - Running, Completed, Error
        Counts:
            Dict - key=feature name, value=count value
        """
        import socket
        svcURL = ''
        if self.app.weburl[-1] == '/':
            svcUrl = "%sinit/server/result" % self.app.weburl
        else:
            svcUrl = "%s/init/server/result" % self.app.weburl

        params = {
            'job':self.job['id'],
            'status':status,
            'server':socket.gethostname(),
            'counts':counts,
            'error':error
        }

        log.debug(svcUrl)
        log.debug('Params: %s' %(params))

        try:
            site_conn = urllib2.urlopen(svcUrl, urllib.urlencode(params))
        except:
            log.error('Unable to connect to web server')
        finally:
            site_conn.close()



    def run_workbench(self, workbench, parameters=None):
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
        parameters = parameters or ' '

        features = []

        workbench_path = os.path.join(self.repository['location'], workbench)
        with open(workbench_path) as f:
            for line in f.readlines():

                # Create list of Features output in Workbench
                if string.count(line, '__wb_out_feat_type__,'): #@SupplyAttributes(__wb_out_feat_type__,

                    # Add to list of Features
                    if string.split(line)[-1].split(',')[-1][0:-1] not in features:
                        features.append(string.split(line)[-1].split(',')[-1][0:-1])

                # Check output dir exists
                if string.count(line, 'DEFAULT_MACRO DestDataset_'):
                    output_dir = line.split('{')[-1].split('}')[0].split()[-1]

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
                            print('Invalid directory %s' %(output_dir))

        log.debug('Features: %s' % features)

        execute_params = workbench_path + parameters

        # Run workbench
        log.info('Running %s %s' %(self.app.fme, execute_params))
        self.execute = subprocess.Popen("%s %s" %(self.app.fme, execute_params), shell=False) #, stdout=subprocess.PIPE
        log.debug('Run PID: %s' % self.execute.pid)
        self.execute.wait()

        # Create Log Counts
        error = False
        workbench_counts = OrderedDict()
        #for line in f.readlines():
        logfile = os.path.join(self.repository['location'], '%s.log' %workbench.split('.')[0])
        if os.path.exists(logfile):
            with open(logfile) as f:
                for line in f.readlines():
                    if string.count(line,'|STATS |'):
                        for feature in features:

                            if string.count(line,'|STATS |%s ' %(feature)):
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
        self.status(status='Running', counts=workbench_counts)

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
            log.info('Completed %s' %(workbench))
            return



    def run(self):
        """
        """
        self.status(status='Running')

        status = ''

        try:
            for workbench in self.workbenches:
                workbench = eval(workbench)
                # Check if the Kill command issued
                if self.terminate:
                    return 'Terminated'

                log.debug(workbench)
                parameters = ' '
                for parameter in workbench['parameters']:
                    parameters += '--%s "%s"' %(parameter['name'], parameter['value'])

                ## Check if workbench exists
                workbench_path = os.path.join(self.repository['location'], workbench['name'])
                if os.path.exists(workbench_path):
                    status = self.run_workbench(workbench['name'], parameters)
                else:
                    log.error('Unable to locate %s' %(workbench['name']))
                    status = 'Unable to locate %s' %(workbench['name'])

        except Exception as e:
            log.error(e, exc_info=True)
            status = e

        ## Store which workbenches failed
        if status:
            log.error('%s %s' %(workbench['name'], status))
            self.status(status='Failed', error='Failed - %s' %(status))
            return #workbench['name'] + ' ' + status
        elif self.terminate:
            self.status(status='Failed', error='Terminated')
            return
        else:
            self.status(status='Completed')
            return



    @property
    def counts(self):
        return self._counts
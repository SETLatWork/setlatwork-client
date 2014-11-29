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

    def __init__(self, data, app):
        self.app = app

        try:
            self.job = data[0]['job']
            #self.repository = data[0]['repository']
            #self.workbenches = data[0]['workbenches']
        except:
            #print 'Failed to decode data\n'
            logging.error('Failed to decode data', exc_info=True)
            logging.debug('job: %s' % job)
            logging.debug('repository: %s' % repository)
            logging.debug('workbenches: %s' % workbenches)
            self.error = 'Failed to decode data'
            self.status(status='Failed')

        self._counts = OrderedDict()
        self.terminate = False
        self.error = None
        self.execute = None

        self.supply_info['supply_root_dir'] = r"\\ZOOT\DES\Data_Supplies\Deliveries"
        self.supply_info['output_root_dir'] = r"D:\DATA_EXTRACTS"

        self.supply_info['supply']['dir_name_lc'] = self.supply_info['supply']['dir_name'].lower()
        self.supply_info['log_date'] = self.log_date = datetime.datetime.now().strftime("%Y%m")
        #self.supply_info['client_dir'] = self.client_dir = "L:\\Data_Supplies\\Deliveries\\%s\\%s\\Scripts" %(self.supply_info['category'], self.supply_info['supply']['dir_name'])
        self.supply_info['client_dir'] = self.client_dir = "%s\\%s\\%s\\Scripts" %(self.supply_info['supply_root_dir'], self.supply_info['category'], self.supply_info['supply']['dir_name'])
        #self.supply_info['output_dir'] = self.output_dir = "D:\\DATA_EXTRACTS\\%s\\%s" %(self.supply_info['supply']['dir_name'], self.supply_info['supply']['dir_name'])
        self.supply_info['output_dir'] = self.output_dir = "%s\\%s\\%s" %(self.supply_info['output_root_dir'], self.supply_info['supply']['dir_name'], self.supply_info['supply']['dir_name'])

    def write(self, txt, main=1):
        """
        Previously used to write to Text Area in GUI implementation.
        """
        print txt


    def kill(self):
        """
        Set the supply to self terminate.
        """
        try:
            print 'Delete PID:' , self.execute.pid
            self.execute.terminate()
        except:
            logging.error('Failed to terminate workbench - supply will terminate on completion')

        self.terminate = True
        self.error = 'Terminated'


    def status(self, status, counts=None):
        """
        Send Supply status to the web-server

        parameters
        ----------
        Status:
            String - Running, Completed, Error
        Counts:
            Dict - key=feature name, value=count value
        """
        import socket
        svcUrl = "%s/init/default/queue" % self.app.weburl
        params = {
            'job':self.supply_info['job'],
            'supply':self.supply_info['supply']['id'],
            'status':status,
            'server':socket.gethostname(),
            'counts':counts,
            'error':self.error
        }

        logging.debug('Supply.status: %s' %(params))

        self.write('\n')
        self.write('Supply Update')
        self.write('-------------------------')
        self.write('URL:       %s' % svcUrl)
        self.write('job:       %s' % self.supply_info['job'])
        self.write('supply:    %s' % self.supply_info['supply']['id'])
        self.write('status:    %s' % status)
        self.write('server:    %s' % socket.gethostname())
        self.write('counts:    %s' % counts) #self._counts,
        self.write('error:     %s' % self.error)
        self.write('-------------------------')
        try:
            urllib2.urlopen(svcUrl, urllib.urlencode(params))
        except:
            #print params
            self.write('SUPPLY ERROR - Unable to connect to web server')



    def run_workbench(self, workbench, parameters=None):
        """
        Run a workbench with the given parameters

        Parameters
        ----------
        workbench:
            string - the name of the workbench to be run.
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

        #f = open('%s/Workbenches/%s' %(self.supply_info['client_dir'], workbench))
        with open('%s/Workbenches/%s' %(self.supply_info['client_dir'], workbench)) as f:
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
                            self.write('test1 ' + line.split('{')[-1].split('}')[0])

                    # Check if data is output to D:\ location
                    elif 'D:\\' in output_dir:
                        if not os.path.exists('\\'.join(output_dir.split('\\')[0:-1])):
                            self.write('Creating Directory: ' + '\\'.join(output_dir.split('\\')[0:-1]))
                            os.makedirs('\\'.join(output_dir.split('\\')[0:-1]))

                    # If output to ORACLE do nothing
                    elif 'ORACLE' in output_dir:
                        pass

                    # Otherwise not setup to handle so output to screen.
                    else:
                        if not 'puts {' in line:
                            self.write('Invalid directory %s' %(output_dir))
        #f.close()

        logging.debug('Features: %s' % features)

        ## Set Logfile Destination
        log_filename = '%s_%s.log' %(self.supply_info['log_date'], workbench.split('.')[0])
        log_file = ' --LogFile %s/Logs/%s' %(self.supply_info['client_dir'], log_filename)
        workbench_file = '%s/Workbenches/%s' %(self.supply_info['client_dir'], workbench)
        workbench_params = workbench_file + parameters + log_file

        ######################################
        ## Run Workbench
        logging.info('Running %s' %(workbench))
        self.execute = subprocess.Popen("%s %s" %(self.fme, workbench_params), shell=False) #, stdout=subprocess.PIPE
        print 'Run PID:' , self.execute.pid
        self.execute.wait()
        #print self.execute.stdout.read()


        #####################################
        ## Create Dict of Log Counts
        error = False
        #try:
        #   f = open('%s/Logs/%s' %(self.supply_info['client_dir'],log_filename))
        #except IOError:
        #   self.write('Log file not found')
        #   return 'Log file not found'

        workbench_counts = OrderedDict()
        #for line in f.readlines():
        with open('%s/Logs/%s' %(self.supply_info['client_dir'],log_filename)) as f:
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
                    logging.critical(line)
                    self.write(line.split('|')[-1].strip())
                    error = True

        #f.close()

        self._counts.update(workbench_counts)

        ##################################
        ## Return Result
        self.status(status='Running', counts=workbench_counts)

        if self.terminate == True:
            return
        elif self.supply_info['format']['format'] == 'GEOTIFF':
            return
        elif error or len(workbench_counts) == 0:
            return 'Error - no features were written.'
        else:
            self.write('|=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
            self.write('|                           Features Written Summary')
            self.write('|=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
            for feature, count in workbench_counts.items():
                try:
                    self.write('|{0:29s}                                     {1:9d}'.format(feature, int(count)))
                except:
                    self.write('|{0}                                             {1}'.format(feature, count))
            self.write('|==============================================================================')
            self.write('Completed %s' %(workbench))
            return


    def run_mastermap(self):
        """
        Run CRS & TIL workbenches
        """

        result = []
        print self.workbenches
        workbenches = []
        try:
            workbenches = filter(lambda x: 'type' in x.keys() and x['type'] in ['CRS','TIL','Raster'], self.workbenches)
        except Exception as e:
            print 'Error: ' , e
            print 'Workbenches: ' , self.workbenches

            for workbench in self.workbenches:
                workbenches.append(eval(workbench))

            workbenches = filter(lambda x: 'type' in x.keys() and x['type'] in ['CRS','TIL','Raster'], workbenches)

        for workbench in workbenches:

            # Check if the Kill command issued
            if self.terminate:
                return 'Terminated'

            parameters = ' --MinX %s --MinY %s --MaxX %s --MaxY %s --DataProj %s' %(self.params['minx'], self.params['miny'], self.params['maxx'], self.params['maxy'], self.params['projection'])

            ## Check for generically named clipper
            if os.path.exists('%s/Clippers/client_area.shp' %(self.supply_info['client_dir'])):
                parameters += ' --ClientArea %s/Clippers/client_area.shp' %(self.supply_info['client_dir'])

            if not os.path.exists('%s/Logs' %(self.supply_info['client_dir'])):
                os.makedirs('%s/Logs' %(self.supply_info['client_dir']))

            ## Add datadest to parameters
            parameters += ' --DataDest %s/%s' %(self.supply_info['output_dir'], workbench['file'].split('/')[2])

            ## The file is stored (e.g. Annual/Wellington_CC/CRS/1_POINTS.fmw) with additional parameters
            ## so take the last one in the list.
            workbench = workbench['file'].split('/')[-1]

            ## Check if workbench exists
            if os.path.exists('%s/Workbenches/%s' %(self.supply_info['client_dir'], workbench)):
                status = self.run_workbench(workbench, parameters)
            else:
                self.write('Unable to locate %s' %(workbench))
                status = 'Unable to locate %s' %(workbench)

            ## Store which workbenches failed
            if status:
                result = workbench + ' ' + status
                return result
            elif self.terminate:
                return

        return result


    def run(self):
        """
        Runs different aspects of the supply object
        depending on what the client is setup to receive.
        """

        self.status(status='Running')

        message = ''
        result = []
        if len(self.workbenches) > 0:
            try:
                if not self.supply_info['rerun']:
                    self.run_prep()

                result = self.run_mastermap()
            except Exception as e:
                result = e
        else:
            result = 'No workbenches found'


        if not self.error or not self.terminate:
            if self.supply_info['format']['format'] in ['ORACLE8I', 'ORACLE']: # 'GEODATABASE_FILE', 'GEODATABASE_MDB',
                try:
                    import qa
                    qa_counts = qa.QA(self.supply_info, self._counts)
                    self.physical_counts = qa_counts.run()
                    self.write('Physical Counts: %s' %(self.physical_counts))
                    self._counts = self.physical_counts
                except Exception as e:
                    result = e


        if result:
            message = 'Failed - %s' %(result)
        elif self.terminate:
            message = 'Terminated'

        if message:
            self.error = message
            self.status(status='Failed')
            self.write('%s Failed: %s' %(self.supply_info['supply']['dir_name'], message))
        else:
            self.status(status='Completed')
            self.write('%s Succeeded' %(self.supply_info['supply']['dir_name']))


        return


    @property
    def counts(self):
        return self._counts
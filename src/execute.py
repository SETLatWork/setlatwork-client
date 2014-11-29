# -*- coding: iso-8859-1 -*-
import logging

class Execute():

	def __init__(self):
		pass

	def kill(self):
		"""
		KILL
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
		STATUS
		Send Supply status to the web-server
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


	def run(self):
		"""
		RUN
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
			try:
				if self.supply_info['supply']['terramatch'] == 'Titles':
					result = self.run_titles()
				elif self.supply_info['supply']['terramatch'] == 'EMS':
					result = self.run_ems()
				elif self.supply_info['supply']['terramatch'] != 'None':
					result = self.run_terramatch()
			except Exception as e:
				result = e

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
			#self.zip()
			if self.supply_info['supply']['incremental'] and not self.supply_info['rerun']:
				self.incremental_tidy_up()
		
		return
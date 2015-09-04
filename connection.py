from pydarn.sdio import beamData, scanData
import logging
from twisted.internet import reactor, protocol
from twisted.internet.protocol import ReconnectingClientFactory
import json
import os, errno

from rtiJS import plotRti
from geoJS import plotFan
from fgpJS import plotFgpJson

import sys 
sys.path.append('~/davitpy')
import datetime,pytz
import numpy as np

import pydarn
from pydarn.proc.music import getDataSet

'''
ProcessData(self)
clears figure, calls graphing method, saves figure

'''
def processData(self):
	logging.info('Updating Geographic Plot')
	for i in range(len(self.parent.geo['figure'])):
		try:
			t1 = datetime.datetime.now()
			self.parent.geo['figure'][i].clf()
			logging.info('Time clearing Geo figure')
			logging.info(datetime.datetime.now()-t1)

			self.parent.geo['figure'][i] =plotFan(self.parent.myScan,[self.parent.rad],
				param=self.parent.geo['param'][i],
				gsct=self.parent.geo['gsct'], 
				maxbeams = int(self.parent.maxbeam[0]),
				maxgates=int(self.parent.nrangs[0]),	
				scale=self.parent.geo['sc'][i],
				drawEdge = self.parent.geo['drawEdge'], 
				gridColor = self.parent.geo['gridColor'],
				backgColor = self.parent.geo['backgColor'],
				continentColor = self.parent.geo['continentColor'],
				continentBorder = self.parent.geo['continentBorder'],
				waterColor = self.parent.geo['waterColor'],
				merColor = self.parent.geo['merColor'],
				merGrid = self.parent.geo['merGrid'],
				figure = self.parent.geo['figure'][i],
				bmnum = self.parent.myBeam.bmnum,
				tfreq = self.parent.myBeam.prm.tfreq,
				noise = self.parent.myBeam.prm.noisesearch,
				rTime=self.parent.myBeam.time,
				title = self.parent.names[0])
			t1 = datetime.datetime.now()
			self.parent.geo['figure'][i].savefig(self.parent.filepath[0]+'geo_'+self.parent.geo['param'][i])
			logging.info('Time saving Geo figure')
			logging.info(datetime.datetime.now()-t1)
		except:
			logging.debug("Error in Geo Plot:",sys.exc_info()[0].__str__())
	logging.info('Updating Fan Plot')
	for i in range(len(self.parent.fan['figure'])):
		try:
			self.parent.fan['figure'][i].clf()
			self.parent.fan['figure'][i]=plotFgpJson(self.parent.myScan,self.parent.rad,
				params=[self.parent.fan['param'][i]],
				gsct=self.parent.fan['gsct'],scales=[self.parent.fan['sc'][i]],
				bmnum = self.parent.myBeam.bmnum,figure = self.parent.fan['figure'][i],
				tfreq = self.parent.myBeam.prm.tfreq,
				noise = self.parent.myBeam.prm.noisesearch,
				rTime=self.parent.myBeam.time,
				title = self.parent.names[0])
			t1 = datetime.datetime.now()
			self.parent.fan['figure'][i].savefig(self.parent.filepath[0]+'fan_'+self.parent.fan['param'][i])
			logging.info('Time saving Fan figure')
			logging.info(datetime.datetime.now()-t1)
		except:
			logging.debug("Error in Fan Plot:",sys.exc_info()[0].__str__())
	#Must wait till the beam list is long enough to work
	if len(self.parent.myBeamList)>2:
		try:
			self.parent.time['figure'].clf()
			logging.info('Updating Time Plot')
			self.parent.time['figure']=plotRti(self.parent.myBeamList,self.parent.rad,
				params=self.parent.time['param'],scales=self.parent.time['sc'],
				gsct=self.parent.time['gsct'],bmnum = int(self.parent.beams[0]),
				figure = self.parent.time['figure'],rTime = self.parent.myBeam.time,
				title = self.parent.names[0])
			t1= datetime.datetime.now()
			self.parent.time['figure'].savefig(self.parent.filepath[0]+'time')
			logging.info('Time saving Time figure')
			logging.info(datetime.datetime.now()-t1)
		except:
			logging.debug("Error in Time Plot:",sys.exc_info()[0].__str__())
		
class EchoClient(protocol.Protocol):
	#initializes variables in the connection
    def connectionMade(self):
    	logging.info('Connected')
    	self.data = ''
    	parent.i = 1
    	self.incom = False
    	self.parent = parent
    	self.endP = True
    	logging.info('Connection Open')
        self.transport.registerProducer(self.transport, streaming=True)
    '''    
    Built in Twisted method overwritten:
    Recieves data parses apart each packet and updates Scan data
    '''
    def dataReceived(self, data):
    	
		def processMsg(self):
			#print 'Msg:', self.data
			#json loads the data
			msg = json.loads(self.data)
			dic = json.loads(msg.pop())
			if 'origin' in dic:
				#prm data update
				self.parent.myBeam = beamData()
				self.parent.myBeam.updateValsFromDict(dic)
				self.parent.myBeam.prm.updateValsFromDict(dic)
				self.endP = False
				
			elif 'rng' in dic:
				#fit data update and param noisesky
				self.parent.myBeam.fit.updateValsFromDict(dic)
				self.parent.myBeam.prm.noisesky = dic['noise']['skynoise']
				parent.timeNow = datetime.datetime.today()
				
				
				#updates time to a datetime string
				time = parent.myBeam.time
				self.parent.myBeam.time = datetime.datetime(time['yr'],time['mo'],\
					time['dy'],time['hr'],time['mt'],time['sc'])
				
				#inserts removes and inserts new beam data
				self.parent.myScan.pop(parent.myBeam.bmnum)
				self.parent.myScan.insert(parent.myBeam.bmnum,parent.myBeam)
				logging.info('Proccessing packet: '+str(parent.i))
				self.parent.i = self.parent.i+1
				self.endP = True
				
				#adds beam data to the Beam list only the specified beam number
				#for the time plot which only plots a single beam
				if self.parent.myBeam.bmnum == int(self.parent.beams[0]):
					self.parent.myBeamList.append(self.parent.myBeam)
				
						
		#As soon as any data is received, write it back.
		if self.endP:
			indS = data.find('["{\\"origin')
			indF = data.find('}"]')
		else:
			indS = data.find('["{')
			indF = data.find('}"]')
		#This parses each packet...
		#overly complicated but for the moment it works
		while(indS != -1 or indF != -1):
			if self.incom:
				indS = data.find('["{')
				indF = data.find('}"]')
				#print 'Incomplete Data:', data
				#print 'IndS: ',indS,'IndF: ',indF
				if indS != -1 and indS < indF:
					self.data = data[indS:indF+3]
					data = data[indF+3:]
					try:
						processMsg(self)
					except:
						logging.debug("Error:",sys.exc_info()[0].__str__())
					self.data = ''
					self.incom = False
				elif indF != -1:
					self.data = self.data + data[:indF+3]
					try:
						processMsg(self)
					except:
						logging.debug("Error:",sys.exc_info()[0].__str__())
					self.data = ''
					data = data[indF+3:]
					self.incom = False
				elif indS != -1:
					self.incom = True
					self.data = data[indS:]
					data = ''
				else:
					self.incom = True
					self.data = self.data+data
					data = ''
			else:
				if self.endP:
					indS = data.find('["{\\"origin')
					indF = data.find('}"]')
				else:
					indS = data.find('["{')
					indF = data.find('}"]')
				#print 'Data:', data
				#print 'IndS: ',indS, 'IndF: ',indF
				if indS != -1 and indF != -1:
					self.data = data[indS:indF+3]
					data = data[indF+3:]
					try:
						processMsg(self)
					except:
						logging.debug("Error:",exc_info()[0].__str__())
					self.data = ''
					indS = data.find('["{')
					indF = data.find('}"]')
					self.incom = False
					if indS != -1 and indF != -1:
						self.data = data[indS:indF+3]
						try:
							processMsg(self)
						except:
							logging.debug("Error:",sys.exc_info()[0].__str__())
						self.data = ''
						data = data[indF+3:]
						self.incom = False
					else:
						self.incom = True
						self.data = data[indS:]
						data = ''
				else:
					self.incom = True
					self.data = data[indS:]
					data = ''
			indS = data.find('["{\\"origin')
			indF = data.find('}"]')
		if self.endP:
			processData(self)
    def connectionLost(self, reason):
    	logging.info("Connection Lost")

'''
Handles lost server connections
Will exponentially try to reconnect to the server
Also removes and replaces saved figure with a lost connection identifier
creates new data array for everything except time data

'''
class EchoFactory(protocol.ReconnectingClientFactory):
	protocol = EchoClient
    
	def clientConnectionFailed(self, connector, reason):
		logging.debug("Connection failed - goodbye!")
		logging.debug('Closed Connection')
		createData(self)
		parent.myScan = self.myScan
		for pr in parent.fan['param']:
			silentRemove('fan_'+pr+'.png')
			silentRemove('geo_'+pr+'.png')
		silentRemove('time.png')
		ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)
    
	def clientConnectionLost(self, connector, reason):
		logging.debug("Connection lost - goodbye!")
		logging.debug('Closed Connection')
		createData(self)
		parent.myScan = self.myScan
		for pr in parent.fan['param']:
			silentRemove('fan_'+pr+'.png')
			silentRemove('geo_'+pr+'.png')
		silentRemove('time.png')
		ReconnectingClientFactory.clientConnectionLost(self, connector,
                                                         reason)

#connects server
def serverCon(self):
	global parent
	parent = self
	t_date = datetime.date.today()
	logging.basicConfig(filename='errlog/err_'+self.rad+\
		'_'+t_date.strftime('%Y%m%d'), level=logging.DEBUG, \
		format='%(asctime)s %(message)s')
	f = EchoFactory()
	reactor.connectTCP(self.hosts[0], int(self.ports[0]), f)
	reactor.run(installSignalHandlers=0)

#disconnects from the server currently never called
def disconnect(self):
	logging.info('Closed Connection')
	parent.i=1
	reactor.stop()
	disconnect(self)

#Clears figure and replaces with text indicating lost connection
def silentRemove(filename):
	for fanFig in parent.fan['figure']:
		fanFig.clf()
		fanFig.text(0.5,0.5,'Lost Connection',backgroundcolor='r',
			size='x-large',style='oblique',ha='center',va='center')
		fanFig.savefig(parent.filepath[0]+filename)

#creates a new data set
def createData(self):
	self.myScan = scanData()
	#only called near midnight contains time plot data
	for i in range(0, int(parent.maxbeam[0])):
		myBeam = beamData()
		today = datetime.datetime.utcnow()
		today = today.replace(tzinfo=pytz.utc)	
		myBeam.time= today
		myBeam.bmnum = i
		myBeam.prm.nrang = int(parent.nrangs[0])
		if i == 0:
			self.myBeam = myBeam
		self.myScan.append(myBeam)



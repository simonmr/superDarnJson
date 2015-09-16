from pydarn.sdio import beamData, scanData
import logging
from twisted.internet import reactor, protocol
from twisted.internet.protocol import ReconnectingClientFactory
import json
import os, errno
from rtiJS import plotRti
from geoJS import plotFan
from fgpJS import plotFgpJson
import matplotlib.pyplot as plot
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
	if self.parent.myBeam.prm.noisesearch is None:
		self.parent.myBeam.prm.noisesearch = 0
	for i in range(len(self.parent.geo['figure'])):
		try:
			self.parent.geo['figure'][i].clf()
			self.parent.geo['figure'][i] =plotFan(self.parent.myScan,[self.parent.rad],
				fovs = self.parent.fovs,
				param=self.parent.geo['param'][i],
				gsct=self.parent.geo['gsct'], 
				maxbeams = int(self.parent.maxbeam[0]),
				maxgates=int(self.parent.nrangs[0]),	
				scale=self.parent.geo['sc'][i],
				drawEdge = self.parent.geo['drawEdge'], 
				myFig = self.parent.geo['figure'][i],
				bmnum = self.parent.myBeam.bmnum,
				site = self.parent.site,
				tfreq = self.parent.myBeam.prm.tfreq,
				noise = self.parent.myBeam.prm.noisesearch,
				rTime=self.parent.myBeam.time,
				title = self.parent.names[0],
				dist = self.parent.dist,
				llcrnrlon = self.parent.llcrnrlon,
				llcrnrlat = self.parent.llcrnrlat,
				urcrnrlon = self.parent.urcrnrlon,
				urcrnrlat = self.parent.urcrnrlat,
				lon_0 = self.parent.lon_0,
				lat_0 = self.parent.lat_0,
				merGrid = self.parent.geo['merGrid'],
				merColor = self.parent.geo['merColor'],
				continentBorder = self.parent.geo['continentBorder'],
				waterColor = self.parent.geo['waterColor'],
				continentColor = self.parent.geo['continentColor'],
				backgColor = self.parent.geo['backgColor'],
				gridColor = self.parent.geo['gridColor'])
			self.parent.geo['figure'][i].savefig("%sgeo_%s" % (self.parent.filepath[0],self.parent.geo['param'][i]))
		except:
			print 'Geo Figure ',sys.exc_info()[0]
	logging.info('Updating Fan Plot')
	for i in range(len(self.parent.fan['figure'])):
		try:
			self.parent.fan['figure'][i].clf()
			self.parent.fan['figure'][i]=plotFgpJson(self.parent.myScan,self.parent.rad,
				params=[self.parent.fan['param'][i]],
				gsct=self.parent.fan['gsct'],
				scales=[self.parent.fan['sc'][i]],
				bmnum = self.parent.myBeam.bmnum,
				figure = self.parent.fan['figure'][i],
				tfreq = self.parent.myBeam.prm.tfreq,
				noise = self.parent.myBeam.prm.noisesearch,
				rTime=self.parent.myBeam.time,
				title = self.parent.names[0])
			self.parent.fan['figure'][i].savefig("%sfan_%s" % (self.parent.filepath[0],self.parent.fan['param'][i]))
		except:
			print 'Fan Figure ',sys.exc_info()[0]
	#Must wait till the beam list is long enough to work
	if len(self.parent.myBeamList)>2:
		try:
			self.parent.time['figure'].clf()
			logging.info('Updating Time Plot')
			self.parent.time['figure']=plotRti(self.parent.myBeamList,
				self.parent.rad,
				params=self.parent.time['param'],
				scales=self.parent.time['sc'],
				gsct=self.parent.time['gsct'],
				bmnum = int(self.parent.beams[0]),
				figure = self.parent.time['figure'],
				rTime = self.parent.myBeam.time,
				title = self.parent.names[0])
			self.parent.time['figure'].savefig("%stime" % (self.parent.filepath[0]))
		except:
			print 'Time Figure ',sys.exc_info()[0]			
class EchoClient(protocol.Protocol):
	#initializes variables in the connection
    def connectionMade(self):
    	logging.info('Connected')
    	self.data = ''
    	parent.i = 1
    	self.incom = False
    	self.parent = parent
    	self.first = True
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
				logging.info("Proccessing packet: %s" % (str(parent.i)))
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
						print '1:',sys.exc_info()[0]
					self.data = ''
					self.incom = False
				elif indF != -1:
					self.data = self.data + data[:indF+3]
					try:
						processMsg(self)
					except:
						print '2:',sys.exc_info()[0]
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
						print '3:',sys.exc_info()[0]
					self.data = ''
					indS = data.find('["{')
					indF = data.find('}"]')
					self.incom = False
					if indS != -1 and indF != -1:
						self.data = data[indS:indF+3]
						try:
							processMsg(self)
						except:
							print '4:',sys.exc_info()[0]
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
			silentRemove("fan_%s.png" % (pr))
			silentRemove("geo_%s.png" % (pr))
		silentRemove('time.png')
		self.first = True
		ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)
    
	def clientConnectionLost(self, connector, reason):
		logging.debug("Connection lost - goodbye!")
		logging.debug('Closed Connection')
		createData(self)
		parent.myScan = self.myScan
		for pr in parent.fan['param']:
			silentRemove("fan_%s.png" % (pr))
			silentRemove("geo_%s.png" % (pr))
		silentRemove('time.png')
		self.first = True
		ReconnectingClientFactory.clientConnectionLost(self, connector,reason)

#connects server
def serverCon(self):
	global parent
	parent = self
	t_date = datetime.date.today()
	logging.basicConfig(filename="errlog/err_%s_%s"\
		% (self.rad,t_date.strftime('%Y%m%d')), level=logging.DEBUG, \
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
		fanFig.savefig("%s%s" % (parent.filepath[0],filename))

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



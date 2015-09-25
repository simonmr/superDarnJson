from pydarn.sdio import beamData, scanData
import logging
from twisted.internet import reactor, protocol, threads, defer
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver
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
import utils
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
			self.parent.geo['figure'][i] = plotFan(self.parent.myScan,[self.parent.rad],
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
			self.no_err = False
			logging.error('geographic plot missing info')
			print 'Geo Figure ',sys.exc_info()[0]
			break
	if self.no_err:
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
				logging.error('fan plot missing info')
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
				logging.error('time plot missing info')
				print 'Time Figure ',sys.exc_info()[0]
				
				

def processMsg(self):
	self.no_err = True
	#print 'Msg:', self.data
	#json loads the data
	msg = json.loads(self.data)
	dic = json.loads(msg.pop())
	if 'origin' in dic:
		#prm data update
		self.parent.myBeam = beamData()
		self.parent.myBeam.updateValsFromDict(dic)
		self.parent.myBeam.prm.updateValsFromDict(dic)
		if self.parent.myBeam.prm.rsep != self.parent.site.rsep:
			logging.info('Difference in rsep',str(self.parent.site.rsep),' : ',str(self.parent.myBeam.prm.rsep))
			self.parent.site.rsep = self.parent.myBeam.prm.rsep
			createData(self)
			
		self.endP = False
		
	elif 'rng' in dic:
		#fit data update and param noisesky
		self.parent.myBeam.fit.updateValsFromDict(dic)
		self.parent.myBeam.prm.noisesky = dic['noise']['skynoise']
		self.parent.timeNow = datetime.datetime.today()
		
		
		#updates time to a datetime string
		time = self.parent.myBeam.time
		self.parent.myBeam.time = datetime.datetime(time['yr'],time['mo'],\
			time['dy'],time['hr'],time['mt'],time['sc'])
		
		#inserts removes and inserts new beam data
		self.parent.myScan.pop(self.parent.myBeam.bmnum)
		self.parent.myScan.insert(self.parent.myBeam.bmnum,self.parent.myBeam)
		logging.info("Proccessing packet: %s" % (str(self.parent.i)))
		self.parent.i = self.parent.i+1
		self.endP = True
		
		#adds beam data to the Beam list only the specified beam number
		#for the time plot which only plots a single beam
		if self.parent.myBeam.bmnum == int(self.parent.beams[0]):
			self.parent.myBeamList.append(self.parent.myBeam)
				
def incommingData(self,data):						
	#As soon as any data is received, write it back.
	indS = data.find('["{')
	indF = data.find('}"]')
	if indS != -1 and indF != -1:
		self.data = data[indS:indF+3]
		data = data[indF+3:]
		#print 'In 1'
		self.comp = True
	elif indF != -1:
		self.data = self.data + data[:indF+3]
		data = data[indF+3:]
		#print 'In 2'
		self.comp = True
	elif indS != -1:
		self.data = data[indS:]
	else:
		self.data = self.data + data
		#print 'In else'
	if self.comp:
		#print 'Full data: ',self.data
		try:
			processMsg(self)
		except:
			print 'Incomming Data ',sys.exc_info()[0]
			print 'Data ',self.data
			self.errorCount = self.errorCount + 1
			logging.error('Error in Data: '+str(self.errorCount))
		indS = data.find('["{')
		if indS != -1:
			self.data = data[indS:]
		else:
			self.data = data
		self.comp = False

	if self.endP:
		processData(self)
		
class EchoClient(protocol.Protocol):
    def connectionMade(self):
    	self.parent = self.factory.parent
    	logging.info('Connected')
    	self.data = ''
    	self.parent.i = 1
    	self.errorCount = 0
    	self.comp = False
    	self.no_err = True
    	self.endP = True
    	logging.info('Connection Open')
        self.transport.registerProducer(self.transport, streaming=True)

    '''    
    Built in Twisted method overwritten:
    Recieves data parses apart each packet and updates Scan data
    '''
    def dataReceived(self, data):
    	incommingData(self,data)
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
	def __init__(self,parent):
		self.parent = parent
	

	def clientConnectionFailed(self, connector, reason):
		logging.debug("Connection failed - goodbye!")
		logging.debug('Closed Connection')
		createData(self)
		for pr in self.parent.fan['param']:
			silentRemove(self,"fan_%s.png" % (pr))
			silentRemove(self,"geo_%s.png" % (pr))
		silentRemove(self,'time.png')
		self.first = True
		ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)
    
	def clientConnectionLost(self, connector, reason):
		logging.debug("Connection lost - goodbye!")
		logging.debug('Closed Connection')
		createData(self)
		for pr in self.parent.fan['param']:
			silentRemove(self,"fan_%s.png" % (pr))
			silentRemove(self,"geo_%s.png" % (pr))
		silentRemove(self,'time.png')
		self.first = True
		ReconnectingClientFactory.clientConnectionLost(self, connector,reason)

#connects server
def serverCon(self):
	t_date = datetime.date.today()
	logging.basicConfig(filename="errlog/err_%s_%s"\
		% (self.rad,t_date.strftime('%Y%m%d')), level=logging.DEBUG, \
		format='%(asctime)s %(message)s')
	f = EchoFactory(self)
	f.parent = self
	reactor.connectTCP(self.hosts[0], int(self.ports[0]), f)
	reactor.run(installSignalHandlers=0)

#disconnects from the server currently never called
def disconnect(self):
	logging.info('Closed Connection')
	parent.i=1
	reactor.stop()


#Clears figure and replaces with text indicating lost connection
def silentRemove(self,filename):
	for fanFig in self.parent.fan['figure']:
		fanFig.clf()
		fanFig.text(0.5,0.5,'Lost Connection',backgroundcolor='r',
			size='x-large',style='oblique',ha='center',va='center')
		fanFig.savefig("%s%s" % (self.parent.filepath[0],filename))

#creates a new data set
def createData(self):
	self.myScan = scanData()
	#only called near midnight contains time plot data
	for i in range(0, int(self.parent.maxbeam[0])):
		myBeam = beamData()
		today = datetime.datetime.utcnow()
		today = today.replace(tzinfo=pytz.utc)	
		myBeam.time= today
		myBeam.bmnum = i
		myBeam.prm.nrang = int(self.parent.nrangs[0])
		if i == 0:
			self.myBeam = myBeam
		self.myScan.append(myBeam)
	self.parent.site.tval = datetime.datetime.utcnow()
	self.parent.llcrnrlon,self.parent.llcrnrlat,self.parent.urcrnrlon,self.parent.urcrnrlat,self.parent.lon_0, \
	self.parent.lat_0, self.parent.fovs,self.parent.dist = utils.plotUtils.geoLoc(self.parent.site,
		int(self.parent.nrangs[0]),self.parent.site.rsep,
		int(self.parent.maxbeam[0]))



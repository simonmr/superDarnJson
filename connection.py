from pydarn.sdio import beamData, scanData
import logging
from twisted.internet import reactor, protocol
from twisted.internet.protocol import ClientFactory
import json
from Queue import Queue 
from threading import Event, Thread
from rtiJS import plotRti
from geoJS import plotFan
from fgpJS import plotFgpJson
import matplotlib.pyplot as plot
import sys,datetime,pytz
sys.path.append('~/davitpy')
from utils import plotUtils,mapObj
import time
from pydarn.proc.music import getDataSet

'''
ProcessData(self)
clears figure, calls graphing method, saves figure

'''

class geoThread(Thread):
	
	def __init__(self, parent,data,timeQue):
		super(geoThread, self).__init__()
		self.parent = parent
		self.data = data
		self.tq = timeQue
		self.oldCpid = -9999999999
		self.maxgates = int(self.parent.nrangs[0])
		
		self.stoprequest = Event()
	
	def run(self):
		
		while not self.data.empty():
			myScan = self.data.get(True, 0.1)
			for mb in myScan:
				myBeam = beamData()
				myBeam = mb
				break
		while not self.stoprequest.isSet():
			time.sleep(1)
			timeNow = datetime.datetime.utcnow()
			myBeam.time = myBeam.time.replace(tzinfo=None)	
			tdif = timeNow - myBeam.time
			if tdif.seconds > 360:
				try:
					reactor.stop()
				except:
					logging.error('Reactor already stopped')
				self.tq.put(0)
				logging.error('Geo thread stopped')
				for pr in self.parent.fan['param']:
					silentRemove(self,"fan_%s.png" % (pr))
					silentRemove(self,"geo_%s.png" % (pr))
				silentRemove(self,'time.png')
				self.stoprequest.set()
				break
			while not self.data.empty():
				myBeam = beamData()
				myBeam = self.data.get()
				if myBeam.cp != self.oldCpid:
					self.oldCpid = myBeam.cp
					self.parent.maxbm = self.parent.maxbeam[0]
				if myBeam.prm.nrang != self.maxgates:
					print 'Changing Gates'
					self.maxgates = myBeam.prm.nrang
					self.parent.lon_0,self.parent.lat_0, self.parent.fovs,\
					self.parent.dist, self.parent.height,self.parent.width = plotUtils.geoLoc(self.parent.site,\
						self.maxgates,self.parent.site.rsep,\
						int(self.parent.maxbm))
					self.parent.myMap = mapObj(coords='geo', projection='stere',\
						lat_0=self.parent.lat_0, lon_0=self.parent.lon_0,\
						width= self.parent.width*1.3,height = self.parent.height*1.3,\
						grid =True,lineColor='0.75')
				if myBeam.bmnum >= len(myScan):
					bmnum = len(myScan)
					while bmnum > len(myScan):
						time.sleep(0.1)
						tmp_myBeam = beamData()
						tmp_myBeam.bmnum = bmnum
						tmp_myBeam.time = timeNow.replace(tzinfo=None)
						myScan.append(tmp_myBeam)
						print tmp_myBeam
						bmnum += 1
					myScan.append(myBeam)
					self.parent.maxbm = myBeam.bmnum+1
					self.parent.lon_0,self.parent.lat_0, self.parent.fovs,\
					self.parent.dist, self.parent.height,self.parent.width = plotUtils.geoLoc(self.parent.site,\
						self.maxgates,self.parent.site.rsep,\
						int(self.parent.maxbm))
					self.parent.myMap = mapObj(coords='geo', projection='stere',\
						lat_0=self.parent.lat_0, lon_0=self.parent.lon_0,\
						width= self.parent.width*1.3,height = self.parent.height*1.3,\
						anchor = 'N',grid =True,lineColor='0.75')
				else:
					myScan.pop(myBeam.bmnum)
					myScan.insert(myBeam.bmnum,myBeam)
			
		
			try:
				self.parent.geo['figure'] = plotFan(myScan,[self.parent.rad],
					fovs = self.parent.fovs,
					params=self.parent.geo['param'],
					gsct=self.parent.geo['gsct'], 
					maxbeams = int(self.parent.maxbm),
					maxgates=self.maxgates,	
					scales=self.parent.geo['sc'],
					drawEdge = self.parent.geo['drawEdge'], 
					myFigs = self.parent.geo['figure'],
					bmnum = myBeam.bmnum,
					site = self.parent.site,
					tfreq = myBeam.prm.tfreq,
					noise = myBeam.prm.noisesearch,
					rTime=myBeam.time,
					radN = self.parent.names[0],
					dist = self.parent.dist,
					lon_0 = self.parent.lon_0,
					lat_0 = self.parent.lat_0,
					merGrid = self.parent.geo['merGrid'],
					merColor = self.parent.geo['merColor'],
					continentBorder = self.parent.geo['continentBorder'],
					waterColor = self.parent.geo['waterColor'],
					continentColor = self.parent.geo['continentColor'],
					backgColor = self.parent.geo['backgColor'],
					gridColor = self.parent.geo['gridColor'],
					filepath = self.parent.filepath[0],
					myMap = self.parent.myMap)
			except:
				logging.error('geographic plot missing info')
				logging.error('Geo Figure: %s'%(sys.exc_info()[0]))

			for i in range(len(self.parent.fan['figure'])):
				time.sleep(1)
				try:
					self.parent.fan['figure'][i].clf()
					self.parent.fan['figure'][i]=plotFgpJson(myScan,self.parent.rad,
						params=[self.parent.fan['param'][i]],
						gsct=self.parent.fan['gsct'],
						scales=[self.parent.fan['sc'][i]],
						bmnum = myBeam.bmnum,
						figure = self.parent.fan['figure'][i],
						tfreq = myBeam.prm.tfreq,
						noise = myBeam.prm.noisesearch,
						rTime=myBeam.time,
						radN = self.parent.names[0])
					self.parent.fan['figure'][i].savefig("%sfan_%s" % (self.parent.filepath[0],self.parent.fan['param'][i]))
				except:
					logging.error('fan plot missing info')
					logging.error('Fan Figure: %s'%(sys.exc_info()[0]))

	def join(self, timeout=None):
		self.stoprequest.set()
		logging.info("Closing geoThread")
		super(geoThread, self).join(timeout)

class timeThread(Thread):
	
	def __init__(self, parent, data):
		super(timeThread, self).__init__()
		self.parent = parent
		self.data = data
		self.stoprequest = Event()
		self.oldDate = self.parent.day
	
	def run(self):
		myBeamList = scanData()
		while not self.data.empty():
			myBeamList = self.data.get(True, 0.01)
		while not self.stoprequest.isSet():
			time.sleep(20)

			while not self.data.empty():
				tmpB = self.data.get(True, 0.01)
				if tmpB == 0:
					try:
						reactor.stop()
					except:
						logging.error('Reactor already stopped')
					logging.error('Time thread stopped')
					self.stoprequest.set()
					sys.exit()
					break
				else:
					myBeam = beamData()
					myBeam = tmpB
				timeNow = datetime.datetime.utcnow()
				if self.oldDate != timeNow.day:
					myBeamList = scanData()
					self.oldDate = timeNow.day
				dFilenm = 'data/'+`timeNow.month`+`timeNow.day`+`timeNow.year`+'_'+self.parent.rad+self.parent.channels[0]
				
				with open(dFilenm,'a+') as f:
					fLine = `myBeam.stid`+';'+`myBeam.time`+';'+`myBeam.cp`+';'+`myBeam.prm.nave`+\
						';'+`myBeam.prm.noisesky`+';'+`myBeam.prm.rsep`+';'+`myBeam.prm.nrang`+\
						';'+`myBeam.prm.frang`+';'+`myBeam.prm.noisesearch`+';'+`myBeam.prm.tfreq`+\
						';'+`myBeam.fit.slist`+';'+`myBeam.prm.ifmode`+';'+`myBeam.fit.v`+';'+\
						`myBeam.fit.p_l`+';'+`myBeam.fit.w_l`+';'+`myBeam.fit.gflg`+'\n'
					f.write(fLine)
				f.close()
				myBeamList.append(myBeam)
				if len(myBeamList)>2:
					try:
						self.parent.time['figure'].clf()
						self.parent.time['figure']=plotRti(myBeamList,
								self.parent.rad,
								params=self.parent.time['param'],
								scales=self.parent.time['sc'],
								gsct=self.parent.time['gsct'],
								bmnum = int(self.parent.beams[0]),
								figure = self.parent.time['figure'],
								rTime = myBeam.time,
								title = self.parent.names[0],
								myFov = self.parent.fovs)
						self.parent.time['figure'].savefig("%stime" % (self.parent.filepath[0]))
					except:
						logging.error('time plot missing info')
						logging.error('Time Figure: %s' %(sys.exc_info()[0]))
	def join(self, timeout=None):
		self.stoprequest.set()
		logging.info("Closing timeThread")
		super(timeThread, self).join(timeout)
					


def processMsg(self):
    try:
        dic = json.loads(self.data)
    except ValueError:
        # errors out if we got multiple packets (race condition)
        # If we get more than one dictionary, just skip the whole thing
        # this shouldn't happen very often
        logging.info("Error decoding dictionary, skipping packet")
        return
    
    #prm data update
    self.parent.myBeam = beamData()
    self.parent.myBeam.updateValsFromDict(dic)
    self.parent.myBeam.prm.updateValsFromDict(dic)

    self.endP = False

    #fit data update and param noisesky
    self.parent.myBeam.fit.updateValsFromDict(dic)
    self.parent.myBeam.prm.noisesky = dic['noise.sky']



    #updates time to a datetime string
    self.parent.myBeam.time = datetime.datetime(dic['time.yr'],dic['time.mo'],\
    	dic['time.dy'],dic['time.hr'],dic['time.mt'],dic['time.sc']) 
    
    #inserts removes and inserts new beam data
    self.gque.put(self.parent.myBeam)
    if self.parent.myBeam.bmnum == int(self.parent.beams[0]):
        self.tque.put(self.parent.myBeam)
    logging.info("Proccessing packet: %s" % (str(self.parent.i)))
    self.parent.i = self.parent.i+1
    self.endP = True


def incommingData(self,data):	
    #As soon as any data is received, write it back.
    time.sleep(0.5)
    self.find = str.find
    start_count = self.data.count('["{')
    if start_count != 0:
        start_count -= 1
    i = 0
    self.data = data

    while i <= start_count:
    	time.sleep(0.5)
        indS = self.find(self.data,'{"')
        indF = self.find(self.data,']}')
        self.parseS = True
        if indS == -1 or indF == -1:
            if indS != -1:
                self.parseP = True
                indF = self.find(data,'}]')
            else:
                indS = self.find(data,'{"')
                indF = self.find(data,'}]')
            self.parseS = False
        if indF < indS:
            indF = -1;
        if indS != -1 and indF != -1:
            if self.parseS:
                if i == start_count:
                    self.data2 = self.data[indF+2:]+data
                else:
                    self.data2 = self.data[indF+2:]
                self.data = self.data[indS:indF+2]
            elif self.parseP:
                self.data = self.data[indS:] + data[:indF+2]
                data = data[indF+2:]
                self.parseP = False
            else:
                self.data = data[indS:indF+2]
                data = data[indF+2:]
            self.comp = True
        elif indF != -1:
            self.data = self.data + data[:indF+2]
            data = data[indF+2:]
            self.comp = True
        elif indS != -1:
            if self.parseP:
                self.data = self.data + data
                self.parseP = False
            else:
                self.data = data[indS:]
        else:
            self.data = self.data + data
        if self.comp:
            processMsg(self)
            if self.parseS:
                data = self.data[indF+2:]+data
                self.parseS = False
            indS = self.find(data,'{"')
            if indS != -1:
                self.data = data[indS:]
            else:
                self.data = data
            self.comp = False

        if self.data2 != None:
            self.data = self.data2
            self.data2 = None
        i +=1

class EchoClient(protocol.Protocol):
    def connectionMade(self):
        self.parent = self.factory.parent
        self.gque = self.factory.gque
        self.tque = self.factory.tque
        logging.info('Connected')
        self.data = ''
        self.data2 = None
        self.parent.i = 1
        self.errorCount = 0
        self.comp = False
        self.endP = False
        self.parseP = False
        self.parseS = False
        logging.info('Connection Open')
        self.transport.registerProducer(self.transport, streaming=True)

    '''    
    Built in Twisted method overwritten:
    Recieves data parses apart each packet and updates Scan data
    '''
    def dataReceived(self, data):
    	time.sleep(0.5)
        incommingData(self,data)
    def connectionLost(self, reason):
        logging.info("Connection Lost")

'''
Handles lost server connections
Will exponentially try to reconnect to the server
Also removes and replaces saved figure with a lost connection identifier
creates new data array for everything except time data

'''
class EchoFactory(ClientFactory):
    protocol = EchoClient
    def __init__(self,parent):
        self.parent = parent

	def startedConnecting(self, connector):
		self.resetDelay()

    def clientConnectionFailed(self, connector, reason):
        logging.debug("Connection failed - goodbye!")
        logging.debug('Closed Connection')
        reactor.stop()
        try:
            self.parent.gt.join()
            self.parent.tt.join()
        except:
            logging.debug("Threads haven't started")
        for pr in self.parent.fan['param']:
            silentRemove(self,"fan_%s.png" % (pr))
            silentRemove(self,"geo_%s.png" % (pr))
        silentRemove(self,'time.png')


    def clientConnectionLost(self, connector, reason):
        logging.debug("Connection lost - goodbye!")
        logging.debug('Closed Connection')
        reactor.stop()
        try:
            self.parent.gt.join()
            self.parent.tt.join()
        except:
            logging.debug("Threads haven't started")
        for pr in self.parent.fan['param']:
            silentRemove(self,"fan_%s.png" % (pr))
            silentRemove(self,"geo_%s.png" % (pr))
        silentRemove(self,'time.png')



#connects server

def serverCon(self):
	t_date = datetime.date.today()
	logging.basicConfig(filename="errlog/err_%s%s_%s"\
		% (self.rad,self.channels[0],t_date.strftime('%Y%m%d')), level=logging.DEBUG, \
		format='%(asctime)s %(message)s')
	f = EchoFactory(self)
	f.parent = self
	f.gque = Queue()
	f.gque.put(self.myScan)
	f.tque = Queue()
	f.tque.put(self.myBeamList)
	f.tt = timeThread(self,f.tque)
	f.gt = geoThread(self,f.gque,f.tque)
	f.gt.start()
	f.tt.start()
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



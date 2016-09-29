from davitpy.pydarn.sdio.radDataTypes import beamData, scanData
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
from davitpy.utils.plotUtils import genCmap,mapObj,geoLoc
import time
from davitpy.pydarn.proc.music import getDataSet
from davitpy import utils
import logging.config
'''
A thread that plots and saves the geographic fan plot
and beam vs gates plot
'''
class geoThread(Thread):
	'''
	Initialization of global variables
	'''
	def __init__(self, parent,data,timeQue):
		super(geoThread, self).__init__()
		self.parent = parent
		self.data = data
		self.tq = timeQue
		self.oldCpid = -9999999999
		self.maxgates = int(self.parent.nrangs[0])
		self.stoprequest = Event()
	
	'''
	Checks if queue is empty and uploads beam information
	as long as stoprequest is not set.
	Once new data is loaded and replaced into the radar beam list
	the geographic data and beam number vs gate plots are called and saved.
	
	If the gate size is different than what is sent in the map of the 
	radar is updated to show all gates
	
	The map will also be updated if the maximum beam is greater then the 
	initial parameters 
	'''	
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
				self.stoprequest.set()
				break
			while not self.data.empty():
				myBeam = beamData()
				myBeam = self.data.get()
				if myBeam.cp != self.oldCpid:
					self.oldCpid = myBeam.cp
					self.parent.maxbm = self.parent.maxbeam[0]
				#updates if maxgates is changing
				if myBeam.prm.nrang != self.maxgates:
					logging.info('Changing Gates')
					self.maxgates = myBeam.prm.nrang
					self.parent.lon_0,self.parent.lat_0, self.parent.fovs,\
					self.parent.dist, self.parent.height,self.parent.width = geoLoc(self.parent.site,\
						self.maxgates,myBeam.prm.rsep,int(self.parent.maxbm))
					self.parent.myMap = mapObj(coords='geo', projection='stere',\
						lat_0=self.parent.lat_0, lon_0=self.parent.lon_0,\
						width= self.parent.width*1.3,height = self.parent.height*1.3,\
						grid =True)
				#updates myScan size if the beam number is greater then the current myScan size
				elif myBeam.bmnum >= len(myScan):
					bmnum = len(myScan)
					while myBeam.bmnum > len(myScan):
						time.sleep(0.1)
						tmp_myBeam = beamData()
						tmp_myBeam.bmnum = bmnum
						tmp_myBeam.time = timeNow.replace(tzinfo=None)
						myScan.append(tmp_myBeam)
						bmnum += 1
					myScan.append(myBeam)
					logging.info('Changing Beam number %s'%(myBeam))
					self.parent.maxbm = myBeam.bmnum+1
					self.parent.lon_0,self.parent.lat_0, self.parent.fovs,\
					self.parent.dist, self.parent.height,self.parent.width = geoLoc(self.parent.site,\
						self.maxgates,myBeam.prm.rsep,\
						int(self.parent.maxbm))
					self.parent.myMap = mapObj(coords='geo', projection='stere',\
						lat_0=self.parent.lat_0, lon_0=self.parent.lon_0,\
						width= self.parent.width*1.3,height = self.parent.height*1.3,\
						anchor = 'N',grid =True,draw=True)
				else:
					myScan.pop(myBeam.bmnum)
					myScan.insert(myBeam.bmnum,myBeam)
			#Plot and save geographic figure for each parameter
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
					nave = myBeam.prm.nave,
					inttime = myBeam.prm.inttsc,
					rTime=myBeam.time,
					radN = self.parent.names[0],
					dist = self.parent.dist,
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
				
			
			#Plot and save beam number vs gates figure for each parameter
			for i in range(len(self.parent.fan['figure'])):
				time.sleep(1)
				if self.parent.fan['param'][i] == 'velocity':
					self.parent.fan['gsct'] = True
				else:
					self.parent.fan['gsct'] = False
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
					
	
	'''
	Stops geoThread
	'''
	def join(self, timeout=None):
		self.stoprequest.set()
		logging.info("Closing geoThread")
		super(geoThread, self).join(timeout)

'''
A thread that plots and saves the time plot
and writes the beam information into a data file
'''
class timeThread(Thread):
	'''
	Initialization of global variables
	'''
	def __init__(self, parent, data):
		super(timeThread, self).__init__()
		self.parent = parent
		self.data = data
		self.stoprequest = Event()
	'''
	Checks if queue is empty and uploads beam information
	as long as stoprequest is not set.
	Once new data is loaded and replaced into the my beam list
	the time plot is called and saved. 
	'''		
	def run(self):
		myBeamList = scanData()
		while not self.data.empty():
			myBeamList = self.data.get(True, 0.01)
		while not self.stoprequest.isSet():
			time.sleep(20)
			timeNow = datetime.datetime.utcnow()
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
				#writes to a file so the beam data can be later uploaded
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
							rTime = timeNow,
							title = self.parent.names[0],
							myFov = self.parent.fovs)
					self.parent.time['figure'].savefig("%stime" % (self.parent.filepath[0]))
				except:
					logging.error('time plot missing info')
					logging.error('Time Figure: %s' %(sys.exc_info()[0]))
			else:
				lowData(self,'time.png')
	def join(self, timeout=None):
		self.stoprequest.set()
		logging.info("Closing timeThread")
		super(timeThread, self).join(timeout)
					
'''
ProcessMsg(self)
loads in the json data and load it correctly into
the specific beam with the fit and param data
Then upload the data in the proper que so that
the correct thread runs and updates
'''
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

'''
incommingData
parses incomming text into the fit and param data section
'''
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
            indF = -1
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

'''    
Built in Twisted method overwritten:
Initializes values recieves data calls the correct method
'''

class EchoClient(protocol.Protocol):
	#initializes needed values and starts connection to server
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

	#Recieves data and calls incommingData method
    def dataReceived(self, data):
    	time.sleep(0.5)
        incommingData(self,data)
    def connectionLost(self, reason):
        logging.info("Connection Lost")

'''
Handles lost server connections
Stops the reactor, threads and changings image to show loss of connection
'''
class EchoFactory(ClientFactory):
    protocol = EchoClient
    def __init__(self,parent):
        self.parent = parent


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


'''
Initializes queues and threads and sets up to wait for a server to connect
'''
def serverCon(self):
	t_date = datetime.date.today()
	logger = logging.getLogger()
	old_log = logger.handlers[0]
	logger.removeHandler(old_log)
	#root_logger.disabled = True
	#new_logger = logging.getLogger()
	#new_logger.disabled = False
	rl = logging.basicConfig(filename="errlog/err_%s%s_%s"\
		% (self.rad,self.channels[0],t_date.strftime('%Y%m%d')), level=logging.DEBUG, \
		format='%(asctime)s %(message)s')
	lh = logging.StreamHandler(rl)
	logger.addHandler(lh)
	logger.debug('Starting everything')
	print 'Writting to file'
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
	f.logger = logger
	reactor.connectTCP(self.hosts[0], int(self.ports[0]), f)
	reactor.run(installSignalHandlers=0)


'''
Clears figure and replaces with text indicating lost connection for
geographic and beam and gates plots
'''
def silentRemove(self,filename):
	for fanFig in self.parent.fan['figure']:
		fanFig.clf()
		fanFig.text(0.5,0.5,'Lost Connection',backgroundcolor='r',
			size='x-large',style='oblique',ha='center',va='center')
		fanFig.savefig("%s%s" % (self.parent.filepath[0],filename))

'''
Clears figure and replaces with text indicating low data amounts only for 
time plots
'''
def lowData(self,filename):
	self.parent.time['figure'].clf()
	self.parent.time['figure'].text(0.5,0.5,'No Data',backgroundcolor='r',
		size='x-large',style='oblique',ha='center',va='center')
	self.parent.time['figure'].savefig("%s%s" % (self.parent.filepath[0],filename))

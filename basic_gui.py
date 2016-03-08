from connection import serverCon,disconnect
from pydarn.sdio import beamData, scanData
import matplotlib.pyplot as plot
from radarPos import RadarPos
import sys, datetime, pytz
from utils import plotUtils,mapObj
from pydarn.radar import radFov
sys.path.append('~/davitpy')


'''
Parses the passed in arguments 
sets up each graph's inputs
clears out old graphs on start
and creates initial datasets on start

'''
class parseStart:
	
	def __init__(self,*args,**kwargs):
		self.channels = []
		parseArgs(self)
		if len(self.channels) == 0:
			self.channels.append('')
		
		
		self.i = 0
		self.rad = self.rad[0]
		self.maxbm = self.maxbeam[0]
		self.fan = None
		self.geo = None
		self.status = None
		#fan data
		self.data = {}
		self.data['param'] = ['velocity','power','width']
		self.data['sc'] = [[-1000,1000],[0,30],[0,500]]
		self.data['gsct'] = True
		self.data['drawEdge'] = False
		self.data['gridColor']='k'
		self.data['backgColor'] = 'w'
		self.data['figure'] = 3*[plot.figure()]
		self.fan = self.data
	
	
		#time data
		self.data = {}
		self.data['param'] = ['velocity','power','width']
		self.data['sc'] = [[-1000,1000],[0,30],[0,500]]
		self.data['gsct'] = True
		self.data['drawEdge'] = False
		self.data['figure'] = plot.figure()
		self.time = self.data
		
	
		#geo data
		self.data = {}
		self.data['param'] = ['velocity','power','width']
		self.data['sc'] = [[-1000,1000],[0,30],[0,500]]
		self.data['gsct'] = True
		self.data['drawEdge'] = False
		self.data['gridColor']='k'
		self.data['backgColor'] = 'w'
		self.data['waterColor'] = '#cce5ff'
		self.data['continentBorder'] = '0.75'
		self.data['continentColor'] = 'w'
		self.data['merColor'] = '0.75'
		self.data['merGrid'] = True
		self.data['figure'] = 3*[plot.figure()]
		self.geo = self.data
		createData(self)
		loadData(self)
		serverCon(self)
		
'''
Start the whole program
'''
def run():

	parseStart()


#parses input arguments	
def parseArgs(self):
	
	for argL in sys.argv:
		indEq = argL.find('=')
		indEq +=1
		if 'hosts' in argL:
			self.hosts = argL[indEq:].split(',')
		elif 'ports' in argL:
			self.ports = argL[indEq:].split(',')
		elif 'names' in argL:
			self.names = argL[indEq:].split(',')
		elif 'streams' in argL:
			self.streams = argL[indEq:].split(',')
		elif 'channels' in argL:
			self.channels = argL[indEq:].split(',')
		elif 'beams' in argL:
			self.beams = argL[indEq:].split(',')
		elif 'nrangs' in argL:
			self.nrangs = argL[indEq:].split(',')
		elif 'maxbeam' in argL:
			self.maxbeam = argL[indEq:].split(',')
		elif 'deltas' in argL:
			self.deltas = argL[indEq:].split(',')
		elif 'mapname' in argL:
			self.mapname = argL[indEq:].split(',')
		elif 'scale' in argL:
			self.scale = argL[indEq:].split(',')
		elif 'rad' in argL:
			self.rad = argL[indEq:].split(',')
		elif 'filepath' in argL:
			self.filepath = argL[indEq:].split(',')


#creates empty datasets used by all plots
#datasets later updated by incoming data
def createData(self):
	self.myScan = scanData()
	self.myBeamList = scanData()
	for i in range(0, int(self.maxbeam[0])):
		myBeam = beamData()
		today = datetime.datetime.utcnow()
		today = today.replace(tzinfo=pytz.utc)
		myBeam.time= today
		myBeam.bmnum = i
		myBeam.prm.nrang = int(self.nrangs[0])
		if i == 0:
			self.myBeam = myBeam
		self.myScan.append(myBeam)
	self.site = RadarPos(code = self.rad)
	self.site.tval = datetime.datetime.utcnow()
	self.lon_0,self.lat_0, self.fovs,self.dist,self.height,self.width = \
	plotUtils.geoLoc(self.site,
		int(self.nrangs[0]),self.site.rsep,
		int(self.maxbeam[0]))
	self.myMap = mapObj(coords='geo', projection='stere', lat_0=self.lat_0, lon_0=self.lon_0,
												 width= self.width*1.2,height = self.height*1.2,grid =True,anchor = 'N',
												 lineColor='0.75')

def loadData(self):
	timeNow = datetime.datetime.utcnow()
	dFilenm = 'data/'+`timeNow.month`+`timeNow.day`+`timeNow.year`+'_'+self.rad+self.channels[0]
	self.day = timeNow.day
	try:
		with open(dFilenm,'r+') as f:
			for line in f:
				spiltline = line.split(';')
				myBeam = beamData()
				myBeam.stid = int(spiltline[0])
				myBeam.bmnum = int(self.beams[0])
				myBeam.time = createDt(spiltline[1])
				myBeam.cp = int(spiltline[2])
				myBeam.prm.nave = int(spiltline[3])
				myBeam.prm.noisesky = float(spiltline[4])
				myBeam.prm.rsep = int(spiltline[5])
				myBeam.prm.nrang = int(spiltline[6])
				myBeam.prm.frang = int(spiltline[7])
				myBeam.prm.noisesearch = float(spiltline[8])
				myBeam.prm.tfreq = float(spiltline[9])
				myBeam.fit.slist = splitArray(spiltline[10])
				myBeam.prm.ifmode = int(spiltline[11])
				myBeam.fit.v = splitArray(spiltline[12])
				myBeam.fit.p_l  = splitArray(spiltline[13])
				myBeam.fit.w_l = splitArray(spiltline[14])
				myBeam.fit.gflg = splitArray(spiltline[15])
				self.myBeamList.append(myBeam)
		f.close()
	except:
		print dFilenm,'file doesn"t exist'
		
def splitArray(strArr):
	splitL = strArr.split(',')
	numArr = []
	for s in splitL:
		if '[' in s:
			s = s[1:len(s)]
		elif ']' in s:
			if '\n' in s:
				s = s[0:len(s)-2]
			else:
				s = s[0:len(s)-1]
		numArr.append(float(s))
	return numArr

def createDt(strDt):
	splitL = strDt.split('(')
	splitD = splitL[1].split(',')
	mt = splitD[5]
	dt = datetime.datetime(int(splitD[0]),int(splitD[1]),int(splitD[2]),\
		int(splitD[3]),int(splitD[4]),int(mt[0:len(mt)-1]))
	return dt
		
	
	
run()


from connection import serverCon,disconnect
from pydarn.sdio import beamData, scanData
import matplotlib.pyplot as plot
from radarPos import RadarPos
import os, errno
import sys 
sys.path.append('~/davitpy')
import datetime
import pytz
import utils
import numpy as np

import pydarn

'''
Parses the passed in arguments 
sets up each graph's inputs
clears out old graphs on start
and creates initial datasets on start

'''
class parseStart:
	
	def __init__(self,*args,**kwargs):
		parseArgs(self)
		self.i = 0
		self.rad = self.rad[0]
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
		self.data['figure'] = 3*[plot.figure(figsize=(11,8.5))]
		self.fan = self.data
	
	
		#time data
		self.data = {}
		self.data['param'] = ['velocity','power','width']
		self.data['sc'] = [[-1000,1000],[0,30],[0,500]]
		self.data['gsct'] = True
		self.data['drawEdge'] = False
		self.data['figure'] = plot.figure(figsize=(12,8))
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
		self.data['figure'] = 3*[plot.figure(figsize=(12,8))]
		self.geo = self.data
		createData(self)
		serverCon(self)
		
'''
Start the whole program
'''
def run():

	parseStart()
	silentRemove(self.filepath[0],'fan.png')
	silentRemove(self.filepath[0],'geo.png')
	silentRemove(self.filepath[0],'time.png')

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
	self.llcrnrlon,self.llcrnrlat,self.urcrnrlon,self.urcrnrlat,self.lon_0,self.lat_0, self.fovs,self.dist = utils.plotUtils.geoLoc(self.site,
		int(self.nrangs[0]),self.site.rsep,
		int(self.maxbeam[0]))

#remove previously written figures
def silentRemove(figPath,filename):
    try:
        os.remove("%s%s" % (figPath,filename))
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured
run()


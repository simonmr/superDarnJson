# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
.. module:: fan
     :synopsis: A module generating fan plots

.. moduleauthor:: AJ, 20130218

***************************
**Module**: pydarn.plotting.fan
***************************
**Functions**:
    * :func:`pydarn.plotting.fan.plotFan`
    * :func:`pydarn.plotting.fan.overlayFan`
"""
    
import numpy,math,datetime,time,gme,matplotlib
from matplotlib.collections import PolyCollection,LineCollection
from utils.timeUtils import *
from utils.plotUtils import genCmap
from utils import mapObj
from pydarn.plotting import overlayFov
from pydarn.radar import radFov
from pydarn.sdio import beamData
from pydarn.sdio.radDataRead import *
import matplotlib.pyplot as plt


def plotFan(myScan,rad,params='velocity',filtered=False ,\
        scales=[],channel='a',coords='geo',
        colors='lasse',gsct=False,fovs=None,edgeColors='face',\
        lowGray=False,fill=True,velscl=1000.,legend=True,overlayPoes=False,\
        poesparam='ted',poesMin=-3.,poesMax=0.5, maxbeams = 16, maxgates = 75, \
        poesLabel=r"Total Log Energy Flux [ergs cm$^{-2}$ s$^{-1}$]",overlayBnd=False, \
		tFreqBands=[],myFigs=None,bmnum = None,site = None,drawEdge = False,
		tfreq = None, noise = None,rTime = None, radN = None,dist = None,
		llcrnrlon=None,llcrnrlat=None,urcrnrlon=None,urcrnrlat=None,lon_0=None,lat_0=None,
		merGrid = True,merColor = '0.75',continentBorder = '0.75',
		waterColor = '#cce5ff',continentColor = 'w',backgColor='w',gridColor='k',\
		filepath = None,myMap = None):

    """A function to make a fan plot
    
    **Args**:
        * **rad** (list): a list of 3 letter radar codes, e.g. ['bks'], e.g. ['bks','wal','gbr']
        * **[param]** (str): the parameter to be plotted, valid inputs are 'velocity', 'power', 'width', 'elevation', 'phi0'.  default = 'velocity'
        * **[filtered]** (boolean): a flag indicating whether the data should be boxcar filtered.  default = False
        * **[scale]** (list): the min and max values of the color scale, i.e. [min,max].  If this is set to [], then default values will be used
        * **[channel] (char)**: the channel for which to plot data.  default = 'a'
        * **[coords]** (str): the coordinate system to use, valid inputs are 'geo', 'mag'.  default = 'geo'
        * **[colors]** (str): the color map to use, valid inputs are 'lasse', 'aj'.  default = 'lasse'
        * **[gsct]** (boolean): a flag indicating whether to plot ground scatter as gray.  default = False
        * **[fov]**  (boolean): a flag indicating whether to overplot the radar fields of view.  default = True
        * **[edgeColors]** (str): edge colors of the polygons, default = 'face'
        * **[lowGray]** (boolean): a flag indicating whether to plot low velocities in gray.  default = False
        * **[fill]** (boolean): a flag indicating whether to plot filled or point RB cells.  default = True
        * **[velscl]** (float): the velocity to use as baseline for velocity vector length, only applicable if fill = 0.  default = 1000
        * **[legend]** (boolean): a flag indicating whether to plot the legend, only applicable if fill = 0.  default = True
        * **[overlayPoes]** (boolean): a flag indicating whether to overlay poes data.  default = False
        * **[poesparam]** (str): the poes parameter to plot.  default = 'ted'.  available params can be found in :class:`gme.sat.poes.poesRec`
        * **[poesMin]** (float): the min value for the poes data color scale.  default = -3.
        * **[poesMax]**  (float): the max value for the poes data color scale.  default = 0.5
        * **[poesLabel]** (str): the label for the poes color bar.  default = r"Total Log Energy Flux [ergs cm$^{-2}$ s$^{-1}$]"
        * **[overlayBnd]** (boolean): a flag indicating whether to plot an auroral boundary determined from fitting poes data.  default = False
        * **[tFreqBands]** (list): upper and lower bounds of frequency in kHz to be used.  Must be unset (or set to []) or have a pair for each radar, and for any band set to [] the default will be used.  default = [[8000,20000]], [[8000,20000],[8000,20000]], etc.
    **Returns**:
        * Nothing

    **Example**:
        ::
        
            import datetime as dt
            pydarn.plotting.fan.plotFan(dt.datetime(2013,3,16,16,30),['fhe','fhw'],param='power',gsct=True)
            pydarn.plotting.fan.plotFan(dt.datetime(2013,3,16,16,30),['fhe','fhw'],param='power',gsct=True,tFreqBands=[[10000,11000],[]])

    Written by AJ 20121004
    Modified by Matt W. 20130717
    """

    
    

    #check the inputs
    assert(isinstance(rad,list)),"error, rad must be a list, eg ['bks'] or ['bks','fhe']"
    for r in rad:
        assert(isinstance(r,str) and len(r) == 3),'error, elements of rad list must be 3 letter strings'
    assert(coords == 'geo' or coords == 'mag'),"error, coords must be one of 'geo' or 'mag'"
    #assert(param == 'velocity' or param == 'power' or param == 'width' or \
    #   param == 'elevation' or param == 'phi0'), \
    #    "error, allowable params are 'velocity','power','width','elevation','phi0'"
    #assert(scale == [] or len(scale)==2), \
    #'error, if present, scales must have 2 elements'
    assert(colors == 'lasse' or colors == 'aj'),"error, valid inputs for color are 'lasse' and 'aj'"
    
    #check freq band and set to default if needed
    assert(tFreqBands == [] or len(tFreqBands) == len(rad)),'error, if present, tFreqBands must have same number of elements as rad'
    for i in range(len(myFigs)):
		time.sleep(01)
		param = params[i]
		scale = scales[i]
		myFig = myFigs[i]
		myFig.clf()
		tbands = []
		for i in range(len(rad)):
			if tFreqBands == [] or tFreqBands[i] == []: tbands.append([8000,20000])
			else: tbands.append(tFreqBands[i])
		
		for i in range(len(tbands)):
			assert(tbands[i][1] > tbands[i][0]),'error, frequency upper bound must be > lower bound'
		
		if(scale == []):
			if(param == 'velocity'): scale=[-200,200]
			elif(param == 'power'): scale=[0,30]
			elif(param == 'width'): scale=[0,150]
			elif(param == 'elevation'): scale=[0,50]
			elif(param == 'phi0'): scale=[-numpy.pi,numpy.pi]
		
			
		fbase = datetime.datetime.utcnow().strftime("%Y%m%d")
			
		cmap,norm,bounds = genCmap(param,scale,colors=colors,lowGray=lowGray)


		myBands = []
		for i in range(len(rad)):
			myBands.append(tbands[i])
		
		myMap.drawcoastlines(linewidth=0.5,color=continentBorder)
		myMap.drawmapboundary(fill_color=waterColor)
		myMap.fillcontinents(color=continentColor, lake_color=waterColor)
		#now, loop through desired time interval
		cols = []
		ft = 'None'
		#go though all files
		pcoll = None
		drawEdge = False
		gridColor ='k'
		backgColor = 'w'
		waterColor = '#cce5ff'
		continentBorder = '0.75'
		continentColor = 'w'
		merColor = '0.75'
		cTime = datetime.datetime.utcnow()

		overlayFov(myMap,site = site,fovColor=backgColor,\
			lineColor=gridColor, dateTime=cTime, fovObj=fovs[0]) 
		intensities, pcoll = overlayFan(myScan,myMap,myFig,param,coords,\
			gsct=gsct,site=site,fov=fovs[0], fill=fill,velscl=velscl,\
			dist=dist,cmap=cmap,norm=norm,scale = scale)
		#if no data has been found pcoll will not have been set, and the following code will object                                   
		if pcoll: 
			cbar = myFig.colorbar(pcoll,orientation='vertical',shrink=.65,fraction=.1,drawedges=drawEdge,norm=norm)
			l = []
			#define the colorbar labels
			for i in range(0,len(bounds)):
				if(param == 'phi0'):
					ln = 4
					if(bounds[i] == 0): ln = 3
					elif(bounds[i] < 0): ln = 5
					l.append(str(bounds[i])[:ln])
					continue
				l.append(str(int(bounds[i])))
			cbar.ax.set_yticklabels(l)
			cbar.ax.tick_params(axis='y',direction='out')
			#set colorbar ticklabel size
			for ti in cbar.ax.get_yticklabels():
				ti.set_fontsize(12)
			if(param == 'velocity'): 
				cbar.set_label('Velocity [m/s]',size=14)
				cbar.extend='max'
				
				
			if(param == 'grid'): cbar.set_label('Velocity [m/s]',size=14)
			if(param == 'power'): cbar.set_label('Power [dB]',size=14)
			if(param == 'width'): cbar.set_label('Spec Wid [m/s]',size=14)
			if(param == 'elevation'): cbar.set_label('Elev [deg]',size=14)
			if(param == 'phi0'): cbar.set_label('Phi0 [rad]',size=14)
		
		if(overlayPoes):
			pcols = gme.sat.poes.overlayPoesTed(myMap, myFig.gca(), cTime, param=poesparam, scMin=poesMin, scMax=poesMax)
			if(pcols != None):
				cols.append(pcols)
				pTicks = numpy.linspace(poesMin,poesMax,8)
				cbar = myFig.colorbar(pcols,ticks=pTicks,orientation='vertical',shrink=0.65,fraction=.1,norm=matplotlib.colors.Normalize(vmin=scale[0], vmax=scale[1]))
				cbar.ax.set_yticklabels(pTicks)
				cbar.set_label(poesLabel,size=14)
				cbar.ax.tick_params(axis='y',direction='out')
				#set colorbar ticklabel size
				for ti in cbar.ax.get_yticklabels():
					ti.set_fontsize(12)    
		if(overlayBnd):
			gme.sat.poes.overlayPoesBnd(myMap, myFig.gca(), cTime)
			
		xmin = 0.1
		xmax = 0.86
		
		#myFig.text(xmin,.95,title,ha='left',weight=550)
		#myFig.text((xmin+xmax)/2.,.95,str(rTime),weight=550,ha='center')
		if noise is None:
			noise =0
		plt.title(radN+'; Time: '+str(rTime),loc='center')
		plt.xlabel('Beam: '+str(bmnum)+'; Freq: '+str(tfreq)+'; Noise: '+"{0:.2f}".format(noise))
		#self.parent.geo['figure'][i].savefig("%sgeo_%s" % (self.parent.filepath[0],self.parent.geo['param'][i]))
		#handle the outputs
		myFig.savefig("%sgeo_%s" % (filepath,param),bbox_inches='tight')
    return myFigs

def overlayFan(myData,myMap,myFig,param,coords='geo',gsct=0,site=None,\
                                fov=None,gs_flg=[],fill=True,velscl=1000.,dist=1000.,
                                cmap=None,norm=None,alpha=1,scale = None):

    """A function of overlay radar scan data on a map

    **Args**:
        * **myData (:class:`pydarn.sdio.radDataTypes.scanData` or :class:`pydarn.sdio.radDataTypes.beamData` or list of :class:`pydarn.sdio.radDataTypes.beamData` objects)**: a radar beam object, a radar scanData object, or simply a list of radar beams
        * **myMap**: the map we are plotting on
        * **[param]**: the parameter we are plotting
        * **[coords]**: the coordinates we are plotting in
        * **[param]**: the parameter to be plotted, valid inputs are 'velocity', 'power', 'width', 'elevation', 'phi0'.  default = 'velocity
        * **[gsct]**: a flag indicating whether we are distinguishing ground scatter.  default = 0
        * **[intensities]**: a list of intensities (used for colorbar)
        * **[fov]**: a radar fov object
        * **[gs_flg]**: a list of gs flags, 1 per range gate
        * **[fill]**: a flag indicating whether to plot filled or point RB cells.  default = True
        * **[velscl]**: the velocity to use as baseline for velocity vector length, only applicable if fill = 0.  default = 1000
        * **[lines]**: an array to have the endpoints of velocity vectors.  only applicable if fill = 0.  default = []
        * **[dist]**: the length in map projection coords of a velscl length velocity vector.  default = 1000. km
    **OUTPUTS**:
        NONE

    **EXAMPLE**:
        ::
            
            overlayFan(aBeam,myMap,param,coords,gsct=gsct,site=sites[i],fov=fovs[i],\
                                                        verts=verts,intensities=intensities,gs_flg=gs_flg)

    Written by AJ 20121004
    """
    
    if(site == None):
        site = RadarPos(myData[0].stid)
    if(fov == None):
        fov = radFov.fov(site=site,rsep=myData[0].prm.rsep,\
        ngates=myData[0].prm.nrang+1,nbeams= site.maxbeam,coords=coords) 
    
    if(isinstance(myData,beamData)): myData = [myData]
    
    gs_flg,lines = [],[]
    if fill: verts,intensities = [],[]
    else: verts,intensities = [[],[]],[[],[]]
 
    #loop through gates with scatter
    for myBeam in myData:
    	if myBeam.fit.slist is not None:
			for k in range(0,len(myBeam.fit.slist)):
				if myBeam.fit.slist[k] not in fov.gates: continue
				r = myBeam.fit.slist[k]
				if fill:
					x1,y1 = myMap(fov.lonFull[myBeam.bmnum,r],fov.latFull[myBeam.bmnum,r])
					x2,y2 = myMap(fov.lonFull[myBeam.bmnum,r+1],fov.latFull[myBeam.bmnum,r+1])
					x3,y3 = myMap(fov.lonFull[myBeam.bmnum+1,r+1],fov.latFull[myBeam.bmnum+1,r+1])
					x4,y4 = myMap(fov.lonFull[myBeam.bmnum+1,r],fov.latFull[myBeam.bmnum+1,r])
					#save the polygon vertices
					verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))
					#save the param to use as a color scale
					if(param == 'velocity'): intensities.append(myBeam.fit.v[k])
					elif(param == 'power'): intensities.append(myBeam.fit.p_l[k])
					elif(param == 'width'): intensities.append(myBeam.fit.w_l[k])
					elif(param == 'elevation' and myBeam.prm.xcf): intensities.append(myBeam.fit.elv[k])
					elif(param == 'phi0' and myBeam.prm.xcf): intensities.append(myBeam.fit.phi0[k])
					
				else:
					x1,y1 = myMap(fov.lonCenter[myBeam.bmnum,r],fov.latCenter[myBeam.bmnum,r])
					verts[0].append(x1)
					verts[1].append(y1)
					
					x2,y2 = myMap(fov.lonCenter[myBeam.bmnum,r+1],fov.latCenter[myBeam.bmnum,r+1])
					
					theta = math.atan2(y2-y1,x2-x1)
					
					x2,y2 = x1+myBeam.fit.v[k]/velscl*(-1.0)*math.cos(theta)*dist,y1+myBeam.fit.v[k]/velscl*(-1.0)*math.sin(theta)*dist
					
					lines.append(((x1,y1),(x2,y2)))
					#save the param to use as a color scale
					if(param == 'velocity'): intensities[0].append(myBeam.fit.v[k])
					elif(param == 'power'): intensities[0].append(myBeam.fit.p_l[k])
					elif(param == 'width'): intensities[0].append(myBeam.fit.w_l[k])
					elif(param == 'elevation' and myBeam.prm.xcf): intensities[0].append(myBeam.fit.elv[k])
					elif(param == 'phi0' and myBeam.prm.xcf): intensities[0].append(myBeam.fit.phi0[k])
					
					if(myBeam.fit.p_l[k] > 0): intensities[1].append(myBeam.fit.p_l[k])
					else: intensities[1].append(0.)
				if(gsct): gs_flg.append(myBeam.fit.gflg[k])

    #do the actual overlay
    if(fill):
        #if we have data
        if(verts != []):
            if(gsct == 0):
                inx = numpy.arange(len(verts))
            else:
                inx = numpy.where(numpy.array(gs_flg)==0)
                x = PolyCollection(numpy.array(verts)[numpy.where(numpy.array(gs_flg)==1)],
                    facecolors='.3',linewidths=0,zorder=5,alpha=alpha,norm=norm)
                myFig.gca().add_collection(x, autolim=True)

            pcoll = PolyCollection(numpy.array(verts)[inx],
                edgecolors='none',linewidths=0,closed=False,zorder=4,
                alpha=alpha,cmap=cmap,norm=norm)
            #set color array to intensities
            pcoll.set_array(numpy.array(intensities)[inx])
            myFig.gca().add_collection(pcoll, autolim=True)
            return intensities,pcoll
        else:
        	return None,None
    else:
        #if we have data
        if(verts != [[],[]]):
            if(gsct == 0):
                inx = numpy.arange(len(verts[0]))
            else:
                inx = numpy.where(numpy.array(gs_flg)==0)
                #plot the ground scatter as open circles
                x = myFig.scatter(numpy.array(verts[0])[numpy.where(numpy.array(gs_flg)==1)],\
                        numpy.array(verts[1])[numpy.where(numpy.array(gs_flg)==1)],\
                        s=.1*numpy.array(intensities[1])[numpy.where(numpy.array(gs_flg)==1)],\
                        zorder=5,marker='o',linewidths=.5,facecolors='w',edgecolors='k')
                myFig.gca().add_collection(x, autolim=True)
                
            #plot the i-s as filled circles
            ccoll = myFig.gca().scatter(numpy.array(verts[0])[inx],numpy.array(verts[1])[inx], \
                            s=.1*numpy.array(intensities[1])[inx],zorder=10,marker='o',linewidths=.5, \
                            edgecolors='face',cmap=cmap,norm=norm)
            
            #set color array to intensities
            ccoll.set_array(numpy.array(intensities[0])[inx])
            myFig.gca().add_collection(ccoll)
            #plot the velocity vectors
            lcoll = LineCollection(numpy.array(lines)[inx],linewidths=.5,zorder=12,cmap=cmap,norm=norm)
            lcoll.set_array(numpy.array(intensities[0])[inx])
            myFig.gca().add_collection(lcoll)

            return intensities,lcoll

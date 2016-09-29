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
.. module:: fgp
   :synopsis: A module for generating rti plots

.. moduleauthor:: AJ, 20130123

*********************
**Module**: pydarn.plotting.rti
*********************
**Functions**:
  * :func:`pydarn.plotting.rti.plotRti`
  * :func:`pydarn.plotting.rti.plotFreq`
  * :func:`pydarn.plotting.rti.plotNoise`
  * :func:`pydarn.plotting.rti.plotCpid`
  * :func:`pydarn.plotting.rti.rtiTitle`
  * :func:`pydarn.plotting.rti.drawAxes`
"""


import numpy
from davitpy.utils.plotUtils import genCmap
import logging
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from davitpy.utils.timeUtils import *
from davitpy.pydarn.sdio import *
import matplotlib.pyplot as plt

def plotFgpJson(myScan,rad,bmnum=7,params=['velocity','power','width'], \
              scales=[],channel='a',coords='gate',colors='lasse',yrng=-1,gsct=False,lowGray=False, \
              filtered=False, tFreqBands=[], figure=None,xtick_size=9,
              ytick_size=9,xticks=None,axvlines=None,plotTerminator=False,
              tfreq = None, noise=None, rTime = None,radN = None):
  """create an rti plot for a secified radar and time period

  **Args**:
  	* **myScan** (Beam): Set of beam information for specific radar
    * **rad** (str): the 3 letter radar code, e.g. 'bks'
    * **[bmnum] (int)**: The beam to plot.  default: 7
    * **[params]** (list): a list of the fit parameters to plot, allowable values are: ['velocity', 'power', 'width', 'elevation', 'phi0'].  default: ['velocity', 'power', 'width']
    * **[scales]** (list): a list of the min/max values for the color scale for each param.  If omitted, default scales will be used.  If present, the list should be n x 2 where n is the number of elements in the params list.  Use an empty list for default range, e.g. [[-250,300],[],[]].  default: [[-200,200],[0,30],[0,150]]
    * **[channel]** (char): the channel you wish to plot, e.g. 'a', 'b', 'c', ...  default: 'a'
    * **[coords]** (str): the coordinates to use for the y axis.  The allowable values are 'gate', 'rng', 'geo', 'mag' default: 'gate'
    * **[colors]** (str): a string indicating what color bar to use, valid inputs are ['lasse','aj'].  default: 'lasse'
    * **[yrng]** (list or -1): a list indicating the min and max values for the y axis in the chosen coordinate system, or a -1 indicating to plot everything.  default: -1.
    * **[gsct]** (boolean): a flag indicating whether to plot ground scatter as gray. default: False (ground scatter plotted normally)
    * **[lowGray]** (boolean): a flag indicating whether to plot low velocity scatter as gray. default: False (low velocity scatter plotted normally)
    * **[filtered]** (boolean): a flag indicating whether to boxcar filter the data.  default = False (no filter)
    * **[tFreqBands]** (list): a list of the min/max values for the transmitter frequencies in kHz.  If omitted, the default band will be used.  If more than one band is specified, retfig will cause only the last one to be returned.  default: [[8000,20000]]
    * **[figure]** (matplotlib.figure) figure object to plot on.  If None, a figure object will be created for you.
    * **[xtick_size]** (int): fontsize of xtick labels
    * **[ytick_size]** (int): fontsize of ytick labels
    * **[xticks]** (list): datetime.datetime objects indicating the location of xticks
    * **[axvlines]** (list): datetime.datetime objects indicating the location vertical lines marking the plot
    * **[plotTerminator]** (boolean): Overlay the day/night terminator.
    * **[tfreq]** (int): the beams freqency for the title 
    * **[noise]** (float): the beams noise for the title
    * **[rTime]** (datetime): the beam time for the title
    * **[radN]** (str): Name of radar site for the title
  **Returns**:
    * Plotted figure

  **Example**:
    ::
    
      import datetime as dt
      import matplotlib.pyplot as plot
      plotFgpJson(myScan,'ade',params='velocity',gsct=True,
			scales=[-1000,1000],bmnum = 12,	figure = plot['figure'],
			tfreq = myBeam.prm.tfreq,noise = myBeam.prm.noisesearch,
			rTime=myBeam.time,radN = 'Adak East')

    
  Written by AJ 20121002
  Modified by Matt W. 20130715
  Modified by Nathaniel F. 20131031 (added plotTerminator)
  Modified by Michelle S. 20160324 (updated to create a real time plot and beam vs gate plot)
  """
    

  #check the inputs
  assert(isinstance(rad,str) and len(rad) == 3),'error, rad must be a string 3 chars long'
  assert(coords == 'gate' or coords == 'rng' or coords == 'geo' or coords == 'mag'),\
  "error, coords must be one of 'gate','rng','geo','mag"
  assert(isinstance(bmnum,int)),'error, beam must be integer'
  assert(0 < len(params) < 6),'error, must input between 1 and 5 params in LIST form'
  for i in range(0,len(params)):
    assert(params[i] == 'velocity' or params[i] == 'power' or params[i] == 'width' or \
    params[i] == 'elevation' or params[i] == 'phi0'), \
    "error, allowable params are 'velocity','power','width','elevation','phi0'"
  assert(scales == [] or len(scales)==len(params)), \
  'error, if present, scales must have same number of elements as params'
  assert(yrng == -1 or (isinstance(yrng,list) and yrng[0] <= yrng[1])), \
  'error, yrng must equal -1 or be a list with the 2nd element larger than the first'
  assert(colors == 'lasse' or colors == 'aj'),"error, valid inputs for color are 'lasse' and 'aj'"

  #assign any default color scales
  tscales = []
  for i in range(0,len(params)):
    if(scales == [] or scales[i] == []):
      if(params[i] == 'velocity'): tscales.append([-200,200])
      elif(params[i] == 'power'): tscales.append([0,30])
      elif(params[i] == 'width'): tscales.append([0,150])
      elif(params[i] == 'elevation'): tscales.append([0,50])
      elif(params[i] == 'phi0'): tscales.append([-numpy.pi,numpy.pi])
    else: tscales.append(scales[i])
  scales = tscales

  #assign default frequency band
  tbands = []
  if tFreqBands == []: tbands.append([8000,20000])
  else: 
    for band in tFreqBands: 
      #make sure that starting frequncy is less than the ending frequency for each band
      assert(band[0] < band[1]),"Starting frequency must be less than ending frequency!"
      tbands.append(band)


  if not myScan:
    logging.debug('error, no data available for the requested time/radar/filetype combination')
    return None

  #initialize empty lists
  vel,pow,wid,elev,phi0,beam,freq,cpid,nave,nsky,nsch,slist,mode,rsep,nrang,frang,gsflg = \
        [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
  for i in range(len(tbands)):
    beam.append([])
    cpid.append([])
    nave.append([])
    nsky.append([])
    rsep.append([])
    nrang.append([])
    frang.append([])
    nsch.append([])
    freq.append([])
    slist.append([])
    mode.append([])
    vel.append([])
    pow.append([])
    wid.append([])
    elev.append([])
    phi0.append([])
    gsflg.append([])
  
  #read the parameters of interest

    for myBeam in myScan:
	  beam[i].append(myBeam.bmnum)
	  cpid[i].append(myBeam.cp)
	  nave[i].append(myBeam.prm.nave)
	  nsky[i].append(myBeam.prm.noisesky)
	  rsep[i].append(myBeam.prm.rsep)
	  nrang[i].append(myBeam.prm.nrang)
	  frang[i].append(myBeam.prm.frang)
	  nsch[i].append(myBeam.prm.noisesearch)
	  if myBeam.prm.tfreq is None:
	  	  myBeam.prm.tfreq = 0
	  freq[i].append(myBeam.prm.tfreq/1e3)
	  slist[i].append(myBeam.fit.slist)
	  mode[i].append(myBeam.prm.ifmode)
	  if('velocity' in params): vel[i].append(myBeam.fit.v)
	  if('power' in params): pow[i].append(myBeam.fit.p_l)
	  if('width' in params): wid[i].append(myBeam.fit.w_l)
	  if('elevation' in params): elev[i].append(myBeam.fit.elv)
	  if('phi0' in params): phi0[i].append(myBeam.fit.phi0)
	  gsflg[i].append(myBeam.fit.gflg)


  for fplot in range(len(tbands)):
    #Check to ensure that data exists for the requested frequency band else
    #continue on to the next range of frequencies
    if not freq[fplot]:
      logging.debug('error, no data in frequency range '+str(tbands[fplot][0])+' kHz to '+str(tbands[fplot][1])+' kHz')
      rtiFig=None	#Need this line in case no data is plotted
      continue

    #get/create a figure
    rtiFig = figure
  
    
    #plot each of the parameter panels
    for p in range(len(params)):
      if(params[p] == 'velocity'): pArr = vel[fplot]
      elif(params[p] == 'power'): pArr = pow[fplot]
      elif(params[p] == 'width'): pArr = wid[fplot]
      elif(params[p] == 'elevation'): pArr = elev[fplot]
      elif(params[p] == 'phi0'): pArr = phi0[fplot]
      #draw the axis
      ax = drawAxes(rtiFig,beam[fplot],rad,cpid[fplot],bmnum,nrang[fplot],frang[fplot],rsep[fplot],p==len(params)-1,yrng=yrng,coords=coords,\
                    xtick_size=xtick_size,ytick_size=ytick_size,xticks=xticks,axvlines=axvlines)
  
      if(pArr == []): continue
      
      rmax = max(nrang[fplot])
      data=numpy.zeros((len(beam[fplot]),rmax))-150000
      if gsct: gsdata=numpy.zeros((len(beam[fplot]),rmax))-150000
      x=numpy.zeros(len(beam[fplot]))
      tcnt = 0
      dt_list   = []
      for i in range(len(beam[fplot])):
        x[tcnt]=beam[fplot][i]
        dt_list.append(beam[fplot][i])
        if(pArr[i] == []): continue
        
        if slist[fplot][i] != None:
          for j in range(len(slist[fplot][i])):
          	  if(not gsct or gsflg[fplot][i][j] == 0):
          	  	  data[tcnt][slist[fplot][i][j]] = pArr[i][j]
          	  elif gsct and gsflg[fplot][i][j] == 1:
          	  	  data[tcnt][slist[fplot][i][j]] = -100000.
        
        tcnt += 1
      tmpdata = numpy.ma.masked_where(data <= -150000, data)
      if(coords == 'gate'): y = numpy.linspace(0,rmax,rmax+1)
      elif(coords == 'rng'): y = numpy.linspace(frang[fplot][0],rmax*rsep[fplot][0],rmax+1)
      else: y = myFov.latFull[bmnum] 
      X, Y = numpy.meshgrid(x[:tcnt], y)
      cmap,norm,bounds = genCmap(params[p],scales[p],colors=colors,lowGray=lowGray)
      cmap.set_bad('w',1.0)
      pcoll = ax.pcolormesh(tmpdata[:][:].T, lw=0.01,edgecolors='w',alpha=1,cmap=cmap,norm=norm)
      cb = rtiFig.colorbar(pcoll,orientation='vertical',shrink=.65,fraction=.1)
      l = []
      #define the colorbar labels
      for i in range(0,len(bounds)):
        if(params[p] == 'phi0'):
          ln = 4
          if(bounds[i] == 0): ln = 3
          elif(bounds[i] < 0): ln = 5
          l.append(str(bounds[i])[:ln])
          continue
        if((i == 0 and params[p] == 'velocity') or i == len(bounds)-1):
          l.append(' ')
          continue
        l.append(str(int(bounds[i])))
      cb.ax.set_yticklabels(l)
        
      #set colorbar ticklabel size
      for t in cb.ax.get_yticklabels():
        t.set_fontsize(9)
      
      #set colorbar label
      if(params[p] == 'velocity'): cb.set_label('Velocity [m/s]',size=10)
      if(params[p] == 'grid'): cb.set_label('Velocity [m/s]',size=10)
      if(params[p] == 'power'): cb.set_label('Power [dB]',size=10)
      if(params[p] == 'width'): cb.set_label('Spec Wid [m/s]',size=10)
      if(params[p] == 'elevation'): cb.set_label('Elev [deg]',size=10)
      if(params[p] == 'phi0'): cb.set_label('Phi0 [rad]',size=10)
    xmin = 0.1
    xmax = 0.96
    if noise is None:
    	noise =0
    rtiFig.text(xmin,.95,radN,ha='left',weight=400)
    rtiFig.text((xmin+xmax)/2.,.95,str(rTime)+'; Beam: '+str(bmnum)+'; Freq: '+str(tfreq)+'; Noise: '+"{0:.2f}".format(noise),weight=100,ha='center')
    return rtiFig

def drawAxes(myFig,beam,rad,cpid,bmnum,nrang,frang,rsep,bottom,yrng=-1,\
	coords='gate',pos=[.1,.1,.85,.85],xtick_size=9,\
	ytick_size=9,xticks=None,axvlines=None):
  """draws empty axes for an rti plot

  **Args**:
    * **myFig**: the MPL figure we are plotting to
    * **times**: a list of datetime objects referencing the beam soundings
    * **rad**: 3 letter radar code
    * **cpid**: list of the cpids or the beam soundings
    * **bmnum**: beam number being plotted
    * **nrang**: list of nrang for the beam soundings
    * **frang**: list of frang of the beam soundings
    * **rsep**: list of rsep of the beam soundings
    * **bottom**: flag indicating if we are at the bottom of the page
    * **[yrng]**: range of y axis, -1=autoscale (default)
    * **[coords]**: y axis coordinate system, acceptable values are 'geo', 'mag', 'gate', 'rng'
    * **[pos]**: position of the plot
    * **[xtick_size]**: fontsize of xtick labels
    * **[ytick_size]**: fontsize of ytick labels
    * **[xticks]**: (list) datetime.datetime objects indicating the location of xticks
    * **[axvlines]**: (list) datetime.datetime objects indicating the location vertical lines marking the plot
  **Returns**:
    * **ax**: an axes object
    
  **Example:
    ::

      ax = drawAxes(aFig,times,rad,cpid,beam,nrang,frang,rsep,0)
      
  Written by AJ 20121002
  """
  
  nrecs = len(beam)
  #add an axes to the figure
  ax = myFig.add_axes(pos)
  ax.yaxis.set_tick_params(direction='out')
  ax.xaxis.set_tick_params(direction='out')
  ax.yaxis.set_tick_params(direction='out',which='minor')
  ax.xaxis.set_tick_params(direction='out',which='minor')

  #draw the axes
  ax.plot_date(np.min(beam), np.max(beam), fmt='w', \
  tz=None, xdate=True, ydate=False, alpha=0.0)
  
  if(yrng == -1):
    ymin,ymax = 99999999,-999999999
    if(coords != 'gate'):
      oldCpid = -99999999
      for i in range(len(cpid)):
        if(cpid[i] == oldCpid): continue
        oldCpid = cpid[i]
        ymin = 0
        if(nrang[i]*rsep[i]+frang[i] > ymax): ymax = nrang[i]*rsep[i]+frang[i]
    
    else:
      ymin,ymax = 0,max(nrang)
  else:
    ymin,ymax = yrng[0],yrng[1]

  xmin,xmax = np.min(beam),np.max(beam)
  xrng = (xmax-xmin)
  #format the x axis
  xMinor = MultipleLocator(2)
  xMajor = MultipleLocator(xmax+1)
  ax.xaxis.set_label_text('Beam Number',size=10)
  ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
  ax.xaxis.set_minor_locator(xMinor)
  ax.xaxis.set_major_locator(xMajor)


  if(coords == 'gate'): 
    ax.yaxis.set_label_text('Range gate',size=10)
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.yaxis.set_major_locator(MultipleLocator((ymax-ymin)/5.))
    ax.yaxis.set_minor_locator(MultipleLocator((ymax-ymin)/25.))
  elif(coords == 'geo' or coords == 'mag'): 
    if(coords == 'mag'): ax.yaxis.set_label_text('Mag Lat [deg]',size=10)
    else: ax.yaxis.set_label_text('Geo Lat [deg]',size=10)
    ax.yaxis.set_major_formatter(FormatStrFormatter('%0.2f'))
    ax.yaxis.set_major_locator(MultipleLocator((ymax-ymin)/5.))
    ax.yaxis.set_minor_locator(MultipleLocator((ymax-ymin)/25.))
  elif(coords == 'rng'): 
    ax.yaxis.set_label_text('Slant Range [km]',size=10)
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.yaxis.set_major_locator(MultipleLocator(1000))
    ax.yaxis.set_minor_locator(MultipleLocator(250))
  
  ax.set_ylim(bottom=ymin,top=ymax)

  return ax

# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""plotUtils module

Plotting utilities (maps, colormaps, ...)

Functions
--------------------------------------------------------------
genCmap         generate a custom colormap
drawCB          draw a colorbar
curvedEarthAxes Plot axes in (R, Theta) coordinates with lower
                limit at R = Earth radius
addColorbar     Colorbar for `curvedEarthAxes`
textHighlighted highlighted annotation (with white lining)
--------------------------------------------------------------

Classes
--------------------------------
mapObj          Create empty map
--------------------------------

"""
from mpl_toolkits import basemap
import logging


class mapObj(basemap.Basemap):
	"""Create empty map
	
	Parameters
	----------
	ax : Optional[matplotlib.axes._subplots.AxesSubplot]
		Subplot axis to associate with this map (default=None)
	datetime : Optional[datetime.datetime]
		new format for providing the time that is added to the mapObj
		class as the attribute "datetime".  This is needed
		when plotting in MLT.  If not provided, (and not
		provided in dateTime) the current time will be
		used (default=None)
	coords : Optional[str]
		plotting coordinates. (default='geo')
	projection : Optional[str]
		map projection. (default='stere')
	resolution : Optional[char]
		map resolution. c=crude, i=inter. (default='c')
	dateTime : Optional[datetime.datetime]
		old format for providing the time that is added to the mapObj
		class as the attribute "dateTime".  This is needed when plotting
		in MLT.  If not provided, (and not provided in datetime) the
		current time will be used. (default=None)
	lon_0 : Optional[float]
		center meridian (default is -70E)
	lat_0 : Optional[float]
		center latitude (default is -90E)
	boundinglat : Optional[float]
		bounding latitude (default is +/-20)
	width : Optional[float]
		width in m from the (lat_0, lon_0) center
	height : Optional[float]
		height in m from the (lat_0, lon_0) center
	draw : Optional[bool]
		set to "False" to skip initial drawing of map
	fillContinents : Optional[float]
		continent color. Default=0.8 is 'grey'
	fillOceans : Optional[char]
		ocean color. Default='None' provides no filling
	fillLakes : Optional[char]
		lake color. Default='None' provides no filling
	fill_alpha : Optional[float]
		Specifies transparency for continents and lakes.
		Default=.5 provides 50% transparency.
	coastLineWidth : Optional[float]
		Line width for coastlines. Default=0.0
	coastLineColor : Optional[char]
		Line color for coastlines. Default=None
	grid : Optional[bool]
		show/hide parallels and meridians grid (default=True)
	gridLabels : Optional[bool]
		label parallels and meridians (default=True)
	showCoords : Optional[bool]
		display coordinate system name in upper right
		corner (default=True)
	**kwargs : 
		See <http://tinyurl.com/d4rzmfo> for more keywords
	
	Attributes
	----------
	lat_0 : float
	
	lon_0 : float
	
	datetime :
	
	dateTime :
	
	Returns
	-------
	map : a Basemap object (<http://tinyurl.com/d4rzmfo>)
		with an additional attribute that specifies the datetime
	
	Examples
	--------
		myMap = mapObj(lat_0=50, lon_0=-95, width=111e3*60, height=111e3*60)
	
	Another example is:
	
		# Create the map
		myMap = utils.mapObj(boundinglat=30, coords='mag')
		# Plot the geographic and geomagnetic North Poles
		# First convert from lat/lon to map projection coordinates...
		x, y = myMap(0., 90., coords='geo')
		# ...then plot
		myMap.scatter(x, y, zorder=2, color='r')
		# Convert to map projection...
		x, y = myMap(0., 90., coords='mag')
		# ...and plot
		myMap.scatter(x, y, zorder=2, color='g')
	
	Notes
	-----
	Once the map is created, all plotting calls will be assumed to
	already be in the map's declared coordinate system given by **coords**.
	
	
	written by Sebastien, 2013-02
	
	"""


	def __init__(self, ax=None, datetime=None, coords='geo', projection='stere',
				 resolution='c', dateTime=None, lat_0=None, lon_0=None,
				 boundinglat=None, width=None, height=None, draw=True, 
				 fillContinents='.8', fillOceans='None', fillLakes=None,
				 fill_alpha=.5, coastLineWidth=0., coastLineColor=None,
				 grid=True, gridLabels=True, showCoords=True, **kwargs):
		"""This class wraps arround :class:`mpl_toolkits.basemap.Basemap`
		(<http://tinyurl.com/d4rzmfo>)
	
		"""

		import numpy as np
		from pylab import text
		import math
		from copy import deepcopy
		import datetime as dt
		
		self._coordsDict = {'mag': 'AACGM',
			  'geo': 'Geographic',
			  'mlt': 'MLT',
			  'fan': 'Fan Only'}

		if coords is 'mlt':             
		  print 'MLT coordinates not implemented yet.'
		  return
	
		if datetime is None:
		  datetime = dt.datetime.utcnow()
		self.datetime = datetime
	
		# Add an extra member to the Basemap class
		if coords is not None and coords not in self._coordsDict:
		  print 'Invalid coordinate system given in coords ({}): setting "geo"'.format(coords)
		  coords = 'geo'
		self.coords = coords
	
		# Set map projection limits and center point depending on hemisphere selection
		if lat_0 is None: 
		  lat_0 = 90.
		  if boundinglat: lat_0 = math.copysign(lat_0, boundinglat)
		if lon_0 is None: 
		  lon_0 = -100.
		  if self.coords == 'mag': 
			_, lon_0, _ = aacgm.aacgmConv(0., lon_0, 0., self.datetime.year, 0)
		if boundinglat:
		  width = height = 2*111e3*( abs(lat_0 - boundinglat) )
	
		# Initialize map
		super(mapObj, self).__init__(projection=projection, resolution=resolution, 
			lat_0=lat_0, lon_0=lon_0, width=width, height=height, **kwargs)
	
		# Add continents
		if coords is not 'mlt' or dateTime is not None:
		  _ = self.drawcoastlines(linewidth=coastLineWidth)
		  _ = self.drawmapboundary(fill_color=fillOceans)
		  _ = self.fillcontinents(color=fillContinents, lake_color=fillLakes)
	
		# Add coordinate spec
		if showCoords:
		  _ = text(self.urcrnrx, self.urcrnry, self._coordsDict[coords]+' coordinates', 
			  rotation=-90., va='top', fontsize=8)
	
		# draw parallels and meridians.
		if grid:
		  parallels = np.arange(-80.,81.,20.)
		  out = self.drawparallels(parallels, zorder=10)
		  # label parallels on map
		  if gridLabels: 
			lablon = int(self.llcrnrlon/10)*10
			rotate_label = lablon - lon_0 if lat_0 >= 0 else lon_0 - lablon + 180.
			x,y = basemap.Basemap.__call__(self, lablon*np.ones(parallels.shape), parallels)
			for ix,iy,ip in zip(x,y,parallels):
			  if not self.xmin <= ix <= self.xmax: continue
			  if not self.ymin <= iy <= self.ymax: continue
			  '''
			  _ = text(ix, iy, r"{:3.0f}$^\circ$".format(ip), 
				  rotation=rotate_label, va='center', ha='center', zorder=10, color=lineColor)
				  '''
		  # label meridians on bottom and left
		  meridians = np.arange(-180.,181.,20.)
		  if gridLabels: 
			merLabels = [False,False,False,True]
		  else: 
			merLabels = [False,False,False,False]
		  # draw meridians
		  out = self.drawmeridians(meridians, labels=merLabels, zorder=10)

	def __call__(self, x, y, inverse=False, coords=None, altitude=0.):
		from copy import deepcopy
		import numpy as np
		import inspect
	
		from davitpy.utils import coord_conv
	
		# First we need to check and see if drawcoastlines() or a similar 
		# method is calling because if we are in a coordinate system 
		# differing from 'geo' then the coastlines will get plotted 
		# in the wrong location...
		try:
		  callerFile, _, callerName = \
				  inspect.getouterframes(inspect.currentframe())[1][1:4]
		except:
		  return basemap.Basemap.__call__(self, x, y, inverse=inverse)
	
		# If call was from drawcoastlines, etc. then we do something different
		if 'mpl_toolkits' in callerFile and callerName is '_readboundarydata':
		  x, y = coord_conv(x, y, "geo", self.coords, altitude=0.,
							date_time=self.datetime)
		  return basemap.Basemap.__call__(self, x, y, inverse=False)
	
		# If the call was not from drawcoastlines, etc. do the conversion.
	
		# If we aren't changing between lat/lon coordinate systems:
		elif coords is None:
		  return basemap.Basemap.__call__(self, x, y, inverse=inverse)
	
		# If inverse is true do the calculation of x,y map coords first, 
		# then lat/lon coord system change.
		elif inverse:
		  x, y = basemap.Basemap.__call__(self, x, y, inverse=True)
		  return coord_conv(x, y, self.coords, coords, altitude=altitude,
						   date_time=self.datetime)
	
		# If inverse is false do the lat/lon coord system change first, 
		# then calculation of x,y map coords.
		else:
		  x, y = coord_conv(x, y, coords, self.coords, altitude=altitude,
						   date_time=self.datetime)
		  return basemap.Basemap.__call__(self, x, y, inverse=False)
	
	def _readboundarydata(self, name, as_polygons=False):
		from copy import deepcopy
		import _geoslib
		import numpy as np
	
		from davitpy.utils import coord_conv
	
		lons, lats = coord_conv(list(self._boundarypolyll.boundary[:, 0]),
								list(self._boundarypolyll.boundary[:, 1]),
								self.coords, "geo", altitude=0.,
								date_time=self.datetime)
		b = np.asarray([lons,lats]).T
		oldgeom = deepcopy(self._boundarypolyll)
		newgeom = _geoslib.Polygon(b).fix()
		self._boundarypolyll = newgeom
		out = basemap.Basemap._readboundarydata(self, name,
												as_polygons=as_polygons)
		self._boundarypolyll = oldgeom
		return out


def drawCB(fig,coll,cmap,norm,map=False,pos=[0,0,1,1]):
	"""manually draws a colorbar on a figure.  This can be used in lieu of the standard mpl colorbar function if you need the colorbar in a specific location.  See :func:`pydarn.plotting.rti.plotRti` for an example of its use.
	**Args**:
	* **fig** (`matplotlib.figure.Figure <http://matplotlib.org/api/figure_api.html#matplotlib.figure.Figure>`_): the figure being drawn on.
	* **coll** (`matplotlib.collections.Collection <http://matplotlib.org/api/collections_api.html?highlight=collection#matplotlib.collections.Collection>`_: the collection using this colorbar
	* **cmap** (`matplotlib.colors.ListedColormap <http://matplotlib.org/api/colors_api.html?highlight=listedcolormap#matplotlib.colors.ListedColormap>`_): the colormap being used
	* **norm** (`matplotlib.colors.BoundaryNorm <http://matplotlib.org/api/colors_api.html?highlight=matplotlib.colors.boundarynorm#matplotlib.colors.BoundaryNorm>`_): the colormap index being used
	* **[map]** (boolean): a flag indicating the we are drawing the colorbar on a figure with a map plot
	* **[pos]** (list): the position of the colorbar.  format = [left,bottom,width,height]
	**Returns**:
	**Example**:
	::
	  cmap,norm,bounds = genCmap('velocity', [-200,200], colors='aj', lowGray=True)
	
	Written by AJ 20120820
	"""
	import matplotlib,numpy
	import matplotlib.pyplot as plot
	
	if not map:
		#create a new axes for the colorbar
		cax = fig.add_axes(pos)
		#set the colormap and boundaries for the collection
		#of plotted items
		if(isinstance(coll,list)):
			for c in coll:
				c.set_cmap(cmap)
				c.set_norm(norm)
				cb = plot.colorbar(c,cax=cax)
		else:
			coll.set_cmap(cmap)
			coll.set_norm(norm)
			cb = plot.colorbar(coll,cax=cax)
	else:
		if(isinstance(coll,list)):
			for c in coll:
				c.set_cmap(cmap)
				c.set_norm(norm)
				cb = fig.colorbar(c,location='right')
		else:
			coll.set_cmap(cmap)
			coll.set_norm(norm)
			cb = fig.colorbar(coll,location='right',pad="5%")
		
	cb.ax.tick_params(axis='y',direction='out')
	return cb


################################################################################
################################################################################
def curvedEarthAxes(rect=111, fig=None, minground=0., maxground=2000, minalt=0,
                    maxalt=500, Re=6371., nyticks=5, nxticks=4):
    """Create curved axes in ground-range and altitude

    Parameters
    ----------
    rect : Optional[int]
        subplot spcification
    fig : Optional[pylab.figure object]
        (default to gcf)
    minground : Optional[float]

    maxground : Optional[int]
        maximum ground range [km]
    minalt : Optional[int]
        lowest altitude limit [km]
    maxalt : Optional[int]
        highest altitude limit [km]
    Re : Optional[float] 
        Earth radius in kilometers
    nyticks : Optional[int]
        Number of y axis tick marks; default is 5
    nxticks : Optional[int]
        Number of x axis tick marks; deafult is 4

    Returns
    -------
    ax : matplotlib.axes object
        containing formatting
    aax : matplotlib.axes object
        containing data

    Example
    -------
        import numpy as np
        from utils import plotUtils
        ax, aax = plotUtils.curvedEarthAxes()
        th = np.linspace(0, ax.maxground/ax.Re, 50)
        r = np.linspace(ax.Re+ax.minalt, ax.Re+ax.maxalt, 20)
        Z = exp( -(r - 300 - ax.Re)**2 / 100**2 ) * np.cos(th[:, np.newaxis]/th.max()*4*np.pi)
        x, y = np.meshgrid(th, r)
        im = aax.pcolormesh(x, y, Z.T)
        ax.grid()

    written by Sebastien, 2013-04

    """
    from matplotlib.transforms import Affine2D, Transform
    import mpl_toolkits.axisartist.floating_axes as floating_axes
    from matplotlib.projections import polar
    from mpl_toolkits.axisartist.grid_finder import FixedLocator, DictFormatter
    import numpy as np
    from pylab import gcf

    ang = maxground / Re
    minang = minground / Re
    angran = ang - minang
    angle_ticks = [(0, "{:.0f}".format(minground))]
    while angle_ticks[-1][0] < angran:
        tang = angle_ticks[-1][0] + 1./nxticks*angran
        angle_ticks.append((tang, "{:.0f}".format((tang-minang)*Re)))
    grid_locator1 = FixedLocator([v for v, s in angle_ticks])
    tick_formatter1 = DictFormatter(dict(angle_ticks))

    altran = float(maxalt - minalt)
    alt_ticks = [(minalt+Re, "{:.0f}".format(minalt))]
    while alt_ticks[-1][0] < Re+maxalt:
        alt_ticks.append((altran / float(nyticks) + alt_ticks[-1][0], 
                          "{:.0f}".format(altran / float(nyticks) +
                                          alt_ticks[-1][0] - Re)))
    _ = alt_ticks.pop()
    grid_locator2 = FixedLocator([v for v, s in alt_ticks])
    tick_formatter2 = DictFormatter(dict(alt_ticks))

    tr_rotate = Affine2D().rotate(np.pi/2-ang/2)
    tr_shift = Affine2D().translate(0, Re)
    tr = polar.PolarTransform() + tr_rotate

    grid_helper = \
        floating_axes.GridHelperCurveLinear(tr, extremes=(0, angran, Re+minalt,
                                                          Re+maxalt),
                                            grid_locator1=grid_locator1,
                                            grid_locator2=grid_locator2,
                                            tick_formatter1=tick_formatter1,
                                            tick_formatter2=tick_formatter2,)

    if not fig: fig = gcf()
    ax1 = floating_axes.FloatingSubplot(fig, rect, grid_helper=grid_helper)

    # adjust axis
    ax1.axis["left"].label.set_text(r"Alt. [km]")
    ax1.axis["bottom"].label.set_text(r"Ground range [km]")
    ax1.invert_xaxis()

    ax1.minground = minground
    ax1.maxground = maxground
    ax1.minalt = minalt
    ax1.maxalt = maxalt
    ax1.Re = Re

    fig.add_subplot(ax1, transform=tr)

    # create a parasite axes whose transData in RA, cz
    aux_ax = ax1.get_aux_axes(tr)

    # for aux_ax to have a clip path as in ax
    aux_ax.patch = ax1.patch

    # but this has a side effect that the patch is drawn twice, and possibly
    # over some other artists. So, we decrease the zorder a bit to prevent this.
    ax1.patch.zorder=0.9

    return ax1, aux_ax


def addColorbar(mappable, ax):
    """ Append colorbar to axes

    Parameters
    ----------
    mappable :
        a mappable object
    ax :
        an axes object

    Returns
    -------
    cbax :
        colorbar axes object

    Notes
    -----
    This is mostly useful for axes created with :func:`curvedEarthAxes`.

    written by Sebastien, 2013-04

    """
    from mpl_toolkits.axes_grid1 import SubplotDivider, LocatableAxes, Size
    import matplotlib.pyplot as plt 

    fig1 = ax.get_figure()
    divider = SubplotDivider(fig1, *ax.get_geometry(), aspect=True)

    # axes for colorbar
    cbax = LocatableAxes(fig1, divider.get_position())

    h = [Size.AxesX(ax), # main axes
         Size.Fixed(0.1), # padding
         Size.Fixed(0.2)] # colorbar
    v = [Size.AxesY(ax)]

    _ = divider.set_horizontal(h)
    _ = divider.set_vertical(v)

    _ = ax.set_axes_locator(divider.new_locator(nx=0, ny=0))
    _ = cbax.set_axes_locator(divider.new_locator(nx=2, ny=0))

    _ = fig1.add_axes(cbax)

    _ = cbax.axis["left"].toggle(all=False)
    _ = cbax.axis["top"].toggle(all=False)
    _ = cbax.axis["bottom"].toggle(all=False)
    _ = cbax.axis["right"].toggle(ticklabels=True, label=True)

    _ = plt.colorbar(mappable, cax=cbax)

    return cbax


def textHighlighted(xy, text, ax=None, color='k', fontsize=None, xytext=(0,0),
                    zorder=None, text_alignment=(0,0), xycoords='data', 
                    textcoords='offset points', **kwargs):
    """Plot highlighted annotation (with a white lining)
    
    Parameters
    ----------
    xy :
        position of point to annotate
    text : str
        text to show
    ax : Optional[ ]

    color : Optional[char]
        text color; deafult is 'k'
    fontsize : Optional [ ]
        text font size; default is None
    xytext : Optional[ ]
        text position; default is (0, 0)
    zorder :
        text zorder; default is None
    text_alignment : Optional[ ]

    xycoords : Optional[ ]
        xy coordinate[1]; default is 'data'
    textcoords : Optional[ ]
        text coordinate[2]; default is 'offset points'
    **kwargs :


    Notes
    -----
    Belongs to class rbspFp.

    References
    ----------
    [1] see `matplotlib.pyplot.annotate
        <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.annotate>`)
    [2] see `matplotlib.pyplot.annotate
        <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.annotate>`)


    """
    import matplotlib as mp
    from pylab import gca

    if ax is None:
        ax = gca()

    text_path = mp.text.TextPath((0, 0), text, size=fontsize, **kwargs)

    p1 = mp.patches.PathPatch(text_path, ec="w", lw=4, fc="w", alpha=0.7,
                              zorder=zorder,
                              transform=mp.transforms.IdentityTransform())

    p2 = mp.patches.PathPatch(text_path, ec="none", fc=color, zorder=zorder, 

                              transform=mp.transforms.IdentityTransform())

    offsetbox2 = \
        mp.offsetbox.AuxTransformBox(mp.transforms.IdentityTransform())
    offsetbox2.add_artist(p1)
    offsetbox2.add_artist(p2)

    ab = mp.offsetbox.AnnotationBbox(offsetbox2, xy, xybox=xytext,
                                     xycoords=xycoords, boxcoords=textcoords,
                                     box_alignment=text_alignment,
                                     frameon=False)

    ab.set_zorder(zorder)
    ax.add_artist(ab)



def genCmap(param, scale, colors='lasse', lowGray=False):
    """Generates a colormap and returns the necessary components to use it

    Parameters
    ----------
    param : str
        the parameter being plotted ('velocity' and 'phi0' are special cases,
        anything else gets the same color scale)
    scale : list
        a list with the [min,max] values of the color scale
    colors : Optional[str]
        a string indicating which colorbar to use, valid inputs are 
        'lasse', 'aj'.  default = 'lasse'
    lowGray : Optional[boolean]
        a flag indicating whether to plot low velocities (|v| < 15 m/s) in
        gray.  default = False

    if self.coords is 'geo':
      return basemap.Basemap.__call__(self, x, y, inverse=inverse)

    elif self.coords is 'mag':
      try:
        callerFile, _, callerName = inspect.getouterframes(inspect.currentframe())[1][1:4]
      except: 
        return basemap.Basemap.__call__(self, x, y, inverse=inverse)
      if isinstance(y, float) and abs(y) == 90.:
        return basemap.Basemap.__call__(self, x, y, inverse=inverse)
      if 'mpl_toolkits' in callerFile and callerName is '_readboundarydata':
        if not inverse:
          try:
            nx, ny = len(x), len(y)
            x = np.array(x)
            y = np.array(y)
            shape = x.shape
            yout, xout, _ = aacgm.aacgmConvArr(
              list(y.flatten()), list(x.flatten()), [0.]*nx, 
              self.datetime.year, 0)
            xout = np.array(xout).reshape(shape)
            yout = np.array(yout).reshape(shape)
          except TypeError:
            yout, xout, _ = aacgm.aacgmConv(y, x, 0., 
              self.datetime.year, 0)
          return basemap.Basemap.__call__(self, xout, yout, inverse=inverse)
        else:
          return basemap.Basemap.__call__(self, x, y, inverse=inverse)
      else:
        return basemap.Basemap.__call__(self, x, y, inverse=inverse)

    elif self.coords is 'mlt':
      print 'Not implemented'
      callerFile, _, callerName = inspect.getouterframes(inspect.currentframe())[1][1:4]


  def _readboundarydata(self, name, as_polygons=False):
    from models import aacgm
    from copy import deepcopy
    import _geoslib
    import numpy as np

    if self.coords is 'mag':
      nPts = len(self._boundarypolyll.boundary[:, 0])
      lats, lons, _ = aacgm.aacgmConvArr(
              list(self._boundarypolyll.boundary[:, 1]), 
              list(self._boundarypolyll.boundary[:, 0]), 
              [0.]*nPts, self.datetime.year, 1)
      b = np.asarray([lons,lats]).T
      oldgeom = deepcopy(self._boundarypolyll)
      newgeom = _geoslib.Polygon(b).fix()
      self._boundarypolyll = newgeom
      out = basemap.Basemap._readboundarydata(self, name, as_polygons=as_polygons)
      self._boundarypolyll = oldgeom
      return out
    else: 
      return basemap.Basemap._readboundarydata(self, name, as_polygons=as_polygons)

"""
    import matplotlib,numpy
    import matplotlib.colors as col
    import matplotlib.pyplot as plot
  
    #the MPL colormaps we will be using
    cmj = matplotlib.cm.jet
    cmpr = matplotlib.cm.prism
  
    #check for a velocity plot
    if(param == 'velocity'):
        #check for what color scale we want to use
        cdict = {'red': ((0.0, 0.0, 0.0),
            (0.25, 1.0, 1.0),
            (0.5, 1.0, 0.0),
            (0.8, 0.0, 0.0),
            (1.0, 1.0, 1.0)),
        'green': ((0.0, 1.0, 1.0),
            (0.25, 1.0, 1.0),
            (0.5, 0.0, 0.0),
            (0.8, 0.7, 0.7),
            (1.0, 1.0, 1.0)),
        'blue': ((0.0, 0.0, 0.0),
            (0.4, 0.0, 0.0),
            (0.5, 0.0, 1.0),
            (0.8, 0.7, 0.7),
            (1.0, 1.0, 1.0))}
        cmap = col.LinearSegmentedColormap('my_colormap',cdict,256)

        #define the boundaries for color assignments
        bounds = numpy.round(numpy.linspace(scale[0],scale[1],11))
        bounds = numpy.append(bounds,50000.)
        norm = matplotlib.colors.Normalize(vmin=scale[0], vmax=scale[1])
        cmap.set_under('.6',1.0)
   
  #if its a non-velocity plot
    else:
        cdict = {'red': ((0.0, 0.0, 0.0),
                 (0.5, 0.0, 0.0),
                 (0.75, 1.0, 1.0),
                 (1.0, 1.0, 1.0)),
            'green':((0.0, 0.0, 0.0),
                 (0.25, 0.7, 0.7),
                 (0.5, 1.0, 1.0),
                 (0.8, 0.7, 0.7),
                 (1.0, 0.0, 0.0)),
            'blue': ((0.0, 1.0, 1.0),
                 (0.2, 0.7, 0.7),
                 (0.4, 1.0, 1.0),
                 (0.5, 0.0, 0.0),
                 (1.0, 0.0, 0.0))}
        cmap = col.LinearSegmentedColormap('my_colormap',cdict,256)
      
        #define the boundaries for color assignments
        bounds = numpy.round(numpy.linspace(scale[0],scale[1],11))
        bounds = numpy.append(bounds,50000.)
        norm = matplotlib.colors.Normalize(vmin=scale[0], vmax=scale[1])

        cmap.set_under('.6',1.0)

    return cmap,norm,bounds
  

################################################################################
################################################################################
def geoLoc(site,maxgates, rsep, maxbeams):
	#Things to pass in:
	#site= RadarPos(myBeam.stid)
	# myBeam.prm.nrang =  maxgates
	# myBeam.prm.rsep  = seems to be the same per beam
	# myBeam.cp
	import numpy,math,matplotlib,calendar,datetime,pylab
	from davitpy import pydarn
	from davitpy.utils import plotUtils
	import logging
	import matplotlib.pyplot as plot
	import matplotlib.lines as lines
	from matplotlib.ticker import MultipleLocator
	import matplotlib.patches as patches
	from matplotlib.collections import PolyCollection,LineCollection
	from mpl_toolkits.basemap import Basemap, pyproj
	from matplotlib.figure import Figure
	import matplotlib.cm as cm
	from matplotlib.backends.backend_agg import FigureCanvasAgg
    

	xmin,ymin,xmax,ymax = 1e16,1e16,-1e16,-1e16
	
	fovs,lonFull,latFull=[],[],[]
	lonC,latC = [],[]
	
	latFull.append(site.geolat)
	lonFull.append(site.geolon)
	latC.append(site.geolat)     #latC and lonC are used for figuring out
	lonC.append(site.geolon)     #where the map should be centered.
	for i in range(maxbeams):
		myFov = pydarn.radar.radFov.fov(site=site,rsep=rsep,\
						nbeams=maxbeams,ngates= maxgates,coords='geo')
		fovs.append(myFov)
		for b in range(0,maxbeams+1):
			for k in range(0,maxgates+1):
				lonFull.append(myFov.lonFull[b][k])
				latFull.append(myFov.latFull[b][k])
		
		k=maxgates
		b=0
	latC.append(myFov.latFull[b][k])
	lonC.append(myFov.lonFull[b][k])
	b=maxbeams
	latC.append(myFov.latFull[b][k])
	lonC.append(myFov.lonFull[b][k])

	fEdgeLat = myFov.latFull[0][k]
	fEdgeLon = myFov.lonFull[0][k]
	lEdgeLat = myFov.latFull[b][k]
	lEdgeLon = myFov.lonFull[b][k]
	cEdgeLat = myFov.latFull[int(b/2)][k]
	cEdgeLon = myFov.lonFull[int(b/2)][k]

	lat_0 = myFov.latFull[int(b/2)][int(k/2)]
	lon_0 = myFov.lonFull[int(b/2)][int(k/2)]

	tmpmap = plotUtils.mapObj(coords='geo',projection='stere', width=10.0**3, 
												height=10.0**3, lat_0=lat_0, lon_0=lon_0)

	xsite,ysite = tmpmap(site.geolon,site.geolat)
	fex,fey = tmpmap(fEdgeLon,fEdgeLat)
	lex,ley = tmpmap(lEdgeLon,lEdgeLat)
	cex,cey = tmpmap(cEdgeLon,cEdgeLat)
	bwidth = numpy.sqrt((fex-lex)**2+(fey-ley)**2)
	leWidth = numpy.sqrt((fex-xsite)**2+(fey-ysite)**2)
	riWidth = numpy.sqrt((xsite-lex)**2+(ysite-ley)**2)
	if bwidth <leWidth:
		if leWidth < riWidth:
			width = riWidth
		else:
			width = leWidth
	elif bwidth <riWidth:
		if riWidth < leWidth:
			width = leWidth
		else:
			width = riWidth
	else:
		width = bwidth
	height = numpy.sqrt((cex-xsite)**2+(cey-ysite)**2)

	dist = width/50.
	cTime = datetime.datetime.utcnow()

	#draw the actual map we want
	return lon_0,lat_0,fovs,dist,width,height


if __name__ == "__main__":
    import pylab as plt
    from datetime import datetime

    from davitpy.models import aacgm

    time = datetime(2014,8,7,18,30)
    time2 = datetime(2014,8,8,0,0)

    print "Simple tests for plotUtils"
    coords='geo'
    lat_0=20.
    lon_0=150.
    print "Setting up figure 1 and axis"
    fig=plt.figure(1)
    ax=None
    print "Init a mapObj instance with draw==False"
    tmpmap1 = mapObj(coords=coords,projection='stere', draw=False, 
                     llcrnrlon=100, llcrnrlat=0, urcrnrlon=170, urcrnrlat=40,
                     lat_0=lat_0, lon_0=lon_0, resolution='l', ax=ax,
                     datetime=time, dateTime=time)
    print "initializing plots with plt.show, expect an empty figure 1 window"
    print "Close figure window to continue with example"
    plt.show()
    print "call the draw method for tmpmap1"
    tmpmap1.draw()
    print "initializing plots with plt.show, expect a map in figure 1 window"
    print "Close figure window to continue with example"
    plt.show()
    print "Making plot in geo and mag for comparison."
    fig2=plt.figure(2)
    ax=None
    print "Init a mapObj instance with draw==True"
    tmpmap2 = mapObj(coords=coords,projection='stere', draw=True,
                     llcrnrlon=100, llcrnrlat=0, urcrnrlon=170, urcrnrlat=40,
                     lat_0=lat_0, lon_0=lon_0, resolution='l', datetime=time,
                     dateTime=time)
    fig3=plt.figure(3)
    ax=None
    coords="mag"
    print "The inputs for the mag plot have been converted to magnetic"
    print "beforehand so the maps should show the same region."
    tmpmap3 = mapObj(coords=coords,projection='stere', draw=True,
                     llcrnrlon=172.63974536615848,llcrnrlat=-8.8093703108623647,
                     urcrnrlon=-121.21238751130332,urcrnrlat=33.758571820294179,
                     lat_0=lat_0, lon_0=lon_0,resolution='l', datetime=time,
                     dateTime=time)
    print "initializing plots with plt.show, expect fig 2 & 3 windows with maps"
    print "Close figure window to continue with example"
    plt.show()

    print "\nComparing magnetic and MLT.  Time selected is " + str(time)
    fig4=plt.figure(4)
    ax=None
    coords="mag"
    tmpmap4 = mapObj(coords=coords, projection="stere", draw=True,
                     boundinglat=40., lat_0=90., lon_0=0., resolution='l',
                     datetime=time, dateTime=time)
    fig5=plt.figure(5)
    ax=None
    coords="mlt"
    tmpmap5 = mapObj(coords=coords, projection="stere", draw=True,
                     boundinglat=40., lat_0=90., lon_0=0., resolution='l',
                     datetime=time, dateTime=time)
    print "MLT at zero MLON should be at " + \
      str(aacgm.mltFromYmdhms(time.year, time.month, time.day,
                              time.hour, time.minute, time.second, 0.))
    print "Figures 4 and 5 should now appear.  Close their windows to continue."
    plt.show()

    print "\nTesting some coordinate transformations."
    print "  Converting geo lat/lon to map x/y to geo lat/lon."
    print "  geo lat/lon to map x/y"

    map1 = mapObj(coords='geo',projection='stere',llcrnrlon=100, llcrnrlat=0, 
                  urcrnrlon=170, urcrnrlat=40, lat_0=54, lon_0=-120,
                  resolution='l', draw=False)
    x,y = map1(-120,54)
    print "    Expected: ",14898932.7446,-14364789.7586
    print "    Received: ",x,y
    print "  map x/y to geo lat/lon"
    lon,lat = map1(x,y,inverse=True,coords='geo')
    print "    Expected: ",-119.99999999999999, 54.000000000000014
    print "    Received: ",lon,lat

    print "\n  Converting mag lat/lon to map x/y to mag lat/lon."
    print "  geo lat/lon to map x/y"
    map1 = mapObj(coords='mag',projection='stere',llcrnrlon=100, llcrnrlat=0,
                  urcrnrlon=170, urcrnrlat=40, lat_0=54, lon_0=-120,
                  resolution='l', draw=False)
    x,y = map1(-120,54)
    print "    Expected: ",14898932.7446,-14364789.7586
    print "    Received: ",x,y
    print "  map x/y to geo lat/lon"
    lon,lat = map1(x,y,inverse=True,coords='mag')
    print "    Expected: ",-119.99999999999999, 54.000000000000014
    print "    Received: ",lon,lat

    print "\n  Converting geo lat/lon to map x/y to mag lat/lon."
    print "  geo lat/lon to map x/y"
    map1 = mapObj(coords='geo',projection='stere',llcrnrlon=100, llcrnrlat=0,
                  urcrnrlon=170, urcrnrlat=40, lat_0=54, lon_0=-120,
                  resolution='l', draw=False)
    x,y = map1(-120,54)
    print "    Expected: ",14898932.7446,-14364789.7586
    print "    Received: ",x,y
    print "  map x/y to mag lat/lon"
    lon,lat = map1(x,y,inverse=True,coords='mag')
    print "    Expected: ",-59.9940107681,59.9324622167
    print "    Received: ",lon,lat

    print "\n  Converting mag lat/lon to map x/y to geo lat/lon."
    print "  mag lat/lon to map x/y"
    map1 = mapObj(coords='mag', projection='stere', llcrnrlon=100, llcrnrlat=0,
                  urcrnrlon=170, urcrnrlat=40, lat_0=54, lon_0=-120,
                  resolution='l', draw=False)
    x,y = map1(-120,54)
    print "    Expected: ",14898932.7446,-14364789.7586
    print "    Received: ",x,y
    print "  map x/y to geo lat/lon"
    lon,lat = map1(x,y,inverse=True,coords='geo')
    print "    Expected: ",175.311901385,58.8384430722
    print "    Received: ",lon,lat

    print "\n  Converting geo lat/lon from a mag map to map x/y."
    print "  mag lat/lon to map x/y"
    map1 = mapObj(coords='mag',projection='stere',llcrnrlon=100, llcrnrlat=0,
                  urcrnrlon=170, urcrnrlat=40, lat_0=54, lon_0=-120,
                  resolution='l', draw=False)
    x,y = map1(175.311901385,58.8384430722,coords='geo')
    print "    Expected: ",14900062.142,-14366347.2577
    print "    Received: ",x,y

    print "\n  Converting mag lat/lon from a geo map to map x/y."
    print "  mag lat/lon to map x/y"
    map1 = mapObj(coords='geo',projection='stere',llcrnrlon=100, llcrnrlat=0,
                  urcrnrlon=170, urcrnrlat=40, lat_0=54, lon_0=-120,
                  resolution='l', draw=False)
    x,y = map1(-59.9940107681,59.9324622167,coords='mag')
    print "    Expected: ",14902099.9295,-14362212.9526
    print "    Received: ",x,y

    print "Testing datetime/dateTime checking."
    print "Setting only datetime:"
    map1 = mapObj(coords='geo',projection='stere', llcrnrlon=100, llcrnrlat=0,
                  urcrnrlon=170, urcrnrlat=40, lat_0=54, lon_0=-120,
                  resolution='l', draw=False, datetime=time)
    print "datetime: "+str(map1.datetime)
    print "dateTime: "+str(map1.dateTime)
    print "Setting only dateTime:"
    map1 = mapObj(coords='geo',projection='stere', llcrnrlon=100, llcrnrlat=0,
                  urcrnrlon=170, urcrnrlat=40, lat_0=54, lon_0=-120,
                  resolution='l', draw=False, dateTime=time)
    print "datetime: "+str(map1.datetime)
    print "dateTime: "+str(map1.dateTime)
    print "Setting both the same:"
    map1 = mapObj(coords='geo',projection='stere', llcrnrlon=100, llcrnrlat=0,
                  urcrnrlon=170, urcrnrlat=40, lat_0=54, lon_0=-120,
                  resolution='l', draw=False, datetime=time, dateTime=time)
    print "datetime: "+str(map1.datetime)
    print "dateTime: "+str(map1.dateTime)
    print "Setting neither:"
    map1 = mapObj(coords='geo', projection='stere', llcrnrlon=100, llcrnrlat=0,
                  urcrnrlon=170, urcrnrlat=40, lat_0=54, lon_0=-120,
                  resolution='l', draw=False)
    print "datetime: "+str(map1.datetime)
    print "dateTime: "+str(map1.dateTime)
    print "Setting to different times, should fail:"
    map1 = mapObj(coords='geo', projection='stere', llcrnrlon=100, llcrnrlat=0,
                  urcrnrlon=170, urcrnrlat=40, lat_0=54, lon_0=-120,
                  resolution='l', draw=False, datetime=time, dateTime=time2)





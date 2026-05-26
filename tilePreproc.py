# -*- coding: utf-8 -*-
"""
Created on Fri May 15 14:20:48 2026

@author: swimm
"""

import grass.script as gs
import grass.grassdb.data as gdb
import numpy as np
import pandas as pd

ditchPrefix ='BluEr'
profilePts=ditchPrefix + '_profilePts'  # GRASS layer

hucPrefix = 'minneopa'

tileLayer = hucPrefix + '_tiles'

#tileLayer = 'tiles_renamed'
ditchLayer = 'BluEr_lines_renamed'
streamLayer = 'streams_selected'
DEM = 'minneopa_4m_topography'

fileDir = "C:/Users/swimm/Downloads/"

res = 4
lineSep='\r\n'

dem='minneopa_4m_topography'

#%% To be created
path = fileDir + "tile_network.txt"
path_orig = fileDir + "tiles_origCat.txt"
path_tileElev = fileDir + "tiles_elevProfile.txt"
path_attrs = fileDir + "tile_attrs.txt"
path_ditchElev = fileDir + "ditches_elevProfile.txt"

tiles_broken = hucPrefix + '_tiles_broken'
tiles_nameless = hucPrefix + '_tiles_nameless'
tiles_renamed = hucPrefix + '_tiles_renamed'

tileEnds =hucPrefix + '_tileEnds'
tileStarts= hucPrefix +'_tileStarts'
tilePts = hucPrefix + '_tilePts'
ditchPts = ditchPrefix + '_ditchPts'

#%%

#gs.run_command('v.what.rast', map_=profilePts, raster=dem, column='elev', layer=2)
#gs.run_command('v.db.select', map_=profilePts, layer=2, format_='csv', file=path_ditchesElev, overwrite=True)

if not gdb.map_exists(tiles_renamed, 'vector'):

    gs.run_command('v.clean', flags='c', input_=tileLayer, output=tiles_broken, tool='break')
    gs.run_command('v.category', flags='t', input_=tiles_broken, output=tiles_nameless, option='del', cat=-1)
    gs.run_command('v.category', input_=tiles_nameless, output=tiles_renamed, option='add')
    gs.run_command('v.db.connect', flags='d', map_=tiles_renamed)
    gs.run_command('v.db.addtable', map_=tiles_renamed)
    
    orig_cats = gs.read_command('v.category', input_=tiles_broken, option='print')
    ls_orig_cats = orig_cats.split(lineSep)[:-1]
    #ls_orig_cats = pd.Series(ls_orig_cats[:-1]).astype('int')
    fIDs = np.arange(1, len(ls_orig_cats)+1)
    dfOrig = pd.DataFrame({'cat': fIDs, 'orig_cat': ls_orig_cats})
    dfOrig.to_csv(path_orig, index=False)
    
    
    gs.run_command('v.to.points', input_=tiles_renamed, output=tileEnds, use='end')
    gs.run_command('v.to.points', input_=tiles_renamed, output=tileStarts, use='start')
    gs.run_command('v.to.points', input_=tiles_renamed, output=tilePts, dmax=res)
    gs.run_command('v.to.points', input_=ditchLayer, output=ditchPts, dmax=res)
    
    gs.run_command('v.db.addcolumn', map_=tileEnds, layer=2, columns=['dist_stream double', \
                   'dist_ditch double', 'ditch_cat int', 'ditch_along double', 'dist_tile double', 'tile_cat int'])
        
    gs.run_command('v.distance', from_=tileEnds, from_layer=2, to=streamLayer, \
                   upload='dist', column='dist_stream')
    gs.run_command('v.distance', from_=tileEnds, from_layer=2, to=ditchLayer, \
                   upload=['dist','cat', 'to_along'], column=['dist_ditch', 'ditch_cat', 'ditch_along'])
    gs.run_command('v.distance', from_=tileEnds, from_layer=2, to=tileStarts, \
                   upload=['dist','cat'], column=['dist_tile','tile_cat'])
        
    gs.run_command('v.to.db', map_=tilePts, layer=2, option='coor', columns=['x','y'])
    gs.run_command('v.what.rast', map_=tilePts, layer=2, raster=DEM, column='elev')
    
    gs.run_command('v.to.db', map_=ditchPts, layer=2, option='coor', columns=['x','y'])
    gs.run_command('v.what.rast', map_=ditchPts, layer=2, raster=DEM, column='elev')
    
    gs.run_command('v.db.select', map_=tileEnds, layer=2, format_='csv', \
                   separator='comma', file=path, overwrite=True)
    gs.run_command('v.db.select', map_=tilePts, layer=2, format_='csv', \
                   separator='comma', file=path_tileElev, overwrite=True)      
    gs.run_command('v.db.select', map_=tileLayer, format_='csv', \
                   separator='comma', file=path_attrs, overwrite=True)    






         
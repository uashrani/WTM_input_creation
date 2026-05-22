# -*- coding: utf-8 -*-
"""
Created on Mon May 11 11:41:08 2026

@author: swimm
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

fileDir = "C:/Users/swimm/Downloads/"

path = fileDir + "tile_network.txt"
path_orig = fileDir + "tiles_origCat.txt"
path_elev = fileDir + "tiles_elevProfile.txt"
path_attrs = fileDir + "tile_attrs.txt"

dist_stream=50
dist_ditch=10
dist_tile=5

filler_grade = 0.04

#%% Functions
def smooth_elev(lcat, df_elev, df_origCats, outElev=0):
    orig_cat = int(df_origCats['orig_cat'][df_origCats['cat']==lcat].iloc[0])
    grade = df_attrs['a_grade'][df_attrs['cat']==orig_cat].iloc[0]
    
    if grade <= 0:
        grade = filler_grade
    #grade = 0.02
    
    slope = -grade * 0.01
    
    tileProfile = df_elev[df_elev['lcat']==lcat]
    outAlong = tileProfile['along'].iloc[-1]
    #print(outElev)
    if outElev == 0: outElev = tileProfile['elev'].iloc[-1]
    
    elev_smooth = slope*(tileProfile['along']-outAlong)+outElev
    
    #i=0
    if (sum(elev_smooth > tileProfile['elev']) / len(tileProfile) > 0.5):
        #print(lcat)
        
        if (lcat in list(outlets['cat'])) or (graph.has_node(lcat)==False) \
            or (len(list(graph.successors(lcat)))==0):
                while (sum(elev_smooth > tileProfile['elev']) / len(tileProfile) > 0):
                    elev_smooth -= 0.1
                    
                print(lcat)
        # else:
        #     #print(sum_)
        #     while (sum(elev_smooth > tileProfile['elev']) / len(tileProfile) > 0.5) and slope < -0.00001:
        #         slope += 0.00001
        #         elev_smooth = slope*(tileProfile['along']-outAlong)+outElev
            # if (sum(elev_smooth > tileProfile['elev']) / len(tileProfile) < 0.5):
            #     #print(lcat, ' got fixed, grade: ', slope*-100)
            #     pass
            # else:
            #     print(lcat)
                
                
        # if (sum(elev_smooth > tileProfile['elev']) > 0.5):
        #     print(lcat)
                    
                    
                #print(lcat)
    # while (sum(elev_smooth > tileProfile['elev']) / len(tileProfile)) > 0.5:
    #     elev_smooth -= 0.1
    #     if i == 0: print(lcat)
    #     i += 1
    
    df_elev.loc[df_elev['lcat']==lcat, 'elev_smooth'] = elev_smooth
    df_origCats.loc[df_origCats['cat']==lcat, 'visited'] = 1
    
    #print('Just did ', lcat)
    
    return df_elev, df_origCats

def move_down(lcat, df_elev, df_origCats):
    
        if (lcat in list(outlets['cat'])) or (graph.has_node(lcat)==False) \
            or (len(list(graph.successors(lcat)))==0):
            df_elev, df_origCats = smooth_elev(lcat, df_elev, df_origCats)
            
            return df_elev, df_origCats
        
        else:
            nextTile = list(graph.successors(lcat))[0]
            
            # If the next one has already been visited, smooth this one using boundary condition
            if df_origCats['visited'][df_origCats['cat']==nextTile].iloc[0]:
                # Get the boundary condition
                outElev = df_elev['elev_smooth'][(df_elev['lcat']==nextTile) & (df_elev['along']==0)].iloc[0]
                df_elev, df_origCats = smooth_elev(lcat, df_elev, df_origCats, outElev=outElev)
                
                return df_elev, df_origCats
            # If the next one has not yet been visited, do that one first
            else:
                
                return move_down(nextTile, df_elev, df_origCats)
        

#%% 
df = pd.read_csv(path)
df_origCats = pd.read_csv(path_orig)
df_elev = pd.read_csv(path_elev)
df_attrs = pd.read_csv(path_attrs)

outlets = df[(df['dist_ditch']<dist_ditch) | (df['dist_stream']<dist_stream)]

nonOutlets = df[(df['dist_ditch']>dist_ditch) & (df['dist_stream']>dist_stream) & (df['dist_tile'] < dist_tile)]
nonOutlets = nonOutlets[nonOutlets['cat'] != nonOutlets['tile_cat']]
# Temporary solution for circular loops
# nonOutlets = nonOutlets[(nonOutlets['cat'] != 651) & (nonOutlets['tile_cat'] != 651)]
# nonOutlets = nonOutlets[(nonOutlets['cat'] != 654) & (nonOutlets['tile_cat'] != 654)]

tileConnects=pd.DataFrame({'from':nonOutlets['cat'], 'to':nonOutlets['tile_cat']})
graph = nx.from_pandas_edgelist(tileConnects, source='from', target='to', create_using=nx.DiGraph)  

### Use linear profile for the outlets
df_elev['elev_smooth'] = 0.1
df_origCats['visited'] = 0


#df_origCats['orig_cat']=[int(s.split('/')[0]) for s in df_origCats['orig_cat']]

#for lcat in [438]:
for lcat in df_origCats['cat']:
     while df_origCats['visited'][df_origCats['cat']==lcat].iloc[0] == 0:
         df_elev, df_origCats = move_down(lcat, df_elev, df_origCats)
         
#df_elev.to_csv(fileDir + 'tile_elevs.txt', index=False, columns=['x','y','elev_smooth'])
         
fig, axs = plt.subplots(1, 5, figsize=(15, 4))
ax = axs.flat
    
for (i,cat) in enumerate([429,612]):
    prof = df_elev[df_elev['lcat']==cat]
    visted = df_origCats['visited'][df_origCats['cat']==cat].iloc[0]
    
    ax[i].plot(prof['along'], np.minimum(prof['elev'], \
                                          prof['elev_smooth']), 'dimgray', linewidth=10, label='new DEM')
    ax[i].plot(prof['along'], prof['elev'], 'orange', label='land surface')
    ax[i].plot(prof['along'], prof['elev_smooth'], 'cyan', label='tile')
    
    ax[i].set_ylim([300,303])
    
ax[i].legend()
    

    
    
# fig, axs = plt.subplots(7,7, figsize=(20,18))
# ax = axs.flat

# for (i,lcat) in enumerate(outlets['cat']):
 
#     df_elev = smooth_elev(lcat, df_elev)
    
#     prof = df_elev[df_elev['lcat']==lcat]
    
#     #ax[i].plot(prof['along'], prof['elev'])
#     #ax[i].plot(prof['along'], prof['elev_smooth'])
    
#     if graph.has_node(lcat):
#         prevLcats = list(graph.predecessors(lcat))
        
#         for prevLcat in prevLcats:
#             outElev = prof['elev_smooth'].iloc[0]
#             df_elev = smooth_elev(lcat, df_elev, outElev=outElev)
        

### Now do the other tiles
# for lcat in df_origCats['cat']:
#     if lcat in outlets['cat']:
#         continue
#     else if graph.has_node(lcat)==False:
#         df_elev = smooth_elev(lcat, df_elev)
#     else:
        
    
        
    
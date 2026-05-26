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
path_ditchElev = fileDir + "ditches_elevProfile.txt"

dist_stream=50
dist_ditch=10
dist_tile=5

filler_grade = 0.04

#%% Functions
def smooth_elev(lcat, df_elev, df_origCats, ditchReplace, outElev=0, gradeFac=1):
    orig_cat = int(df_origCats['orig_cat'][df_origCats['cat']==lcat].iloc[0])
    grade = df_attrs['a_grade'][df_attrs['cat']==orig_cat].iloc[0]*gradeFac
    
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
    if (sum(elev_smooth > tileProfile['elev']) / len(tileProfile) > 0.1):
        #print(lcat)
        
        if (lcat in list(outlets['cat'])) or (graph.has_node(lcat)==False) \
            or (len(list(graph.successors(lcat)))==0):
                while np.nanmean(tileProfile['elev'] - elev_smooth) < 1:
                
                    elev_smooth -= 0.1
                    
                df_entry = df[df['lcat']==lcat].iloc[0]
                if df_entry['dist_ditch'] == 0 and df_entry['ditch_along']==0:
                    
                    lastElev = elev_smooth.iloc[-1]
                    
                    ditch_cat = df_entry['ditch_cat']
                    ditch_prof = df_ditchElev[df_ditchElev['lcat']==ditch_cat]
                    
                    ditch_elevSmooth = slope*ditch_prof['along'] + lastElev
                    
                    burnedDiff = ditch_prof['elev'] - ditch_elevSmooth
                    replaceUntil = np.where(burnedDiff < 0)[0][0]
                    
                    ditchReplace_row = ditch_prof.iloc[:replaceUntil].copy()
                    ditchReplace_row['elev_smooth'] = ditch_elevSmooth
                    
                    ditchReplace = pd.concat((ditchReplace, ditchReplace_row))
    
    df_elev.loc[df_elev['lcat']==lcat, 'elev_smooth'] = elev_smooth
    df_origCats.loc[df_origCats['cat']==lcat, 'visited'] = 1
    
    #print('Just did ', lcat)
    
    return df_elev, df_origCats, ditchReplace

def move_down(lcat, df_elev, df_origCats, ditchReplace, gradeFac=1):
    
        #print('now doing lcat ', lcat)
    
        if (lcat in list(outlets['cat'])) or (graph.has_node(lcat)==False) \
            or (len(list(graph.successors(lcat)))==0):
            df_elev, df_origCats, ditchReplace = smooth_elev(lcat, df_elev, df_origCats, ditchReplace, gradeFac=gradeFac)
            
            return df_elev, df_origCats, ditchReplace
        
        else:
            nextTile = list(graph.successors(lcat))[0]
            
            # If the next one has already been visited, smooth this one using boundary condition
            if df_origCats['visited'][df_origCats['cat']==nextTile].iloc[0]:
                # Get the boundary condition
                outElev = df_elev['elev_smooth'][(df_elev['lcat']==nextTile) & (df_elev['along']==0)].iloc[0]
                df_elev, df_origCats, ditchReplace = smooth_elev(lcat, df_elev, df_origCats, ditchReplace, outElev=outElev, gradeFac=gradeFac)
                
                return df_elev, df_origCats, ditchReplace
            # If the next one has not yet been visited, do that one first
            else:
                
                return move_down(nextTile, df_elev, df_origCats, ditchReplace, gradeFac=gradeFac)
        

#%% 
df = pd.read_csv(path)
df_origCats = pd.read_csv(path_orig)
df_elev = pd.read_csv(path_elev)
df_attrs = pd.read_csv(path_attrs)
df_ditchElev = pd.read_csv(path_ditchElev)

outlets = df[(df['dist_ditch']<dist_ditch) | (df['dist_stream']<dist_stream)]

nonOutlets = df[(df['dist_ditch']>dist_ditch) & (df['dist_stream']>dist_stream) & (df['dist_tile'] < dist_tile)]
nonOutlets = nonOutlets[nonOutlets['cat'] != nonOutlets['tile_cat']]

tileConnects=pd.DataFrame({'from':nonOutlets['cat'], 'to':nonOutlets['tile_cat']})
graph = nx.from_pandas_edgelist(tileConnects, source='from', target='to', create_using=nx.DiGraph)  

### Use linear profile for the outlets
df_elev['elev_smooth'] = 0.1
df_origCats['visited'] = 0
ditchReplace = pd.DataFrame()

for lcat in df_origCats['cat']:
     while df_origCats['visited'][df_origCats['cat']==lcat].iloc[0] == 0:
         df_elev, df_origCats, ditchReplace = move_down(lcat, df_elev, df_origCats, ditchReplace)

df_origCats['long_visited'] = 0
df_origCats['grade'] = 1.0

for i in range(5):   

    tileHigher = df_elev[df_elev['elev_smooth'] > df_elev['elev']]
    lcats_tileHigher = sorted(set(tileHigher['lcat']))
    
    #print(lcats_tileHigher)
    
    df_origCats['visited'] = 0
    df_origCats['med_visited'] = 0
    
    df_elev2 = df_elev.copy()
    
    for lcat in lcats_tileHigher: 
        gradeFac = 1
        
        for i in range(9):
            df_tile = df_elev2[df_elev2['lcat']==lcat]
            
            if sum(df_tile['elev_smooth'] > df_tile['elev']) / len(df_tile) < 0.1:
   
                df_origCats.loc[df_origCats['visited']==1, 'med_visited'] = df_origCats['visited'][df_origCats['visited']==1]
                df_origCats.loc[(df_origCats['visited']==1) & (df_origCats['grade']>gradeFac), 'grade'] = gradeFac
                #print("fixed ", lcat, "grade ", gradeFac)
                break
            
            df_origCats['visited'] = df_origCats['med_visited']
            
            gradeFac = gradeFac - 0.1
            
            while df_origCats['visited'][df_origCats['cat']==lcat].iloc[0] == 0:
                df_elev2, df_origCats, ditchReplace = move_down(lcat, df_elev2, df_origCats, ditchReplace, gradeFac=gradeFac)
            
        if i==8:
            df_origCats.loc[df_origCats['visited']==1, 'med_visited'] = df_origCats['visited'][df_origCats['visited']==1]
            df_origCats.loc[(df_origCats['visited']==1), 'grade'] = gradeFac
    
    repeatVisits = df_origCats[(df_origCats['med_visited']==1) & (df_origCats['long_visited']==1)]
    
    setUnvisited = []
    for cat in repeatVisits['cat']:
        if graph.has_node(cat):
            allPred = list(nx.ancestors(graph, cat))
            
            setUnvisited += allPred
            
    setUnvisited = set(setUnvisited)
    df_origCats.loc[df_origCats['cat'].isin(setUnvisited), 'long_visited']=0

    df_elev = df_elev2.copy()
    df_origCats.loc[df_origCats['med_visited']==1, 'long_visited'] = df_origCats['med_visited'][df_origCats['med_visited']==1]
    
    #print(df_origCats[df_origCats['long_visited']==1])
    
df_origCats['visited'] = df_origCats['long_visited']
toUpdate = df_origCats[df_origCats['visited']==0]
update_lcats = sorted(set(toUpdate['cat']))
    
for lcat in update_lcats:
      while df_origCats['visited'][df_origCats['cat']==lcat].iloc[0] == 0:
          
          gradeFac = df_origCats['grade'][df_origCats['cat']==lcat].iloc[0]
          df_elev, df_origCats, ditchReplace = move_down(lcat, df_elev, df_origCats, ditchReplace, gradeFac=gradeFac)

df_elev.loc[df_elev['elev']-df_elev['elev_smooth'] < 0.001, 'elev_smooth']=df_elev['elev']-0.001
newElevPts1 = df_elev[['x','y','elev_smooth']]
newElevPts2 = ditchReplace[['x','y','elev_smooth']]
newElevPts = pd.concat((newElevPts1,newElevPts2),ignore_index=True)
    
newElevPts.to_csv(fileDir + 'tile_elevs.txt', index=False, columns=['x','y','elev_smooth'])   















# for lcat in range(1,652): 
#         df_tile = df_elev[df_elev['lcat']==lcat]
        
#         if sum(df_tile['elev_smooth'] > df_tile['elev']) / len(df_tile) > 0:
#             print(lcat)
            
# for lcat in range(1,652):
#     if graph.has_node(lcat) and len(list(graph.successors(lcat))) > 0:
#         des = list(graph.successors(lcat))[0]
        
#         thisProf = df_elev[df_elev['lcat']==lcat]
#         nextProf = df_elev[df_elev['lcat']==des]
        
#         diff = thisProf['elev_smooth'].iloc[-1] - nextProf['elev_smooth'].iloc[0]
        
#         if diff!=0:
#             print(lcat,des)
#             thisProf = thisProf - diff
            
        #thisProf = thisProf - 
    

    
# fig, axs = plt.subplots(1, 9, figsize=(15, 4))
# ax = axs.flat
    
#for (i,cat) in enumerate([1,319,486,269,270,261,582,97,581]):
# for (i,cat) in enumerate([636,220]):
#     prof = df_elev[df_elev['lcat']==cat]
    
#     # ax[i].plot(prof['along'], np.minimum(prof['elev'], \
#     #                                       prof['elev_smooth']), 'dimgray', linewidth=10, label='new DEM')
#     ax[i].plot(prof['along'], prof['elev'], 'k', label='land surface')
#     ax[i].plot(prof['along'], prof['elev_smooth'], 'cyan', label='tile')
    
    #ax[i].set_ylim([300,303])
        
#(sum(elev_smooth > tileProfile['elev']) / len(tileProfile) > 0.1) 
    
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
        
    
        
    
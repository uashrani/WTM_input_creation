# -*- coding: utf-8 -*-
"""
Created on Fri May 22 13:34:57 2026

@author: swimm
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

fileDir = "C:/Users/swimm/Downloads/"
path_ditchesElev = fileDir + "ditches_elevProfile.txt"

df_wNans=pd.read_csv(path_ditchesElev)
df = df_wNans[np.isnan(df_wNans['elev']) == False]

lcats = sorted(set(df['lcat']))

fig, axs = plt.subplots(6,6, figsize=(20,18))
ax = axs.flat

for (i,lcat) in enumerate(lcats):
    
    prof = df[df['lcat']==lcat]
    
    ax[i].plot(prof['along'], prof['elev'])
    
    ax[i].set_title(lcat)
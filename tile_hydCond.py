# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 10:47:02 2026

@author: swimm
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

fracFull = 0.1
cellRes = 4
subsurf = 1.5

path = "C:/Users/swimm/Downloads/tile_properties.txt"

df = pd.read_csv(path)

df.loc[df['tile_dim']<0, 'tile_dim'] = np.nan
df.loc[df['grade']<=0, 'grade'] = np.nan
df['slope'] = df['grade'] / 100
df['diam'] = df['tile_dim'] * .0254
df['radius'] = df['diam'] / 2

### Hydraulic radius calculation
df['theta'] = 2 * np.arccos((0.5 - fracFull) / 0.5)
df['filledArea'] = df['radius']**2 * (df['theta'] - np.sin(df['theta'])) / 2
df['peri'] = df['radius'] * df['theta']
df['Rh'] = df['filledArea'] / df['peri']

### Manning's n calculation
df['n'] = np.nan
df.loc[(df['tile_dim'] >= 3) & (df['tile_dim'] <= 8), 'n'] = .015
df.loc[(df['tile_dim'] > 8) & (df['tile_dim'] <= 12), 'n'] = .017
df.loc[(df['tile_dim'] > 12), 'n'] = .02

df['n_partial'] = (1.22 + 0.6*(fracFull - 0.1))*df['n']       # fracFull = 0.1 to 0.2
#df['n_partial'] = (1 + fracFull/0.3)*df['n']   # fracFull <= 0.03
#df['n_partial'] = (1.1 + (12/7)*(fracFull-0.03))*df['n']      # fracfull 

df['velocity'] = 1 / df['n_partial'] * (df['Rh'])**(2/3) * df['slope']**(1/2)

### Hydraulic conductivity
df['hydCond'] = df['velocity'] * (df['diam'] / cellRes) * (df['diam'] *  fracFull / subsurf)

df.loc[df['hydCond'] > 0.001, 'hydCond'] = 0.001

fig, ax = plt.subplots()

ax.hist(df['hydCond'], bins=20)
#ax.set_xlim([0,0.01])



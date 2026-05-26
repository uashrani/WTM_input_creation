# -*- coding: utf-8 -*-
"""
Created on Mon May 25 19:27:13 2026

@author: swimm
"""

ksat_hor = ['', 'B']
ksat_ver = ['', 'C1', 'C2']
decay = ['', 'D']

inPath = '/users/2/ashra061/WTM_inputs/minneopa_4m_tilingCombos/'
outPath = '/users/2/ashra061/WTM_outputs/tiling/'

paramsDict = {'run_type': 'equilibrium', \
              'fsm_on': '1', \
              'evap_mode': '1', \
              'infiltration_on': '1', \
              'runoff_ratio_on': '0', \
              'grid_type':'1', \
              'res_meters': '4', \
              'cells_per_degree': '120', \
              'southern_edge': '44', \
              'deltat': '900', \
              'total_cycles': '365', \
              'cycles_to_save': '365',
              'fdepth_a': '200', \
              'fdepth_b': '150', \
              'fdepth_fmin': '2', \
              'maxiter': '96',\
              'time_start': '0', \
              'time_end': '0', \
              'region': 'minneopa', \
              'supplied_wt': '0', \
              }

prefixes = []

for b in ksat_hor:
    for c in ksat_ver:
        for d in decay:
            prefix = ''
            prefix += b + c + d
            
            if prefix != '':
                prefixes += [prefix]
                
prefixes = ['A', 'AB'] + prefixes

for prefix in prefixes[:2]:
    # Create the config file
    fileName = 'Config_file_' + prefix + '.cfg'
    
    f = open(fileName, 'a')
    
    for key in paramsDict:
        f.write(key+'\t\t' + paramsDict[key] + '\n')
    f.write('surfdatadir\t\t'+inPath + prefix + '\n')
    f.write('textfilename\t\t'+outPath+prefix+'.txt\n')
    f.write('outfile_prefix\t\t'+outPath+prefix + '_')
    
    f.close()
                
    # And the jobscript
    fileName2 = 'script' + prefix + '.sh' 
    
    f2 = open(fileName2, 'a')
    
    f2.write('#!/bin/bash\n')
    f2.write('#SBATCH --time=96:00:00\n')
    f2.write('#SBATCH --ntasks=32\n')
    f2.write('#SBATCH --mem=32G\n')
    f2.write('#SBATCH --tmp=32G\n')
    f2.write('#SBATCH --mail-type=ALL\n')
    f2.write('#SBATCH --mail-user=ashra061@umn.edu\n')
    f2.write('#SBATCH -p msismall,msilong\n')
    
    f2.write('outPath="' + outPath + '"\n')
    f2.write('module load gdal\n')
    f2.write('module load petsc/3.24.5-gnu-rocky8\n')
    f2.write('ulimit -s unlimited\n')
    f2.write('export OMP_NUM_THREADS=32\n')
    outFile = outPath+'timing'+prefix+'.txt'
    f2.write('{ /usr/bin/time -v ./build/wtm.x ' + fileName + \
             ' -snes_mf -snes_type anderson -snes_stol 0.001; }' + \
                 '|& tee ' + outFile)
        
    f2.close()
                           


            
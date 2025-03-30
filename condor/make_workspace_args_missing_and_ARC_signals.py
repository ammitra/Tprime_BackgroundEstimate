'''
Create the arguments to make workspaces for the missing (before ARC review) and requested (during ARC review) signals.
'''
import glob, os, subprocess
import numpy as np 

MTs = np.arange(800,3100,100)
MPs = [75,100,125,175,200,250,350,450,500]
SRtf = '0x0'
CRtf = '0x0'

missing = {
    900: [250],
    1000: [175,250,350],
    1100: [125,250,350,500],
    1200: [100,125,350,500],
    1300: [100,200,500],
    1400: [100,500],
    1500: [350,450,500],
    1600: [175,500],
    1700: [125,175,450],
    1800: [175,200,250,350],
    1900: [200],
    2000: [75,125,200],
    2100: ['all'],
    2200: ['all'],
    2300: ['all'],
    2400: [75,100,250,250,500],
    2500: ['all'],
    2600: ['all'],
    2700: ['all'],
    2800: [75,175,200,250,350,450],
    2900: [200],
}

out = open('condor/workspace_args_missing_and_ARC_signals.txt','w')
for MT, MPHIs in missing.items():
    if MPHIs == ['all']:
        for MP in MPs:
            out.write(f'-w {MT}-{MP}_unblind_ -s {MT}-{MP} --SRtf {SRtf} --CRtf {CRtf} --make\n')
    else:
        for MP in MPHIs:
            out.write(f'-w {MT}-{MP}_unblind_ -s {MT}-{MP} --SRtf {SRtf} --CRtf {CRtf} --make\n')

out.close()
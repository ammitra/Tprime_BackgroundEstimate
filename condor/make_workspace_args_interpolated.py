import glob, os
import numpy as np

MTs = np.arange(800,3100,100)
MPs_generated = [150, 225, 275, 300, 325, 375, 400, 425, 475]

SRtf = '0x0'
CRtf = '0x0'
json = 'interpolated.json'

out = open('condor/workspace_args_tprime_interpolated.txt','w')
for MT in MTs:
    for MPHI in MPs_generated:
        out.write(f'-w {MT}-{MPHI}-INTERPOLATED_unblind_ -s {MT}-{MPHI} --SRtf {SRtf} --CRtf {CRtf} --json {json} --make\n')

'''
After running workspace creation and generating modified datacards, this script checks whether all workspaces were created properly
'''
import os
import numpy as np

MTs = np.arange(800,3100,100)
MPs = [75,100,125,175,200,250,350,450,500]

out = open('MISSING_SIGNALS.txt','w')

for MT in MTs:
    for MP in MPs:
        if not os.path.exists(f'{MT}-{MP}_unblind_fits/base.root'):
            out.write(f'{MT}-{MP}\n')
            print(f'{MT}-{MP}')

out.close()
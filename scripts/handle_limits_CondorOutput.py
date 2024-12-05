'''
Moves the FitDiagnostics Condor output files to their respective directories.
'''
import glob, os, ROOT
from TwoDAlphabet.helpers import execute_cmd
import argparse


'''
IMPORTANT - the limits have been calculated in two ways (using the postfit workspace):
    1) with the full SR+CR model
    2) with the CR masked and all CR-specific nuisances frozen and zeroed
The second method speeds up limit calculation by a factor of almost 200 and provides almost identical results. Therefore, the default will be to use these results. If desired, this can be changed by passing `--withCR` to the script.
'''
parser = argparse.ArgumentParser()
parser.add_argument("--withCR", dest='withCR', action='store_true', help='If passed as an argument, use the limits calculated with the ttbar CR. Otherwise, will use the limits calculated with the CR masked.')
args = parser.parse_args()

limits = glob.glob('higgsCombine_*.AsymptoticLimits.mH120.root')

for rootfile in limits:
    signal = rootfile.split('_')[1]
    execute_cmd(f'mv higgsCombine_{signal}*.AsymptoticLimits.mH120.root {signal}_unblind_fits/')

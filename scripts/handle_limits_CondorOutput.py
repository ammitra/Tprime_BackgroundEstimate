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

# Just hard-code this to look only for jobs without CR
limits = glob.glob('higgsCombine_*_noCR_workspace.AsymptoticLimits.mH120.root')

for rootfile in limits:
    signal = rootfile.split('_')[1]
    # First check whether the `limit` TTree has all 5 branches (+/-1,2 sigma expected and observed).
    # If it does not, this indicates that the AsymptoticLimits command failed for this mass point. 
    f = ROOT.TFile.Open(rootfile)
    limit = f.Get('limit')
    if limit.GetEntries() != 6:
        print(f'ERROR: AsymptoticLimit calculation for signal {signal} failed. Redo.')
        execute_cmd(f'mv {rootfile} FAILED_{rootfile}')
    else:
        execute_cmd(f'mv {rootfile} {signal}_unblind_fits/')
    f.Close()

'''
Moves the FitDiagnostics Condor output files to their respective directories.
'''
import glob, os, ROOT
from TwoDAlphabet.helpers import execute_cmd

failed = open('failed_FitDiagnostics.txt','w')

def make_postfit_workspace(fd):
    signal = fd.split('.root')[0].split('_')[-1]
    print(f'Making postfit workspace for signal {signal}...')
    w_f = ROOT.TFile.Open(f'higgsCombineTest.FitDiagnostics.mH120.{signal}.root','READ')
    w = w_f.Get('w')
    fr_f = ROOT.TFile.Open(f'fitDiagnosticsTest_{signal}.root')
    fr = fr_f.Get('fit_b')
    if (fr == None):
        print(f'Fit result "fit_b" does not exist in fit result file {fr_f}')
        failed.write(f'{signal}\n')
    else:
        myargs = ROOT.RooArgSet(fr.floatParsFinal())
        w.saveSnapshot('initialFit',myargs,True)
        fout = ROOT.TFile(f'initialFitWorkspace_{signal}.root', "recreate")
        fout.WriteTObject(w, 'w')
        fout.Close()


cards = glob.glob('card_*.txt')
roots = glob.glob('fitDiagnosticsTest_*.root')

for rootfile in roots:
    signal = rootfile.split('.root')[0].split('_')[-1]
    # check if the signal has cards as well 
    if f'card_{signal}.txt' not in cards: 
        print(f'ERROR: signal {signal} has a fitDiagnostics file but not a card...')
        failed.write(f'{signal}\n')
    else:
        make_postfit_workspace(rootfile)
        # Move all the files to the proper workspace
        workspace = f'{signal}_unblind_fits/'
        for outputfile in [f'card_{signal}.txt', f'fitDiagnosticsTest_{signal}.root', f'initialFitWorkspace_{signal}.root',f'higgsCombineTest.FitDiagnostics.mH120.{signal}.root']:
            execute_cmd(f'mv {outputfile} {workspace}')
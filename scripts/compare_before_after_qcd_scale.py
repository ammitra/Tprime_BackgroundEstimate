'''
Script to compare the limits before and after adding the QCD scale uncertainty for ttbar
'''
import ROOT
import glob 
import os 

fitDirs = glob.glob('*_fits/')
for fitDir in fitDirs:
    if 'backup' in fitDir:
        continue
    signal = fitDir.split('_')[0]
    
    AL_file_name = f'higgsCombine_{signal}_noCR_workspace.AsymptoticLimits.mH120.root'    
    
    AL_file_new = f'{fitDir}{AL_file_name}'
    AL_file_old = f'results_unblinded_ANv14_Paperv3_noQCDscale/{fitDir}{AL_file_name}'

    if not os.path.exists(AL_file_new):
        continue
    if not os.path.exists(AL_file_old):
        print(f'ERROR: AsymptoticLimits for signal {signal} does not exist in old directory...')
        continue 

    fOld = ROOT.TFile.Open(AL_file_old)
    fNew = ROOT.TFile.Open(AL_file_new)

    tOld = fOld.Get('limit')
    tNew = fNew.Get('limit')

    nOld = tOld.GetEntries()
    nNew = tNew.GetEntries()

    if (nOld != 6):
        print(f'ERROR: AsymptoticLimits for signal {signal} only has {nOld} entries [OLD]')
        continue
    if (nNew != 6):
        print(f'ERROR: AsymptoticLimits for signal {signal} only has {nOld} entries [NEW]')
        continue

    print(f'-------------{signal}-------------')
    for i in range(6):
        d = {0:'-2 sigma expected',1:'-1 sigma expected',2:'Median expected',3:'+1 sigma expected',4:'+2 sigma expected',5:'Observed'}

        print(f'{d[i]} limit:')
        tOld.GetEntry(i)
        tNew.GetEntry(i)

        lOld = tOld.limit
        lNew = tNew.limit

        print(f'[OLD] {lOld}')
        print(f'[NEW] {lNew}')
        diff = (abs(lNew - lOld) / lOld) * 100.0
        if (lNew < lOld):
            print(f'\tNew limits are stronger by {round(diff,2)}%')
        else:
            print(f'\tNew limits are weaker by {round(diff,2)}%')
    print('')

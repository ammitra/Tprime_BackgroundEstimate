'''
From a 2DAlphabet workspace, generates statistical uncertainty templates for a given 
process. The templates will be generated such that every bin in the distribution is 
fixed except for the bin under consideration, which will be floated up/down by the MC
statistical uncertainty. Output file format will be:
    - <process>_<year>_MCstats.root
        - MHvsMTH_<region>__mcstats_<binX>_<binY>_up
        - MHvsMTH_<region>__mcstats_<binX>_<binY>_down

Then the 2DAlphabet format would be 
"GLOBAL": {
    "MCStatsPath": "relative/path/to/MCstatsFile/",
    "MCStatsFile": "$process_MCstats.root",
    "HIST_UP": "MHvsMTH_$region__$syst_up",
    "HIST_DOWN": "MHvsMTH_$region__$syst_down",
}
"SYSTEMATICS": {
    "mcstats_<binX>_<binY>": {
        "UP": "MCStatsPath/MCStatsFile:HIST_UP",
        "DOWN": "MCStatsPath/MCStatsFile:HIST_DOWN",
        "SIGMA": 1.0
    },
    ...
}
'''
import ROOT
import numpy as np

regions = ['SR_fail','SR_pass','ttbarCR_fail','ttbarCR_pass']
organized_hists = ROOT.TFile.Open('organized_hists.root','READ')

syst_names = []

for process in ['ttbar']:
    for year in ['16','16APV','17','18']:
        f = ROOT.TFile.Open(f'{process}_{year}_MCstats.root','RECREATE')
        f.cd()
        for region in regions:
            # Have to do some nonsense and make dummy histograms for 2DAlphabet. It needs a histogram for all regions.
            for rDummy in regions:
                h = organized_hists.Get(f'{process}_{year}_{region}_FULL')
                print(f'Generating MC stats templates for region {region}, 20{year}  [rDummy = {rDummy}]')
                hNom = h.Clone(f'MHvsMTH_{region}__nominal')
                hNom.Write()
                nx = h.GetNbinsX()
                ny = h.GetNbinsY()
                for i in range(1,nx+1):
                    for j in range(1,ny+1):
                        nom = h.GetBinContent(i,j)
                        unc = np.sqrt(nom)
                        for var in ['up','down']:
                            hBinVar = hNom.Clone(f'MHvsMTH_{region}__{rDummy}_mcstats_{i}_{j}_{var}')
                            if rDummy == region:
                                if var == 'up':
                                    hBinVar.SetBinContent(i,j, nom+unc)
                                else:
                                    new = nom-unc 
                                    if new < 0: new = 0.0
                                    hBinVar.SetBinContent(i,j, new)
                                syst_name = f'{region}_mcstats_{i}_{j}'
                                # Only make an entry in the JSON for this nuisance if the nominal value is less than 20 events (in the SR, where we have lower stats) and greater than zero 
                                if ('SR' in region):
                                    if (nom <= 20.0) and (nom > 0.0):
                                        if 'pass' in syst_name:
                                            #print(f'\t{syst_name} = {nom}')
                                            syst_names.append(syst_name)
                                else:
                                    # make CR nuisances for all bins in pass, b/c the statistcs are much higher
                                    if 'pass' in syst_name:
                                        syst_names.append(syst_name)
                            else:
                                # Dummy histogram, all zeros 
                                hBinVar.SetBinContent(i,j,0.0)
                            hBinVar.Write()

base_syst_str = '''
        "%s": {
            "UP": "MCStatsPath/MCStatsFile:HIST_UP",
            "DOWN": "MCStatsPath/MCStatsFile:HIST_DOWN",
            "SIGMA": 1.0
        },
'''
out = open('mcstat_systs.txt','w')
print('Writing MCstat systematics to file...')
all_systs = list(dict.fromkeys(syst_names))
#print('"'+'","'.join(all_systs)+'"')
out.write('"'+'","'.join(all_systs)+'"')
out.write('\n')
for syst in all_systs:
    #print(base_syst_str%(syst))
    out.write(base_syst_str%(syst)+'\n')
out.close()
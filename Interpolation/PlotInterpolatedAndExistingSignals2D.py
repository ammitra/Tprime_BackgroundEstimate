'''
Plots the 9 mPhi nominal histograms for every mT. 
Used to see which mass points should be interpolated and which should not be.
'''
import ROOT
import matplotlib
import matplotlib.pyplot as plt
import mplhep as hep
import matplotlib.ticker as mticker
import numpy as np
import uproot

MTs = [800,  900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000]
MPs_existing  = [75, 100, 125, 175, 200, 250, 350, 450, 500]
MPs_generated = [150, 225, 275, 300, 325, 375, 400, 425, 475]
MPs = MPs_existing + MPs_generated
MPs.sort()

bad = {800: 125, 900: 175, 1000: 200, 1100: 250, 1200: 250, 1300: 250, 1400: 250, 1500: 250, 1600: 250, 1700: 350, 1800: 350, 1900: 350, 2000: 350, 2100: 350, 2200: 350, 2300: 350, 2400: 350, 2500: 350, 2600: 350, 2700: 350, 2800: 350, 2900: 350, 3000: 350}


for MT in MTs:
    plt.style.use(hep.style.CMS)
    hep.style.use("CMS")
    fig, axes = plt.subplots(6, 3, figsize=(15,15), dpi=150, sharex=True, sharey=True)
    axes = axes.flatten()
    for i, MP in enumerate(MPs):
        year = 18
        print(f'Generating 3x3 plot for {MT}-{MP}, 20{year}')
        try:
            f = uproot.open(f'root://cmseos.fnal.gov//store/user/ammitra/topHBoostedAllHad/selection/THselection_TprimeB-{MT}-{MP}_{year}.root')
        except:
            print(f'File for {MT}-{MP}, 20{year} not found..')
        try:
            hist = f['MHvsMTH_SR_pass__nominal']
        except:
            print(f'Hist "MHvsMTH_SR_pass__nominal" for {MT}-{MP}, 20{year} not found..')
        hep.hist2dplot(hist, ax=axes[i], flow=None, cbar=None, rasterized=True, linewidth=0, cmap='viridis')
        axes[i].text(0.4, 0.9, r'$m_{\phi} = %s$ GeV'%(MP), color='white', fontsize='small', transform=axes[i].transAxes, ha='center', va='top')
        if MP in MPs_generated:
            if MP > bad[MT] and MP in MPs_generated:
                if MT>=1800:
                    axes[i].text(0.4, 0.3, '(interpolated, not used)', color='red', fontsize='small', transform=axes[i].transAxes, ha='center', va='top')
                else:
                    axes[i].text(0.4, 0.6, '(interpolated, not used)', color='red', fontsize='small', transform=axes[i].transAxes, ha='center', va='top')
            else:
                axes[i].text(0.4, 0.6, '(interpolated)', color='white', fontsize='small', transform=axes[i].transAxes, ha='center', va='top')

        if i == 2:
            lumiText = "13 TeV (2018)" 
            hep.cms.lumitext(lumiText,ax=axes[i])
        if i == 0:
            hep.cms.text("Simulation Preliminary",loc=0,ax=axes[i])
            axes[i].set_ylabel(r'$m_{T^\prime}^{rec}$ [GeV]', loc='top')
        if i == 8:
            axes[i].set_xlabel(r'$m_{\phi}^{rec}$ [GeV]', loc='right')

    fig.subplots_adjust(wspace=0, hspace=0)

    plt.savefig(f'plots/INTERP_AND_EXISTING_mt-{MT}.pdf', bbox_inches='tight')

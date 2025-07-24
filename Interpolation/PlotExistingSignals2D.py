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

for MT in MTs:
    plt.style.use(hep.style.CMS)
    hep.style.use("CMS")
    fig, axes = plt.subplots(3, 3, figsize=(15,15), dpi=150, sharex=True, sharey=True)
    axes = axes.flatten()
    for i, MP in enumerate(MPs_existing):
        year = 18
        print(f'Generating 3x3 plot for {MT}-{MP}, 20{year}')
        try:
            f = uproot.open(f'root://cmseos.fnal.gov//store/user/ammitra/topHBoostedAllHad/selection/THselection_TprimeB-{MT}-{MP}_{year}.root')
        except:
            print(f'File for {MT}-{MP}, 20{year} not found..')
        hist = f['MHvsMTH_SR_pass__nominal']
        hep.hist2dplot(hist, ax=axes[i], flow=None, cbar=None, rasterized=True, linewidth=0, cmap='viridis')
        axes[i].text(0.4, 0.9, r'$m_{\phi} = %s$ GeV'%(MP), color='white', fontsize='small', transform=axes[i].transAxes, ha='center', va='top')

        if i == 2:
            lumiText = "13 TeV (2018)" 
            hep.cms.lumitext(lumiText,ax=axes[i])
        if i == 0:
            hep.cms.text("Simulation Preliminary",loc=0,ax=axes[i])
            axes[i].set_ylabel(r'$m_{T^\prime}^{rec}$ [GeV]', loc='top')
        if i == 8:
            axes[i].set_xlabel(r'$m_{\phi}^{rec}$ [GeV]', loc='right')

    fig.subplots_adjust(wspace=0, hspace=0)

    plt.savefig(f'plots/mt-{MT}.pdf', bbox_inches='tight')

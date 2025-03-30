'''
Script to observe the effect of QCD scale variations on signal MC templates 
'''
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import ROOT as r
from PyHist import PyHist
import copy
import matplotlib
from TwoDAlphabet.plotstyle import *

f = r.TFile.Open('root://cmseosmgm01.fnal.gov:1094//store/user/ammitra/topHBoostedAllHad/selection/THselection_TprimeB-1800-125_17.root')

for syst in ['renormalization','factorization']:
    hNom = f.Get('MHvsMTH_SR_pass__nominal')
    hUp  = f.Get(f'MHvsMTH_SR_pass__QCDscale_{syst}_up')
    hDn  = f.Get(f'MHvsMTH_SR_pass__QCDscale_{syst}_down')

    for proj in ['X','Y']:
        hNom1D = getattr(hNom,'Projection'+proj)()
        hUp1D  = getattr(hUp,'Projection'+proj)()
        hDn1D  = getattr(hDn,'Projection'+proj)()

        nom = PyHist(hNom1D)
        up  = PyHist(hUp1D)
        down = PyHist(hDn1D)

        plt.style.use([hep.style.CMS])
        fig, (ax, rax) = plt.subplots(
            2, 1, figsize=(12, 10), dpi=200, gridspec_kw={"height_ratios": [3, 1], "hspace": 0.1}, sharex=True
        )

        edges = nom.bin_edges

        hep.histplot(nom.bin_values, edges, ax=ax, stack=False, label='Nominal', histtype='step', facecolor=None, edgecolor='black')
        hep.histplot(down.bin_values, edges, ax=ax, stack=False, label=r'$+1\sigma$', histtype='step', facecolor=None, edgecolor='red')
        hep.histplot(up.bin_values, edges, ax=ax, stack=False, label=r'$-1\sigma$', histtype='step', facecolor=None, edgecolor='blue')
        
        rUp = nom.bin_values / down.bin_values
        rDn = nom.bin_values / up.bin_values

        rax.set_ylim(0,2)

        hep.histplot(rUp, edges, ax=rax, stack=False, label='Nom/Up', histtype='step', facecolor=None, edgecolor='red')
        hep.histplot(rDn, edges, ax=rax, stack=False, label='Nom/Dn', histtype='step', facecolor=None, edgecolor='blue')

        ax.legend(loc='best')
        rax.legend(loc='best')

        fig.savefig(f'{syst}_{proj}.png')

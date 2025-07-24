'''
Plot the shapes of the generated and existing signals to compare them.
'''
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import ROOT as r
from PyHist import PyHist
import copy
import matplotlib
import ROOT
from matplotlib.lines import Line2D


MTs = [800,  900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000]
MPs_existing  = [75, 100, 125, 175, 200, 250, 350, 450, 500]
MPs_generated = [150, 225, 275, 300, 325, 375, 400, 425, 475]
MPs = MPs_existing + MPs_generated
MPs.sort()

def getPyHist(inFile, hName, proj):
    try:
        f = ROOT.TFile.Open(inFile,'READ')
    except:
        print(f'{inFile} does not exist...')
        return None
    h = f.Get(hName)
    if not h:
        return None
    h1D = getattr(h, f'Projection{proj}')()
    h1D = PyHist(h1D)
    f.Close()
    return h1D

def plot(mT, proj):
    axis_label = r'$m_{\phi}^{rec}$ [GeV]'
    outFileName = f''

    sigs       = [] # List of arrays representing signal histo
    signames   = [] # List of signal names
    sig_colors = [] # List of colors (blue=existing, red=generated)

    edges = []

    # Loop over all signals
    for i, mP in enumerate(MPs):
        print(f'Obtaining histo for {mT}-{mP}...')
        if mP in MPs_existing:
            existing = True
            sig_colors.append("#3f90da")
        else:
            existing = False
            sig_colors.append("#bd1f01")

        sigsRun2 = []

        for year in ['16','16APV','17','18']:
            if existing:
                fName = f'root://cmsxrootd.fnal.gov//store/user/ammitra/topHBoostedAllHad/selection/THselection_TprimeB-{mT}-{mP}_{year}.root'
                hName = 'MHvsMTH_SR_pass__nominal'
            else:
                fName = f'backup_10June2025_working_but_not_good/rootfiles/THselection_TprimeB-{mT}-{mP}_{year}_INTERPOLATED.root'
                hName = 'MHvsMTH_SR_pass__nominal'
                print('\tGENERATED')

            ph = getPyHist(fName, hName, proj)
            if not ph:
                print(f'{fName} does not exist')
                continue
            
            sigsRun2.append(ph)

            # sigs.append(ph.bin_values)
            # signames.append(r'$(%s,%s)$'%(mT,mP))
            # SF = 50 if proj == 'X' else 100
            # edges.append(ph.bin_edges + i*SF)

        dummy = np.zeros_like(sigsRun2[0].bin_values)
        SF = 200 if proj == 'X' else 600
        edges.append(sigsRun2[0].bin_edges + i*SF)
        for ph in sigsRun2:
            ph.divide_by_bin_width()
            dummy += ph.bin_values
        sigs.append(dummy)
        signames.append(r'$(%s,%s)$'%(mT,mP))



    plt.style.use([hep.style.CMS])
    fig, ax = plt.subplots(dpi=200)

    for i, sig in enumerate(sigs):
        hep.histplot(sig, edges[i], ax=ax, label=signames[i], histtype='step', edgecolor=sig_colors[i])
        if proj == 'X':
            # Add arrow to describe which signal is which 
            phimass = signames[i].split(',')[-1].split(')')[0]
            ax.annotate(
                signames[i],
                xy     = (int(phimass) + i*SF, np.max(sig)),  xycoords='data',
                xytext = (80, 40), textcoords='offset points',
                arrowprops=dict(arrowstyle="<-",connectionstyle="arc3,rad=.2"),
                fontsize=10
            )


    # Format
    #ax.set_yscale('log')
    ax.margins(x=0)
    lumiText = r"138 $fb^{-1}$ (13 TeV)"    
    hep.cms.lumitext(lumiText,ax=ax)
    hep.cms.label(loc=0, ax=ax, label='', rlabel='', data=False)
    if proj == 'X':
        ax.set_xlabel(r'$m_{\phi}^{rec}$ [GeV]')
        ax.set_ylabel('Events')
    else:
        ax.set_xlabel(r'$m_{T^\prime}^{rec}$ [GeV]')
        ax.set_ylabel('Events')
    ax.text(0.5, 0.65, 'SR Pass', fontsize=30, va='top', ha='left', transform=ax.transAxes, fontproperties='Tex Gyre Heros:bold')
    ax.text(0.5, 0.6, r'$m_{T^\prime}^{rec}=%s$ GeV'%(mT), fontsize=20, va='top', ha='left', transform=ax.transAxes)

    custom_lines = [
        Line2D([0], [0], color="#3f90da", lw=1),
        Line2D([0], [0], color="#bd1f01", lw=1),
    ]
    ax.legend(custom_lines, ['Existing', 'Interpolated'])

    plt.savefig(f'plots/ExistingAndGenerated-{mT}_{proj}.pdf')

# for MT in MTs:
#     plot(MT, 'X')
#     plot(MT, 'Y')

plot(900, 'X')
plot(900, 'Y')
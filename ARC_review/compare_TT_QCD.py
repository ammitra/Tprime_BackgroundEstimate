import ROOT
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mplhep as hep
from collections import OrderedDict
import array
import subprocess
from TwoDAlphabet.binning import convert_to_events_per_unit, get_min_bin_width

# Options for plotting
stack_style = {
    'edgecolor': (0, 0, 0, 0.5),
}
errorbar_style = {
    'linestyle': 'none',
    'marker': '.',      # display a dot for the datapoint
    'elinewidth': 2,    # width of the errorbar line
    'markersize': 20,   # size of the error marker
    'capsize': 0,       # size of the caps on the errorbar (0: no cap fr)
    'color': 'k',       # black 
}

# Function stolen from https://root-forum.cern.ch/t/trying-to-convert-rdf-generated-histogram-into-numpy-array/53428/3
def hist2array(hist, include_overflow=False, return_errors=False):
    '''Create a numpy array from a ROOT histogram without external tools like root_numpy.

    Args:
        hist (TH1): Input ROOT histogram
        include_overflow (bool, optional): Whether or not to include the under/overflow bins. Defaults to False. 
        return_errs (bool, optional): Whether or not to return an array containing the sum of the weights squared. Defaults to False.

    Returns:
        arr (np.ndarray): Array representing the ROOT histogram
        errors (np.ndarray): Array containing the sqrt of the sum of weights squared
    '''
    hist.BufferEmpty()
    root_arr = hist.GetArray()
    if isinstance(hist, ROOT.TH1):
        shape = (hist.GetNbinsX() + 2,)
    elif isinstance(hist, ROOT.TH2):
        shape = (hist.GetNbinsY() + 2, hist.GetNbinsX() + 2)
    elif isinstance(hist, ROOT.TH3):
        shape = (hist.GetNbinsZ() + 2, hist.GetNbinsY() + 2, hist.GetNbinsX() + 2)
    else:
        raise TypeError(f'hist must be an instance of ROOT.TH1, ROOT.TH2, or ROOT.TH3')

    # Get the array and, optionally, errors
    arr = np.ndarray(shape, dtype=np.float64, buffer=root_arr, order='C')
    if return_errors:
        errors = np.sqrt(np.ndarray(shape, dtype='f8', buffer=hist.GetSumw2().GetArray()))

    if not include_overflow:
        arr = arr[tuple([slice(1, -1) for idim in range(arr.ndim)])]
        if return_errors:
            errors = errors[tuple([slice(1, -1) for idim in range(errors.ndim)])]

    if return_errors:
        return arr, errors
    else:
        return arr

def plot_same(
    outname,
    bkgs = {},
    edges = None,
    logyFlag = False,
    title = '',
    xtitle = '',
    ytitle_ax = '',
    ytitle_rax = '',
    subtitle = '',
    lumiText = r'$138 fb^{-1} (13 TeV)$',
    extraText = 'Preliminary',
    units = 'GeV'):

    plt.style.use([hep.style.CMS])
    fig, (ax, rax) = plt.subplots(
        2, 1, figsize=(12, 10), dpi=100, gridspec_kw={"height_ratios": [3, 1], "hspace": 0.1}, sharex=True
    )

    # Main plot
    bkg_list = [] # fail, pass
    for key, val in bkgs.items(): # latex name, (array, color)
        arr = val[0]
        color = val[1]
        hep.histplot(arr[1:], edges[1:], color=color, ax=ax, label=key)
        bkg_list.append(arr[1:])

    if logyFlag:
        ax.set_ylim(0.001, bkg_list[0].max()*1e5)
        ax.set_yscale('log')

    # Ratio plot
    ratio = bkg_list[0]/bkg_list[1]
    hep.histplot(ratio, edges[1:], color='black', ax=rax)
    rax.set_ylabel(ytitle_rax)
    rax.margins(x=0)
    rax.grid(axis='y')

    rax.set_xlabel(xtitle)
    ax.set_title(title,loc='left')
    ax.legend(loc='best')
    ax.margins(x=0)
    hep.cms.label(loc=2, ax=ax, label=extraText, rlabel='', data=True) # multiline, upper left corner
    hep.cms.lumitext(lumiText,ax=ax)
    plt.savefig(outname)


def getProjn(h,proj):
    hprojn = getattr(h,f'Projection{proj}')()
    hprojn.SetDirectory(0)
    return hprojn

binningX = np.array([60,80,100,120,140,160,180,200,220,260,300,560])
binningY = np.array([800,900,1000,1100,1200,1300,1400,1500,1700,2000,3500])

'''
Requested plots:
    * Ratio of each background Fail/Pass in QCD CR, TT CR and SR                        
    * Ratio of TT background Fail/Fail and Pass/Pass from TT CR to SR, QCD CR to SR     <------------------------
    * Ratio of QCD background Fail/Fail and Pass/Pass from TT CR to SR, QCD CR to SR    <------------------------
'''
# Plot ratio of given bkg in Fail/Fail and Pass/Pass from TTCR to SR, QCD CR to SR
# The f_SR file will contain the TT CR distributions as well.
for bkg in ['ttbar','Background']:
    f_CR = ROOT.TFile.Open('CR_fits/CRfits/TprimeB-1800-125-CR0x0_area/plots_fit_b/all_plots.root','READ')
    f_SR = ROOT.TFile.Open('../1800-125_unblind_fits/TprimeB-1800-125-SR0x0-CR0x0_area/plots_fit_b/all_plots.root','READ')
    
    # Get name of all histograms of this bkg
    postfit_CR = [i.GetName() for i in f_CR.GetListOfKeys() if ('postfit_2D' in i.GetName() and f'{bkg}_' in i.GetName())]
    postfit_SR = [i.GetName() for i in f_SR.GetListOfKeys() if ('postfit_2D' in i.GetName() and f'{bkg}_' in i.GetName())]

    # Get test histograms for X and Y projections
    dummyH = f_CR.Get(postfit_CR[0]).Clone()
    X = dummyH.ProjectionX(); X.Reset(); X = hist2array(X)
    Y = dummyH.ProjectionY(); Y.Reset(); Y = hist2array(Y)

    # Create plots
    for region in ['fail','pass']:
        for proj in ['X','Y']:
            SR   = [np.zeros_like(X if proj == 'X' else Y),'red']
            CR   = [np.zeros_like(X if proj == 'X' else Y),'blue']
            TTCR = [np.zeros_like(X if proj == 'X' else Y),'green']
            for histname in postfit_CR + postfit_SR:
                if f'_SR_{region}_' in histname:
                    h = f_SR.Get(histname)
                elif f'_CR_{region}_' in histname:
                    h = f_CR.Get(histname)
                elif f'_ttbarCR_{region}_' in histname:
                    h = f_SR.Get(histname)
                else:
                    continue

                h = getProjn(h,proj)
                min_width = get_min_bin_width(h)
                h = convert_to_events_per_unit(h)
                h = hist2array(h)

                if f'_SR_{region}_' in histname:
                    SR[0] += h
                elif f'_CR_{region}_' in histname:
                    CR[0] += h
                elif f'_ttbarCR_{region}_' in histname:
                    TTCR[0] += h           

            # Plot 
            if bkg == 'Background': bkgName = 'QCD'
            elif bkg == 'ttbar': bkgName = r'$t\bar{t}$'
            xtitle = r'$m_{\phi}$ [GeV]' if proj == 'X' else r'$m_{t\phi}$ [GeV]'
            for logyFlag in [True,False]:
                for r in ['QCD CR', 'TT CR']:
                    print(f'Plotting {region}/{region} from {r} to SR, {proj} projection, {"logy" if logyFlag else "linear"}')

                    if bkg == 'Background': bkgName = 'QCD'
                    elif bkg == 'WJets': bkgName = r'W+jets'
                    elif bkg == 'ZJets': bkgName = r'Z+jets'
                    elif bkg == 'ttbar': bkgName = r'$t\bar{t}$'

                    rname = '_'.join(r.split(' '))
                    plot_same(
                        outname    = f'plots/regions/{bkg}_{region}_{proj}_{rname}_{"logy" if logyFlag else ""}.jpg',
                        bkgs       = {r:CR if r=='QCD CR' else TTCR,'SR':SR},
                        edges      = binningX if proj == 'X' else binningY,
                        logyFlag   = logyFlag,
                        title      = f'{bkgName}, {region}/{region}, {r} to SR',
                        xtitle     = xtitle,
                        ytitle_ax  = f'Events / {min_width} GeV',
                        ytitle_rax = f'{r}/SR',
                        subtitle   = '',
                        lumiText   = r'$138 fb^{-1} (13 TeV)$',
                        extraText  = 'Preliminary',
                        units      = 'GeV'
                    )
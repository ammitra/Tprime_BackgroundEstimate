'''
Function to plot the X and Y projections of the postfit background estimate as single plots rather than slices. For use in the paper instead of the 3x2 plots
'''
import ROOT, uproot
import matplotlib.pyplot as plt
import numpy as np
import mplhep as hep
from TwoDAlphabet.binning import convert_to_events_per_unit, get_min_bin_width
from collections import OrderedDict

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

def getProjn(h,proj):
    hprojn = getattr(h,f'Projection{proj}')()
    hprojn.SetDirectory(0)
    return hprojn

def poisson_conf_interval(k):
    """
    Calculate Poisson (Garwood) confidence intervals using ROOT's TH1 with kPoisson error option.
    
    Parameters:
    k (array): The number of counts (events) per bin.

    Returns:
    lower (array): Bin count - lower error.
    upper (array): Bin count + upper error.
    """
    lower = np.zeros_like(k, dtype=float)
    upper = np.zeros_like(k, dtype=float)
    #Temp hist to exploit ROOT's built-in CI calculating function
    hist = ROOT.TH1F("hist_delete", "", 1, 0, 1)
    hist.SetBinErrorOption(ROOT.TH1.kPoisson)
    hist.Sumw2()

    for i, count in enumerate(k):
        hist.SetBinContent(1, count)
        
        lower[i] = hist.GetBinContent(1) - hist.GetBinErrorLow(1)
        upper[i] = hist.GetBinContent(1) + hist.GetBinErrorUp(1)
        
    hist.Delete()
    
    return lower, upper    

def plot_stack(
    outname,
    data,
    bkgs = {},
    sigs = {},
    edges = None,
    title = '',
    xtitle = '',
    ytitle = '',
    subtitle = '',
    totalBkg = None,
    logyFlag = False,
    lumiText = r'$138 fb^{-1} (13 TeV)$',
    extraText = 'Preliminary',
    units = 'GeV'):

    plt.style.use([hep.style.CMS])
    fig, (ax, rax) = plt.subplots(
        2, 1, figsize=(12, 10), dpi=100, gridspec_kw={"height_ratios": [3, 1], "hspace": 0.1}, sharex=True
    )


    bkg_stack = np.vstack([val[0] for key, val in bkgs.items()])
    bkg_stack = np.hstack([bkg_stack, bkg_stack[:,-1:]])
    bkg_stack = np.hstack([bkg_stack])
    bkg_colors = [val[1] for key, val in bkgs.items()]
    bkg_labels = [key for key, val in bkgs.items()]

    sig_stack = np.vstack([val[0] for key, val in sigs.items()])
    sig_stack = np.hstack([sig_stack, sig_stack[:,-1:]])
    sig_stack = np.hstack([sig_stack])
    sig_colors = [val[1] for key, val in sigs.items()]
    sig_labels = [key for key, val in sigs.items()]

    ax.stackplot(edges, bkg_stack, labels=bkg_labels, colors=bkg_colors, step='post', **stack_style)
    ax.set_ylabel(f'Events / bin width $(GeV^{-1})$')
    ax.set_ylabel(ytitle)
    
    # plot data 
    lower_errors, upper_errors = poisson_conf_interval(data)
    yerr = [data - lower_errors, upper_errors - data]
    bin_centers = (edges[:-1] + edges[1:])/2
    ax.errorbar(x=bin_centers, y=data, yerr=np.abs(yerr), xerr=None, label='Data', **errorbar_style)

    # plot signals
    for key,val in sigs.items():
        sigarr = val[0] #/ bin_widths
        scaling = 10
        ax.step(x=edges, y=np.hstack([sigarr,sigarr[-1]])*scaling, where='post', color=val[1], label=r'%s \times %s'%(key,scaling))
    
    if logyFlag:
        if totalBkg.max() >= data.max():
            ax.set_ylim(0.001, totalBkg.max()*1e5)
        else:
            ax.set_ylim(0.001, data.max()*1e5)
        ax.set_yscale('log')
    else:
        if totalBkg.max() >= data.max():
            ax.set_ylim(0, totalBkg.max()*1.5)
        else:
            ax.set_ylim(0, data.max()*1.5)

    ax.legend(loc='best')
    ax.margins(x=0)
    hep.cms.label(loc=0, ax=ax, label=extraText, rlabel='', data=True)
    hep.cms.lumitext(lumiText,ax=ax)

    # now plot ratio of data/prediction
    bkg_nonzero = totalBkg.copy()
    bkg_nonzero[bkg_nonzero==0] = 1e-2
    data_over_pred = data / bkg_nonzero
    rax.set_ylim([0, 2])
    hep.histplot(data_over_pred, edges, histtype='errorbar', color='black', ax=rax)
    rax.set_ylabel('Data/Pred.')
    rax.margins(x=0)
    rax.grid(axis='y')
    rax.set_xlabel(xtitle)


    plt.savefig(outname)


##################################################################
# Main code
##################################################################
f_shapes = '../results_unblinded_ANv14_Paperv3_noQCDscale/1800-125_unblind_fits/TprimeB-1800-125-SR0x0-CR0x0_area/plots_fit_b/all_plots.root'

f = ROOT.TFile.Open(f_shapes,'READ')

histlist = [i.GetName() for i in f.GetListOfKeys() if ('postfit_2D' in i.GetName() and 'ttbarCR' not in i.GetName())]

print(histlist)

# get test histograms for X and Y projections
dummyH = f.Get(histlist[0]).Clone()

dummyX = dummyH.ProjectionX(); dummyX.Reset(); dummyX = hist2array(dummyX)
dummyY = dummyH.ProjectionY(); dummyY.Reset(); dummyY = hist2array(dummyY)

binningX = np.array([60,80,100,120,140,160,180,200,220,260,300,560])
binningY = np.array([800,900,1000,1100,1200,1300,1400,1500,1700,2000,3500])

for region in ['SR_fail','SR_pass']:
    for proj in ['X','Y']:

        tt   = [np.zeros_like(dummyX if proj == 'X' else dummyY), '#e42536'] # red
        vj   = [np.zeros_like(dummyX if proj == 'X' else dummyY), '#5790fc'] # blue
        qcd  = [np.zeros_like(dummyX if proj == 'X' else dummyY), '#f89c20'] # orange
        sig  = [np.zeros_like(dummyX if proj == 'X' else dummyY), '#7a21dd'] # purple
        data = [np.zeros_like(dummyX if proj == 'X' else dummyY), 'black']
        tot  = [np.zeros_like(dummyX if proj == 'X' else dummyY), 'black']

        for histname in histlist:
            if region not in histname: continue

            h = f.Get(histname)
            h = getProjn(h,proj)
            min_width = get_min_bin_width(h)
            print(f'min width {min_width}')
            h_converted = convert_to_events_per_unit(h, min_width)
            hfinal = hist2array(h_converted)

            # Append to the relevant process
            if 'ttbar' in histname:
                tt[0] += hfinal
            elif 'Jets' in histname:
                vj[0] += hfinal
            elif 'TprimeB' in histname:
                sig[0] += hfinal
            elif 'Background' in histname:
                qcd[0] += hfinal
            elif 'data' in histname:
                data[0] += hfinal
            elif 'Total' in histname:
                tot[0] += hfinal

        print(f'{region}_{proj}----------------------------------------------------------------------------------------------------------')
        print(data)
        print(tt)
        print(vj)
        print(sig)
        print(qcd)
        print('----------------------------------------------------------------------------------------------------------')

        bkgHists_nom = OrderedDict(
            [
                (r'$t\bar{t}$',tt),
                (r'QCD',qcd),
                (r'V+Jets',vj)
            ]
        )
        bkgHists_log = OrderedDict(
            [
                (r'QCD',qcd),
                (r'$t\bar{t}$',tt),
                (r'V+Jets',vj)
            ]
        )
        sigHists = OrderedDict([(r'$T^{\prime}_{1800}\to t\phi_{125}$',sig)])

        xtitle = r'$m_{\phi}$ [GeV]' if proj == 'X' else r'$m_{T^{\prime}}$ [GeV]'

        print(f'Plotting {region} projection {proj}')
        for log in [True,False]:
            plot_stack(
                outname=f'plots/{region}_projection{proj}{"_logy" if log else ""}.pdf',
                data=data[0],
                bkgs=bkgHists_nom if not log else bkgHists_log,
                sigs=sigHists,
                totalBkg=tot[0],
                edges=binningX if proj=='X' else binningY,
                title=f'{region}_{proj}',
                xtitle=xtitle,
                ytitle=f'Events / GeV',
                lumiText=r'$138 fb^{-1}$ (13 TeV)',
                extraText='TEST',
                logyFlag = log
            )

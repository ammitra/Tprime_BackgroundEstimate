'''
Based off Matej's work
https://github.com/Boosted-X-H-bb-Y-anomalous-jet/AnomalousSearchPlotting/blob/master/plots_for_paper.py

Requires that the postfit shapes have been generated for the given signal and TF. 
'''
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import ROOT as r
plt.style.use(hep.style.CMS)
from PyHist import PyHist
import copy
import matplotlib

colours = {
    # CMS 10-colour-scheme from
    # https://cms-analysis.docs.cern.ch/guidelines/plotting/colors/#categorical-data-eg-1d-stackplots
    "darkblue": "#3f90da",
    "lightblue": "#92dadd",
    "orange": "#e76300",
    "red": "#bd1f01",
    "darkpurple": "#832db6",
    "brown": "#a96b59",
    "gray": "#717581",
    "beige": "#b9ac70",
    "yellow": "#ffa90e",
    "lightgray": "#94a4a2",
    # extra colours
    "darkred": "#A21315",
    "green": "#7CB518",
    "mantis": "#81C14B",
    "forestgreen": "#2E933C",
    "darkgreen": "#064635",
    "purple": "#9381FF",
    "deeppurple": "#36213E",
    "ashgrey": "#ACBFA4",
    "canary": "#FFE51F",
    "arylideyellow": "#E3C567",
    "earthyellow": "#D9AE61",
    "satinsheengold": "#C8963E",
    "flax": "#EDD382",
    "vanilla": "#F2F3AE",
    "dutchwhite": "#F5E5B8",
}
BG_COLOURS = {
    "QCD": "darkblue",
    "TT": "brown",
    "W+Jets": "orange",
    "Z+Jets": "yellow"
}

errorbar_style = {
    'linestyle': 'none',
    'marker': '.',      # display a dot for the datapoint
    'elinewidth': 2,    # width of the errorbar line
    'markersize': 15,   # size of the error marker
    #'capsize': 4,       # size of the caps on the errorbar (0: no cap fr)
    'color': 'k',       # black 
}

# Data point styling parameters
DATA_STYLE = {
    "histtype": "errorbar",
    "color": "black",
    "markersize": 15,
    "elinewidth": 2,
    "capsize": 0,
}

stack_style = {
    'edgecolor': (0, 0, 0, 0.5),
}

# hatch_style = {
#     'facecolor': 'none',
#     'edgecolor': 'black',#'#9c9ca1',
#     'alpha': 1,
#     'linewidth': 0,
#     'hatch': '//'
# }

hatch_style = {
    'color':'black',
    'alpha':0.2
}


def get_binning_x(hLow,hSig,hHigh):
    bins = []
    for i in range(1,hLow.GetNbinsX()+1):
        bins.append(hLow.GetXaxis().GetBinLowEdge(i))
    for i in range(1,hSig.GetNbinsX()+1):
        bins.append(hSig.GetXaxis().GetBinLowEdge(i))
    for i in range(1,hHigh.GetNbinsX()+2):#low edge of overflow is high edge of last bin
        bins.append(hHigh.GetXaxis().GetBinLowEdge(i))
    bins = np.array(bins,dtype='float64')
    return bins

def get_binning_y(hLow,hSig,hHigh):
    #histos should have same binning in Y
    bins = []
    for i in range(1,hLow.GetNbinsY()+2):
        bins.append(hLow.GetYaxis().GetBinLowEdge(i))
    bins = np.array(bins,dtype='float64')
    return bins

def get2DPostfitPlot(file, process, region, prefit=False):
    if not r.TFile.Open(file):
        raise FileNotFoundError(f"The file '{file}' does not exist or cannot be opened.")
    
    f = r.TFile.Open(file)
    fitStatus = "prefit" if prefit else "postfit"
    
    hLow = f.Get(f"{region}_LOW_{fitStatus}/{process}")
    if not hLow:
        raise ValueError(f"Histogram '{region}_LOW_{fitStatus}/{process}' does not exist in the file '{file}'.")
    
    hSig = f.Get(f"{region}_SIG_{fitStatus}/{process}")
    if not hSig:
        raise ValueError(f"Histogram '{region}_SIG_{fitStatus}/{process}' does not exist in the file '{file}'.")
    
    hHigh = f.Get(f"{region}_HIGH_{fitStatus}/{process}")
    if not hHigh:
        raise ValueError(f"Histogram '{region}_HIGH_{fitStatus}/{process}' does not exist in the file '{file}'.")
    
    h2 = merge_low_sig_high(hLow, hSig, hHigh, hName=f"h2_{process}_{region}")
    h2.SetDirectory(0)
    return h2


def merge_low_sig_high(hLow,hSig,hHigh,hName="temp"):
    n_x_low     = hLow.GetNbinsX()
    n_x_sig     = hSig.GetNbinsX()
    n_x_high    = hHigh.GetNbinsX()
    n_x         = n_x_low + n_x_sig + n_x_high
    n_y         = hLow.GetNbinsY()#assumes Y bins are the same
    bins_x      = get_binning_x(hLow,hSig,hHigh)
    bins_y      = get_binning_y(hLow,hSig,hHigh)
    h_res       = r.TH2F(hName,"",n_x,bins_x,n_y,bins_y)
    for i in range(1,n_x_low+1):
        for j in range(1,n_y+1):
            h_res.SetBinContent(i+0,j,hLow.GetBinContent(i,j))
            h_res.SetBinError(i+0,j,hLow.GetBinError(i,j))

    for i in range(1,n_x_sig+1):
        for j in range(1,n_y+1):
            h_res.SetBinContent(i+n_x_low,j,hSig.GetBinContent(i,j))
            h_res.SetBinError(i+n_x_low,j,hSig.GetBinError(i,j))

    for i in range(1,n_x_high+1):
        for j in range(1,n_y+1):
            h_res.SetBinContent(i+n_x_sig+n_x_low,j,hHigh.GetBinContent(i,j))
            h_res.SetBinError(i+n_x_sig+n_x_low,j,hHigh.GetBinError(i,j))
    return h_res

def get_hists(input_file,region,processes,prefit=False):
    histos_region_dict = {}
    for process in processes:
        h2 = get2DPostfitPlot(input_file,process,region,prefit)
        histos_region_dict[process]=h2
    return histos_region_dict

def ARC_plot(hData,hMC,hTotalBkg,labelsMC,colorsMC,xlabel,outputFile,xRange=[],yRange=[],projectionText="",yRangeLog=[],mx='',my='',combined_sigma=False, prelim=False, log=False):
    # Set up variables
    edges = hData.bin_edges
    print(edges)
    centersData = hData.get_bin_centers()

    # K:V {label:color}
    label_colors = dict(zip(labelsMC,colorsMC))

    # Concatenate processes per year (and W+Z -> V)
    tt  = np.zeros_like(hData.bin_values)
    wj  = np.zeros_like(hData.bin_values)
    zj  = np.zeros_like(hData.bin_values)
    xy  = np.zeros_like(hData.bin_values)
    qcd = np.zeros_like(hData.bin_values)

    # Get the pre-divide quantities 
    pre_divide_data = hData.bin_values
    pre_divide_bkg  = hTotalBkg.bin_values
    pre_divide_berr = hTotalBkg.bin_error

    print(pre_divide_data)
    print(pre_divide_bkg)
    print(pre_divide_berr)
    print('*************')

    # Now divide by bin width
    hData.divide_by_bin_width()
    hTotalBkg.divide_by_bin_width()

    print(pre_divide_data)
    print(pre_divide_bkg)
    print(pre_divide_berr)

    for h in hMC:
        # Divide by bin width 
        h.divide_by_bin_width()
        # Get the name
        hname = h.histo_name
        if 'ttbar_' in hname:
            tt += h.bin_values
        elif 'WJets' in hname:
            wj += h.bin_values
        elif 'ZJets' in hname:
            zj += h.bin_values
        elif 'Tprime' in hname:
            xy += h.bin_values
            print(h.bin_values)
        elif 'Background' in hname:
            qcd += h.bin_values
        else:
            continue

    # Fontsize
    fs = 36

    # Set up plotting 
    plt.style.use([hep.style.CMS])
    fig, (ax, rax) = plt.subplots(
        2, 1, figsize=(12, 14), gridspec_kw={"height_ratios": [3, 1], "hspace": 0.1}, sharex=True
    )

    if log:
        ax.set_yscale('log')

    # Concatenate V+jets bkg into "other"
    other = wj + zj
    # Organize backgrounds in opposite order of yields (lowest first)
    '''
    bkg_yields = np.array([wj, zj, tt, qcd])
    bkg_colors = ["#e76300","#ffa90e","#a96b59","#3f90da"]
    bkg_labels = ['W+jets','Z+jets',r'$t\bar{t}$','QCD']
    '''
    bkg_yields = np.array([other, qcd, tt])
    bkg_colors = ["#ffa90e","#3f90da","#a96b59"]
    bkg_labels = ['V+jets','QCD',r'$t\bar{t}$']
    # Organize signal
    sig_yields = xy
    sig_colors = "#bd1f01"
    sig_scale  = 2 #1.7621e-01 # postfit signal strength for S+B
    # sig_labels = r'$T^{\prime}_{%s}\to t\phi_{%s}$ $\times$ %s'%(mx,my,round(sig_scale,2))
    sig_labels = r'$T^{\prime}_{%s}\to t\phi_{%s}$'%(mx,my)
    # Organize data
    yerr = hData.get_error_pairs()
    xerrorsData = [width / 2 for width in hData.bin_widths]
    # Organize uncertainty
    tot_err = hTotalBkg.get_error_pairs()
    y1 = bkg_yields.sum(axis=0) - tot_err[0]
    y2 = bkg_yields.sum(axis=0) + tot_err[1]

    # Plot backgrounds
    hep.histplot(bkg_yields, edges, ax=ax, stack=True, label=bkg_labels, histtype="fill",facecolor=bkg_colors)
    if 'fail' not in outputFile:
        # Plot signal 
        ax.step(x=edges, y=np.hstack([sig_yields,sig_yields[-1]])*sig_scale, where='post', label=sig_labels, color=sig_colors, linewidth=3)
    # Plot data 
    ax.errorbar(x=centersData, y=hData.bin_values, xerr=xerrorsData, yerr=yerr, label='Data', capsize=0, **errorbar_style)
    # Plot systematic uncertainty
    ax.fill_between(x=edges, y1=np.hstack([y1,y1[-1]]), y2=np.hstack([y2,y2[-1]]), step='post', label=r'Total Bkg. Unc.', **hatch_style, linewidth=0.0)

    # Calculate pulls: sigma=sqrt{Nbkg_postfit - bkgUnc^2}
    # Use the pre-divide quantities:
    #   pre_divide_data 
    #   pre_divide_bkg
    #   pre_divide_berr
    sigma = np.sqrt(pre_divide_bkg - pre_divide_berr**2)
    slabel   = r"(Data - Bkg.) / $\sigma$"
    rax_ylim = 3.5

    print('----------------------------------------------------------------------------')
    print(pre_divide_bkg)
    print(pre_divide_berr)
    print(pre_divide_berr**2)
    print(sigma)
    print('----------------------------------------------------------------------------')
    exit()

    pulls = (pre_divide_data - pre_divide_bkg) / (sigma + 1e-7)

    # Plot pulls in rax
    # hep.histplot(pulls, edges, yerr=np.ones_like(pulls), xerr=True, ax=rax, **DATA_STYLE, label=r"(Data - Bkg.) / " + slabel)
    rax.step(x=edges, y=np.hstack([pulls,pulls[-1]]), where='post', label=slabel, color='black', linewidth=4)


    # if 'fail' not in outputFile:
    #     # Plot signal in rax
    #     sig_rax = copy.deepcopy(sig_yields) * sig_scale
    #     sig_rax = sig_rax / (sigma + 1e-7)
    #     hep.histplot(sig_rax, edges, ax=rax, label=r'$T^{\prime}_{%s} \to t\phi_{%s}$ / $\sigma$'%(mx,my), histtype="step", color=sig_colors, linewidth=4)


    # To match Raghav we want the legend to be in order: Data, signal, [QCD,TT,ZJ,WJ], syst unc
    handles, labels = ax.get_legend_handles_labels()
    # print(handles)
    # print(labels)
    # exit()
    #order = [6,4,3,2,1,0,5]
    if 'fail' not in outputFile:
        order = [5,3,2,1,0,4] # Data, signal, [QCD, TT, Other], bkg unc
    else:
        order = [4,2,1,0,3] # Data, [QCD, TT, Other], bkg unc
    leg = ax.legend([handles[idx] for idx in order],[labels[idx] for idx in order], loc='best',ncol=1, fontsize=fs-4)

    # Create two separate legends for rax
    handles, labels = rax.get_legend_handles_labels()
    signal_handles = []
    signal_labels = []
    other_handles = []
    other_labels = []

    for handle, label in zip(handles, labels):
        if 'prime' in label:
            signal_handles.append(handle)
            signal_labels.append(label)
        else:
            other_handles.append(handle)
            other_labels.append(label)

    if other_handles:
        first_legend = rax.legend(
            signal_handles, 
            signal_labels, 
            ncol=1, 
            loc="upper right",
            fontsize=fs-9,
            bbox_to_anchor=(1.0, 1.05)
        )
        rax.add_artist(first_legend)  # Add the first legend to the plot

    # Format Axes
    yMaximum = max(hData.bin_values)*1.5
    if log:
        ax.set_ylim([1e-3, yMaximum*100])
    else:
        ax.set_ylim([0., yMaximum])
    ax.margins(x=0)
    rax.set_ylim([-rax_ylim, rax_ylim])
    rax.margins(x=0)
    #rax.legend(loc='best',ncols=2)
    rax.hlines(0, *rax.get_xlim(), color=colours["gray"], linewidth=2, linestyle='dashed')

    if 'prime' in xlabel:
        xticks = [1000, 1500, 2000, 2500, 3000]
        ax.set_xticks(xticks)
        ax.set_xticklabels([f"{x:.0f}" for x in xticks], rotation=0, fontsize=fs)

    ax.set_xlim([edges[0],edges[-1]])
    rax.set_xlim([edges[0],edges[-1]])

    ax.tick_params(axis="both", which="major", labelsize=fs-4)
    rax.tick_params(axis="both", which="major", labelsize=fs-4)

    lumiText = r"138 $fb^{-1}$ (13 TeV)"    
    hep.cms.lumitext(lumiText,ax=ax, fontsize=fs)
    hep.cms.label(loc=0, ax=ax, label='Preliminary' if prelim else '', rlabel='', data=True, fontsize=fs)
    rax.set_xlabel(xlabel, fontsize=fs)
    rax.set_ylabel(r'(Data - Bkg.) / $\sigma$', fontsize=fs-5)
    ax.set_ylabel('< Events / GeV >', fontsize=fs)

    # Region naming
    if 'SR' in outputFile:
        if 'fail' in outputFile:
            region_text1 = 'SR Fail'
        else:
            region_text1 = 'SR Pass'
    else:
        if 'fail' in outputFile:
            region_text1 = 'BLAH'
        else:
            region_text1 = 'BLAH'

    p = leg.get_window_extent()
    # ax.text(0.3, 0.94, region_text1, fontsize=30, va='top', ha='left', transform=ax.transAxes, fontproperties='Tex Gyre Heros:bold')
    xpos = 0.055
    ypos = 0.88
    ax.text(
        xpos,
        ypos,
        region_text1,
        transform=ax.transAxes,
        fontsize=fs,
        fontproperties='Tex Gyre Heros:bold'
    )
    
    # Reduce whitespace around figure and save
    #plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.1)
    plt.savefig(outputFile, bbox_inches='tight')


def plot_projection(histos_dict, region, processes, labels_dict, colors_dict, axis="X",yRange=[],yRangeLog=[1,10**5], prefit=False, mx='', my='',combined_sigma=False, prelim=False, log=False):
    if axis not in ["X", "Y"]:
        raise ValueError("Invalid axis. Choose 'X' or 'Y'.")

    # Set up variables
    axis_label = r"$m_{\phi}^{rec}$ [GeV]" if axis == "X" else r"$m_{T^\prime}^{rec}$ [GeV]"
    file_suffix = "mX" if axis == "X" else "mY"
    file_suffix += "_Prefit" if prefit else "_Postfit"
    file_suffix += "_CombinedSigma" if combined_sigma else "_SeparateSigma"
    file_suffix += f'_{mx}-{my}'
    file_suffix += '_Preliminary' if prelim else '_Final'
    file_suffix += '_log' if log else '_linear'
    x_range = [800,4500] if axis == "X" else [300,4500]
    projection_method = f"Projection{axis}"

    # Extract histograms
    histos = histos_dict[region]

    h_data = getattr(histos["data_obs"], projection_method)(f"data_{axis}")
    h_data.SetBinErrorOption(1)
    h_data = PyHist(h_data)
    #h_data.divide_by_bin_width()

    h_mc = []
    labels_mc = []
    colors_mc = []
    for process in processes:
        print(process)
        h_temp = getattr(histos[process], projection_method)(f"{process}_{axis}")
        h_temp = PyHist(h_temp)
        h_name = h_temp.histo_name
        #h_temp.divide_by_bin_width()
        h_mc.append(h_temp)
        labels_mc.append(labels_dict[process])
        colors_mc.append(colors_dict[process])

    h_bkg = getattr(histos["TotalBkg"], projection_method)(f"bkg_{axis}")
    h_bkg = PyHist(h_bkg)
    #h_bkg.divide_by_bin_width()


    for ext in ['pdf','png']:
        ARC_plot(h_data, h_mc, h_bkg, labels_mc, colors_mc,axis_label,f"./plots/{region}_{file_suffix}.{ext}",xRange=x_range,yRange=yRange,projectionText=region.replace("_", " "),yRangeLog=yRangeLog, mx=mx, my=my, combined_sigma=combined_sigma, prelim=prelim, log=log)

if __name__ == "__main__":

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--prefit', dest='prefit',
                        action='store_true',
                        help='Plot prefit distributions instead of postfit')
    parser.add_argument('--sig', dest='sig', type=str,
                        default='1100-175', # signal which seems to have highest significance
                        action='store', help='mx-my signal mass to plot')
    args = parser.parse_args()

    prefit = args.prefit
    mx = args.sig.split('-')[0]
    my = args.sig.split('-')[1]

    input_file = f"{args.sig}_unblind_fits/postfitshapes_b.root"

    #proc_base = ['WJets','ZJets',f'TprimeB-{args.sig}','ttbar']
    proc_base = ['WJets','ZJets','ttbar']
    procs = []
    for p in proc_base:
        for y in ['16APV','16','17','18']:
            procs.append(f'{p}_{y}')

    procs_SR_pass = procs + ['Background_SR_pass_0x0','data_obs','TotalBkg']
    procs_SR_fail = procs + ['Background_SR_fail','data_obs','TotalBkg']

    histos_dict = {}
    histos_dict['SR_fail'] = get_hists(input_file,'SR_fail',procs_SR_fail,prefit)
    histos_dict['SR_pass'] = get_hists(input_file,'SR_pass',procs_SR_pass,prefit)

    # Now get s+b postfit signal shape 
    proc_sig = [f'TprimeB-{args.sig}_{y}' for y in ['16','16APV','17','18']]
    sig_hists_SR_pass = get_hists(input_file.replace('_b','_s'), 'SR_pass', proc_sig, prefit)
    histos_dict['SR_pass'].update(sig_hists_SR_pass)

    procs_SR_pass = procs_SR_pass + proc_sig


    labels_dict = {}
    colors_dict = {}
    for key in procs_SR_pass + procs_SR_fail:
        if key in labels_dict: continue 
        if key in colors_dict: continue
        else:
            if 'WJets' in key:
                label = '__nolabel__'
                color = '#1f77b4'
            elif 'ZJets' in key:
                label = 'V+Jets'
                color = '#1f77b4'
            elif 'ttbar' in key:
                label = r'$t\bar{t}$'
                color = '#d42e12'
            elif 'Background' in key:
                label = 'Multijet'
                color = '#f39c12'
            elif 'Tprime' in key:
                print('tprime spotted')
                label = r'$T^{\prime}_{%s} \to t\phi_{%s}$'%(mx,my)
                color = 'black'
            colors_dict[key] = color
            labels_dict[key] = label

    for k, v in {
        'SR_pass':procs_SR_pass,
        'SR_fail':procs_SR_fail
    }.items():
        for axis in ['X','Y']:
            for combined_sigma in [True]:
                for prelim in [True, False]:
                    for log in [True, False]:
                        plot_projection(histos_dict,k,v,labels_dict,colors_dict,axis=axis, prefit=prefit, mx=mx, my=my, combined_sigma=combined_sigma, prelim=prelim, log=log)

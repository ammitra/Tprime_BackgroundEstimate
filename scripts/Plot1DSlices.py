'''
Script to plot the postfit data and prediction in 1D slices
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


fs = 36

def PlotSlices(combined_sigma=False):
    input_file = '900-200_unblind_fits/postfitshapes_b.root'

    proc_base = ['WJets','ZJets','ttbar']
    procs = []
    for p in proc_base:
        for y in ['16APV','16','17','18']:
            procs.append(f'{p}_{y}')

    # procs_SR_fail = procs + ['Background_SR_fail','data_obs','TotalBkg']
    procs_SR_pass = procs + ['Background_SR_pass_0x0','data_obs','TotalBkg']

    # histos_dict = {}
    # histos_dict['SR_fail'] = get_hists(input_file,'SR_fail',procs_SR_fail,False)
    SRP_histos = get_hists(input_file,'SR_pass',procs_SR_pass,False)

    for i in range(1,SRP_histos['TotalBkg'].GetNbinsY()+1):
        dummyPH = PyHist(SRP_histos['TotalBkg'].ProjectionX(f'dummy_{i}',i,i))
        edges   = dummyPH.bin_edges
        centers = dummyPH.get_bin_centers()
        # Concatenate processes per year (and W+Z -> V)
        tt  = np.zeros_like(dummyPH.bin_values)
        vj  = np.zeros_like(dummyPH.bin_values)
        qcd = np.zeros_like(dummyPH.bin_values)
        data = None
        dataNoDiv = None
        bkg  = None
        bkgNoDiv = None
        # Get the sigs
        sig1 = np.zeros_like(dummyPH.bin_values)
        sig2 = np.zeros_like(dummyPH.bin_values) 
        sig3 = np.zeros_like(dummyPH.bin_values) 
        sig4 = np.zeros_like(dummyPH.bin_values) 
        sig5 = np.zeros_like(dummyPH.bin_values) 
        sig6 = np.zeros_like(dummyPH.bin_values) 
        sig7 = np.zeros_like(dummyPH.bin_values) 
        # Text for the slices 
        projLowEdge  = int(SRP_histos['TotalBkg'].GetYaxis().GetBinLowEdge(i))
        projUpEdge   = int(SRP_histos['TotalBkg'].GetYaxis().GetBinUpEdge(i))
        print(projLowEdge, projUpEdge)

        # Fill the arrays with the bkg+data shapes for this slice
        for j, shape in enumerate(SRP_histos.items()):
            proj = SRP_histos[shape[0]].ProjectionX(f'{shape[0]}_projx_{i}',i,i)
            projPH = PyHist(proj)
            projPH.divide_by_bin_width()
            noDiv = PyHist(proj)
            if 'ttbar_' in projPH.histo_name:
                tt += projPH.bin_values
            elif 'Jets' in projPH.histo_name:
                vj += projPH.bin_values
            elif 'Background' in projPH.histo_name:
                qcd += projPH.bin_values
            elif 'data' in projPH.histo_name:
                dataNoDiv = noDiv
                data = projPH
            elif 'TotalBkg' in projPH.histo_name:
                bkgNoDiv = noDiv
                bkg = projPH
            elif '200' in projPH.histo_name:
                sig1 += projPH.bin_values
            elif '225' in projPH.histo_name:
                sig2 += projPH.bin_values
            elif '250' in projPH.histo_name:
                sig3 += projPH.bin_values
            elif '275' in projPH.histo_name:
                sig4 += projPH.bin_values
            elif '300' in projPH.histo_name:
                sig5 += projPH.bin_values
            elif '325' in projPH.histo_name:
                sig6 += projPH.bin_values
            elif '350' in projPH.histo_name:
                sig7 += projPH.bin_values
            else:
                continue

        # Set up plotting 
        plt.style.use([hep.style.CMS])
        fig, (ax, rax) = plt.subplots(
            2, 1, figsize=(12, 14), gridspec_kw={"height_ratios": [3, 1], "hspace": 0.1}, sharex=True
        )
        bkg_yields = np.array([vj, tt, qcd])
        bkg_colors = ["#ffa90e","#a96b59","#3f90da"]
        bkg_labels = ['Other',r'$t\bar{t}$','QCD']

        # Organize data
        yerr = data.get_error_pairs()
        xerrorsData = [width / 2 for width in data.bin_widths]

        # Organize uncertainty
        tot_err = bkg.get_error_pairs()
        y1 = bkg_yields.sum(axis=0) - tot_err[0]
        y2 = bkg_yields.sum(axis=0) + tot_err[1]

        # Plot backgrounds
        hep.histplot(bkg_yields, edges, ax=ax, stack=True, label=bkg_labels, histtype="fill",facecolor=bkg_colors)

        # Plot data 
        ax.errorbar(x=centers, y=data.bin_values, xerr=xerrorsData, yerr=yerr, label='Data', capsize=0, **errorbar_style)
        # Plot systematic uncertainty
        ax.fill_between(x=edges, y1=np.hstack([y1,y1[-1]]), y2=np.hstack([y2,y2[-1]]), step='post', label=r'Total Bkg. Uncertainty', **hatch_style, linewidth=0.0)

        # Plot signals 
        sig_yields = np.array([sig1,sig2,sig3,sig4,sig5,sig6,sig7])

        # Calculate pulls
        if combined_sigma:
            # sigma    = np.sqrt(data.bin_error**2 + bkg.bin_error**2)
            # #sigma    = np.sqrt(hTotalBkg.bin_values + hTotalBkg.bin_error**2)
            # slabel   = r"$\sigma$"
            # rax_ylim = 3.5 
            sigma = np.sqrt(abs(bkgNoDiv.bin_values - bkgNoDiv.bin_error**2))
            rax_ylim = 3.5

        pulls = (dataNoDiv.bin_values - bkgNoDiv.bin_values) / (sigma + 1e-1)
        # fixed = []
        # for p in pulls:
        #     if not np.isnan(p):
        #         fixed.append(p)
        #     else:
        #         print('nan found')
        #         fixed.append(0)
        # pulls = np.array(fixed)



        print(pulls)

        '''
        # Pull plot
        sigma = np.sqrt(data.bin_error**2 + bkg.bin_error**2)
        pulls = (data.bin_values - bkg.bin_values) / sigma
        hep.histplot(pulls, edges, yerr=np.ones_like(pulls), xerr=True, ax=rax, **DATA_STYLE, label=r"(Data - Bkg.) / $\sigma$")
        '''

        # Plot pulls in rax
        # hep.histplot(pulls, edges, yerr=np.ones_like(pulls), xerr=True, ax=rax, **DATA_STYLE, label=r"(Data - Bkg.) / " + slabel)
        rax.step(x=edges, y=np.hstack([pulls,pulls[-1]]), where='post', color='black', linewidth=4)

        if not combined_sigma:
            eUp = np.zeros_like(pulls) + bkg.bin_error / (sigma + 1e-3)
            eDn = np.zeros_like(pulls) - bkg.bin_error / (sigma + 1e-3)
            rax.fill_between(
                x=edges, 
                y1=np.hstack([eUp, eUp[-1]]), 
                y2=np.hstack([eDn, eDn[-1]]), 
                step='post', 
                label=r"$\sigma_\mathrm{Syst}$ / $\sigma_\mathrm{Stat}$",
                **hatch_style,
                linewidth=0
            )


        handles, labels = ax.get_legend_handles_labels()
        order = [4, 2, 1, 0, 3] # Data, [QCD, TT, Other], bkg unc
        leg = ax.legend([handles[idx] for idx in order],[labels[idx] for idx in order], loc='best',ncol=1, fontsize=fs-4)

        # Format Axes
        if max(data.bin_values) < 1.0:
            yMaximum = max(bkg.bin_values)*1.5
        else:
            yMaximum = max(data.bin_values)*1.5
        ax.set_ylim([0., yMaximum])
        ax.margins(x=0)
        rax.set_ylim([-rax_ylim, rax_ylim])
        rax.margins(x=0)
        rax.legend(loc='best',ncols=2)
        rax.hlines(0, *rax.get_xlim(), color=colours["gray"], linewidth=2, linestyle='dashed')

        ax.set_xlim([edges[0],edges[-1]])
        rax.set_xlim([edges[0],edges[-1]])

        lumiText = r"138 $fb^{-1}$ (13 TeV)"    
        hep.cms.lumitext(lumiText,ax=ax, fontsize=fs)
        hep.cms.label(loc=0, ax=ax, label='Supplementary', rlabel='', data=True, fontsize=fs)
        rax.set_xlabel(r'$m_{\phi}^{rec}$ [GeV]', fontsize=fs)
        rax.set_ylabel(r'(Data-Pred.) / $\sigma$', fontsize=fs)
        ax.set_ylabel('< Events / GeV >', fontsize=fs)

        xticks = [100, 200, 300, 400, 500]
        ax.set_xticks(xticks)
        ax.set_xticklabels([f"{x:.0f}" for x in xticks], rotation=0, fontsize=fs)

        ax.tick_params(axis="both", which="major", labelsize=fs-4)
        rax.tick_params(axis="both", which="major", labelsize=fs-4)

        projectionText = "{0}".format(projLowEdge)+"<$p_{T}$<"+"{0} GeV".format(projUpEdge)
        projectionText = r'$%s < m_{T^\prime}^{rec} < %s$ GeV'%(projLowEdge,projUpEdge)
        ax.text(0.7, 0.5, projectionText, fontsize=fs-5, va='top', ha='center', transform=ax.transAxes)

        # Reduce whitespace around figure and save
        plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.1)
        if combined_sigma:
            suffix = '_CombinedSigma'
        else:
            suffix = '_SeparateSigma'
        plt.savefig(f'plots/slice_projX_MY-{projLowEdge}-{projUpEdge}_{suffix}.pdf', bbox_inches='tight')
        plt.savefig(f'plots/slice_projX_MY-{projLowEdge}-{projUpEdge}_{suffix}.png', bbox_inches='tight')


if __name__ == "__main__":
    for combined_sigma in [True]:
        PlotSlices(combined_sigma)
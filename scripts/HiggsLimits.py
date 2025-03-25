'''
Script to generate 1D limits as a function of mT for fixed mPhi=125 GeV
'''
import os, glob
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import mplhep as hep
import matplotlib.ticker as mticker
import ROOT
import subprocess
import pandas as pd
from collections import OrderedDict
import argparse

'''
IMPORTANT - the limits have been calculated in two ways (using the postfit workspace):
    1) with the full SR+CR model
    2) with the CR masked and all CR-specific nuisances frozen and zeroed
The second method speeds up limit calculation by a factor of almost 200 and provides almost identical results. Therefore, the default will be to use these results. If desired, this can be changed by passing `--withCR` to the script.
'''
parser = argparse.ArgumentParser()
parser.add_argument("--withCR", dest='withCR', action='store_true', help='If passed as an argument, use the limits calculated with the ttbar CR. Otherwise, will use the limits calculated with the CR masked.')
parser.add_argument('--pb', dest='pb', action='store_true', help='Plot in units of pb instead of fb (default False)')
#parser.add_argument('--bsm', dest='bsm', action='store_true', help="Scale limits by BSM branching ratio T' -> tH = 0.25")
args = parser.parse_args()

for name in ['raw','scaled']:
    if name == 'raw':
        factor = 1.0
    else:
        # MC is exclusive, so to obtain inclusive results we must scale up MC by a factor of 1/BR(SM) ~= 2.5
        tbqq_BR = 0.991 * 0.6732 # Wqq taken from https://arxiv.org/pdf/2201.07861
        hbb_BR = 5.84E-1 # Hbb taken from table 11.3: https://pdg.lbl.gov/2016/reviews/rpp2016-rev-higgs-boson.pdf
        factor = 1./(tbqq_BR * hbb_BR)

    print(f'Plotting 1D limits for mPhi = mH, {name}')

    # 0: minus2, 1: minus2, 2: median, 3: plus1, 4: plus2, 5: observed
    dfs     = {0:None, 1:None, 2:None, 3:None, 4:None, 5:None}
    new_dfs = {0:None, 1:None, 2:None, 3:None, 4:None, 5:None}

    for i in range(len(dfs)):
        if i == 0:
            fname = f"limits/limits_Minus2_{'withCR' if args.withCR else 'noCR'}.csv"
        elif i == 1:
            fname = f"limits/limits_Minus1_{'withCR' if args.withCR else 'noCR'}.csv"
        elif i == 2:
            fname = f"limits/limits_Expected_{'withCR' if args.withCR else 'noCR'}.csv"
        elif i == 3:
            fname = f"limits/limits_Plus1_{'withCR' if args.withCR else 'noCR'}.csv"
        elif i == 4:
            fname = f"limits/limits_Plus2_{'withCR' if args.withCR else 'noCR'}.csv"
        else:
            fname = f"limits/limits_Observed_{'withCR' if args.withCR else 'noCR'}.csv"
        lim = pd.read_csv(fname)
        dfs[i] = lim

    # Loop over all 5 limits 
    for i in range(len(dfs)):
        df = dfs[i]   # Get the entire dataframe for this limit
        df = df[df['MPhi'] == 125.0]    # Get the limits only for mPhi=125
        df = df.sort_values(by='MTprime')   # Sort by ascending mT
        new_dfs[i] = df # overwrite it in the master dict 

    # Get the distinct x values
    xs = new_dfs[0]['MTprime'].values

    plt.style.use([hep.style.CMS])
    fig, ax = plt.subplots(figsize=(12,10), dpi=200)

    green = '#607641' 
    yellow = '#F5BB54'

    ax.set_xlim([800, 3000])    # the x-axis is plotting mT 
    ax.set_yscale('log')


    if not args.pb:
        ax.set_ylim([5e-2, 1e3])#1e4])    # the y-axis is plotting xsec * BR
    else:
        ax.set_ylim([1e-3,1.7])

    # locmin = mticker.LogLocator(base=10.0,subs=(0.2,0.4,0.6,0.8),numticks=12)
    # ax.xaxis.set_minor_locator(locmin)
    # ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    # ax.yaxis.set_minor_locator(locmin)
    # ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())

    # scale the values by factor (1 if raw, BRs if not)
    for i in range(6):
        new_dfs[i] = new_dfs[i] * factor

    # Now get the actual values
    if args.pb:
        for i in range(6):
            new_dfs[i] = new_dfs[i]/1000.

    m2  = new_dfs[0]['Limit (fb)'].values #/ 1. if not args.pb else 1000.
    m1  = new_dfs[1]['Limit (fb)'].values #/ 1. if not args.pb else 1000.
    med = new_dfs[2]['Limit (fb)'].values #/ 1. if not args.pb else 1000.
    p1  = new_dfs[3]['Limit (fb)'].values #/ 1. if not args.pb else 1000.
    p2  = new_dfs[4]['Limit (fb)'].values #/ 1. if not args.pb else 1000.
    obs = new_dfs[5]['Limit (fb)'].values #/ 1. if not args.pb else 1000.
    #x_vals = dfs[0]['MTprime'].values
    x_vals = [float(x) for x in xs]

    ax.fill_between(x_vals, m2, p2, color=yellow, label=r'$\pm 2\sigma$')
    ax.fill_between(x_vals, m1, p1, color=green, label=r'$\pm 1\sigma$')
    ax.plot(x_vals, med, color='black', linewidth=2.5, linestyle='--', label='Expected 95% CL limit')
    ax.plot(x_vals, obs, color='black', linewidth=2.5, linestyle='-', label='Observed')

    ax.text(0.7, 0.5, r'$m_{\phi} = m_{H} = 125$ GeV', ha='center', va='top', fontsize=25, transform=ax.transAxes,fontproperties='Tex Gyre Heros:bold')

    if name == 'raw':
        ax.set_ylabel(r"$\sigma$(pp $\to T^\prime \to tH$) [%sb]"%('f' if not args.pb else 'p'))
    else:
        ax.set_ylabel(r"$\sigma$(pp $\to T^\prime bq$) $\times$ B($T^\prime \to tH$) [%sb]"%('f' if not args.pb else 'p'))
        #ax.set_ylabel(r'$\sigma$(pp $\to T^\prime \to tH$) $\times$ B($t \to bq\bar{q}$) $\times$ B($H \to b\bar{b}$) [%sb]'%('f' if not args.pb else 'p'))

    # THEORY CURVES - https://docs.google.com/spreadsheets/d/19uSpGSsEgSHceBl1-pnneIWJ_abYn7GB/edit?gid=1774300745#gid=1774300745
    mT_1 = np.array([0.6,0.65,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.2,2.4,2.6])*1000
    XS_1 = np.array([203.40,137.17,88.107,45.920,25.327,14.550,8.640,5.342,3.390,2.197,1.448,0.9743,0.6638,0.4588,0.3201,0.2256,0.119,0.0671,0.0401])
    mT_5 = np.array([0.6,0.65,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,2.0,2.2,2.4,2.6])*1000
    XS_5 = np.array([956.42,651.19,416.3495,218.437,120.4725,69.8805,42.0605,26.1005,16.6795,10.8675,7.239,4.894,3.366,2.3395,1.172,0.631556,0.36267,0.221838])
    
    if args.pb:
        for arr in [XS_1, XS_5]:
            for i in range(len(arr)):
                arr[i] = arr[i]/1000.

    ax.plot(mT_1, XS_1, linewidth=2.5, label=r'$\sigma(NLO),$ Singlet $T^{\prime},$ $\Gamma/m_{T^{\prime}}=0.01$', color='#e42536') # red
    ax.plot(mT_5, XS_5, linewidth=2.5, label=r'$\sigma(NLO),$ Singlet $T^{\prime},$ $\Gamma/m_{T^{\prime}}=0.05$', color='#5790fc') # blue

    ax.set_xlabel(r"$m_{T^\prime}$ (GeV)",loc='right')

    #handles, labels = ax.get_legend_handles_labels()
    #ax.legend(handles, labels, loc='upper right', fontsize=8, frameon=True)
    ax.legend(loc='best',ncol=1)
    hep.cms.label(loc=2, ax=ax, label='Preliminary', rlabel='', data=True)
    lumiText = r"138 $fb^{-1}$ (13 TeV)"
    hep.cms.lumitext(lumiText,ax=ax)

    fig.tight_layout()
    plt.savefig(f"plots/Higgs_limits_1D_{'withCR' if args.withCR else 'noCR'}{'_pb' if args.pb else ''}_{name}.pdf")
    plt.savefig(f"plots/Higgs_limits_1D_{'withCR' if args.withCR else 'noCR'}{'_pb' if args.pb else ''}_{name}.png")

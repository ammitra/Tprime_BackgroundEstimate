'''
Script to generate a 4x4 grid of plots for 1D limits as a function of mTprime for different mPhi values.
Similar to those made by Xanda:
    - https://www.dropbox.com/scl/fi/t1h7qcb5e1hby75ixeme6/HY_bbWW4q_examples.pdf?rlkey=mp6b5qv7w64ajweqkthwimhaw&e=1&dl=0
    - https://gitlab.cern.ch/acarvalh/generalsummary/-/blob/B2G-23-002/specific_interpretations/HYPlot/DrawHYPlot.py?ref_type=heads
    - https://indico.cern.ch/event/1337889/contributions/5694589/attachments/2770171/4826694/PhysicsDays_HY_progress_Dec2023.pdf

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

args = parser.parse_args()

# Main plotting routine for each axes
def plot_limit_1D(ax, x_axis_vals, yMass, m2, m1, med, p1, p2, obs):
    '''
    pass numpy arrays for the +/-1, +/-2, and median expected limits and the axes on which to draw.
    '''
    green = '#607641' 
    yellow = '#F5BB54'

    ax.grid(True, axis='y', linestyle='dashed')

    ax.set_yscale('log')
    #ax.set_xscale('log')
    ax.set_xlim([800, 3000])    # the x-axis is plotting mT 
    ax.set_ylim([1e-2, 1e6])    # the y-axis is plotting xsec * BR limit 

    locmin = mticker.LogLocator(base=10.0,subs=(0.2,0.4,0.6,0.8),numticks=12)
    ax.xaxis.set_minor_locator(locmin)
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.yaxis.set_minor_locator(locmin)
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())

    ax.fill_between(x_axis_vals, m2, p2, color=yellow, label=r'$\pm 2\sigma$')
    ax.fill_between(x_axis_vals, m1, p1, color=green, label=r'$\pm 1\sigma$')
    ax.plot(x_axis_vals, med, color='black', linestyle='--', label='Expected 95% CL limit')
    ax.plot(x_axis_vals, obs, color='black', linestyle='-', label='Observed')

    ax.text(0.2, 0.95, r'$m_{\phi} = %s$ GeV'%(yMass), ha='center', va='top', fontsize='small', transform=ax.transAxes)

# X and Y masses for consideration
xs = ['800', '900', '1000', '1200', '1400', '1600', '1800', '2000', '2400', '2800', '2900', '3000']
ys = ['75', '100', '125', '175', '200', '250', '350', '450', '500']

for name in ['raw','scaled']:
    if name == 'raw':
        factor = 1.0
    else:
        factor = 0.991 * 0.6732 # T->bqq BR.  Wqq taken from https://arxiv.org/pdf/2201.07861

    print(f'Plotting 1D limits {name}')

    # 0: minus2, 1: minus2, 2: median, 3: plus1, 4: plus2, 5: observed
    dfs  = {0:None, 1:None, 2:None, 3:None, 4:None, 5:None}
    sigs = OrderedDict([(my,dfs.copy()) for my in ys])

    # Now populate the dfs dict with the full dataframes of all the limits 
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

    # Store the dataframes for the median, +/-1 sigma, +/-2 sigma, and observed limits.
    for my in ys:
        for lim in range(len(dfs)):
            df = dfs[lim]
            df = df[df['MPhi'] == float(my)]
            sigs[my][lim] = df.sort_values(by='MTprime')

    # At this point, all 9 mPhi values have their 5 limits stored in pandas dfs as a function of mTprime.
    hep.cms.text("WiP",loc=0)
    lumiText = "138 $fb^{-1} (13 TeV)$"    
    hep.cms.lumitext(lumiText)
    fig, axes = plt.subplots(3, 3, figsize=(10,10), dpi=150, sharex=True, sharey=True)
    axes = axes.flatten()

    for i, mY in enumerate(ys):
        ax = axes[i]
        lims = sigs[mY]

        # scale the values by factor (1 if raw, BRs if not)
        for i in range(6):
            lims[i]['Limit (fb)'] = lims[i]['Limit (fb)'] * factor

        y_vals = lims[0]['MTprime'].values # just grab the minus2 key as a dummy key to get they Y-vals. All keys should give the same
        m2  = lims[0]['Limit (fb)'].values
        m1  = lims[1]['Limit (fb)'].values
        med = lims[2]['Limit (fb)'].values
        p1  = lims[3]['Limit (fb)'].values
        p2  = lims[4]['Limit (fb)'].values
        o   = lims[5]['Limit (fb)'].values

        plot_limit_1D(
            ax = ax, 
            x_axis_vals = y_vals, 
            yMass = mY, 
            m2 = m2, 
            m1 = m1, 
            med = med,
            p1 = p1, 
            p2 = p2,
            obs = o
        )
        # until I figure out a better way to apply a common x/y-axis label to subplots...
        if i == 0:
            if name == 'raw':
                ax.set_ylabel(r"$\sigma$(pp $\to T^\prime \to t\phi$) [fb]")
            else:
                ax.set_ylabel(r'$\sigma$(pp $\to T^\prime \to t\phi$) $\times B(t\to bq\bar{q})\times B(\phi\to b\bar{b})$ [fb]')
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles, labels, loc='upper right', fontsize=8, frameon=True) # Draw legend with box so it doesn't get obscured by gridlines
            lumiText = "138 $fb^{-1}$ (13 TeV)" 
            hep.cms.text("WiP",loc=0,ax=ax)
            hep.cms.lumitext(lumiText,ax=ax)

        if i == len(ys)-1:
            ax.set_xlabel(r"$m_{T^\prime}$ (GeV)",loc='right')

    fig.tight_layout()
    plt.savefig(f"plots/column_limits_1D_{'withCR' if args.withCR else 'noCR'}_mT_{name}.pdf")
    plt.savefig(f"plots/column_limits_1D_{'withCR' if args.withCR else 'noCR'}_mT_{name}.png")

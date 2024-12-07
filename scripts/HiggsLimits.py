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
args = parser.parse_args()

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

# Plot 
hep.cms.text("WiP",loc=0)
lumiText = "138 $fb^{-1} (13 TeV)$"    
hep.cms.lumitext(lumiText)
fig, ax = plt.subplots(dpi=200)

green = '#607641' 
yellow = '#F5BB54'

ax.grid(True, axis='y', linestyle='dashed')

ax.set_xlim([800, 3000])    # the x-axis is plotting mT 
ax.set_yscale('log')

if not args.pb:
    ax.set_ylim([1e-1, 1e4])    # the y-axis is plotting xsec
else:
    ax.set_ylim([1e-3,1.0])

# locmin = mticker.LogLocator(base=10.0,subs=(0.2,0.4,0.6,0.8),numticks=12)
# ax.xaxis.set_minor_locator(locmin)
# ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
# ax.yaxis.set_minor_locator(locmin)
# ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())

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
ax.plot(x_vals, med, color='black', linestyle='--', label='Expected 95% CL limit')
ax.plot(x_vals, obs, color='black', linestyle='-', label='Observed')

ax.text(0.3, 0.95, r'$m_{\phi} = 125$ GeV', ha='center', va='top', fontsize='small', transform=ax.transAxes)

ax.set_ylabel(r"$\sigma$(pp $\to T^\prime \to t\phi$) (%sb)"%('f' if not args.pb else 'p'))
ax.set_xlabel(r"$m_{T^\prime}$ (GeV)",loc='right')
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels, loc='upper right', fontsize=8, frameon=True)
lumiText = "138 $fb^{-1}$ (13 TeV)" 
hep.cms.text("WiP",loc=0,ax=ax)
hep.cms.lumitext(lumiText,ax=ax)

fig.tight_layout()
plt.savefig(f"plots/Higgs_limits_1D_{'withCR' if args.withCR else 'noCR'}{'_pb' if args.pb else ''}.pdf")
plt.savefig(f"plots/Higgs_limits_1D_{'withCR' if args.withCR else 'noCR'}{'_pb' if args.pb else ''}.png")
import os, glob
import numpy as np
from scipy import interpolate
import matplotlib
import matplotlib.pyplot as plt
import mplhep as hep
import matplotlib.ticker as mticker
import ROOT
import subprocess
import pandas as pd
import argparse

'''
IMPORTANT - the limits have been calculated in two ways (using the postfit workspace):
    1) with the full SR+CR model
    2) with the CR masked and all CR-specific nuisances frozen and zeroed
The second method speeds up limit calculation by a factor of almost 200 and provides almost identical results. Therefore, the default will be to use these results. If desired, this can be changed by passing `--withCR` to the script.

The limits are scaled by 1/BR(t->bqq) b/c the signal MC is exclusive. Given that this MC is exclusive, the number from AsymptoticLimits is already the limit on the BR (t->bqq,H->bb). In other words: this is the limit on T->tH[ at 100% BR]->(qbb) (bb) [at100% BR], i.e. exclusive decay. In order to get the limit on the tH (inclusive) you need to scale up the exclusive decay limit by 1/BR, i.e. 2.5.  

'''
parser = argparse.ArgumentParser()
parser.add_argument("--withCR", dest='withCR', action='store_true', help='If passed as an argument, use the limits calculated with the ttbar CR. Otherwise, will use the limits calculated with the CR masked.')
args = parser.parse_args()

failed = open('failed_limits.txt','w')

plt.style.use(hep.style.CMS)
hep.style.use("CMS")
formatter = mticker.ScalarFormatter(useMathText=True)
formatter.set_powerlimits((-3, 3))
plt.rcParams.update({"font.size": 20})

def mxmy(sample):
    # Example input: 1000-100_unblind_fits/higgsCombine_1000-100_noCR_workspace.AsymptoticLimits.mH120.root
    mX = float(sample.split('/')[1].split('_')[1].split('-')[0])
    mY = float(sample.split('/')[1].split('_')[1].split('-')[1])
    return (mX, mY)

# 0-4 are m2,m1,exp,p1,p2 sigma limits, 5 is observed
limits = {0: [], 1: [], 2: [], 3: [], 4: [], 5: []}
limits_tbqq = {0: [], 1: [], 2: [], 3: [], 4: [], 5: []}

#files = glob.glob('results_unblinded_ANv14_Paperv3_noQCDscale/*_fits/higgsCombine*workspace*.AsymptoticLimits.*')
files = glob.glob('*_fits/higgsCombine*workspace*.AsymptoticLimits.*')

files = [f for f in files if 'workspace' in f]
if args.withCR:
    files = [f for f in files if 'noCR' not in f]
else:
    files = [f for f in files if 'noCR' in f]

# Let x=Tprime, y=Phi
for sample in files:
    tbqq_BR = 0.991 * 0.6732 # Wqq taken from https://arxiv.org/pdf/2201.07861
    mx, my = mxmy(sample)
    print('Processing sample ({},{})'.format(mx,my))
    # loop over m2 to p2 sigma 
    f = ROOT.TFile.Open(sample,'READ')
    limTree = f.Get('limit')
    if not limTree:
        failed.write(f'{mx}-{my}\t- No limit TTree\n')
        print(f'ERROR: signal {mx}-{my} has no limit TTree')
        continue
    for i in range(6):
        # Check if the limit exists 
        if not limTree.GetEntry(i):
            failed.write(f'{mx}-{my}\t- Missing limit entry {i}\n')
            print(f'ERROR: signal {mx}-{my} missing limit entry {i}')
            continue
        # The input normalization is all in picobarns (1pb = 1000fb)
        # So we multiply all limits by the input cross section in fb
        limTree.GetEntry(i)
        if mx < 1400: 
            signalNorm = 0.1 * (1000.)
        else: 
            signalNorm = 0.01 * (1000.)
        # raw limits
        limit = limTree.limit * signalNorm
        limits[i].append([mx, my, limit])
        # limits scaled by 1/BR(t->bqq)
        limit_scaled = limTree.limit * signalNorm / tbqq_BR
        limits_tbqq[i].append([mx, my, limit_scaled])

for key in limits.keys():
    limits[key] = np.array(limits[key])
    limits_tbqq[key] = np.array(limits_tbqq[key])

# Make separate files 
for key, limit in limits.items():
    print(type(key),key)
    df = pd.DataFrame(limit, columns=["MTprime", "MPhi", "Limit (fb)"])
    labels = {
        0: 'Minus2',
        1: 'Minus1',
        2: 'Expected',
        3: 'Plus1',
        4: 'Plus2',
        5: 'Observed'
    }
    df.to_csv(f"limits/limits_{labels[key]}_{'withCR' if args.withCR else 'noCR'}.csv")
# Make combined files
joint_limits = pd.DataFrame(limits[0],columns=["MTprime", "MPhi", "DROP"])
joint_limits = joint_limits.drop('DROP',axis=1)
joint_limits = joint_limits.sort_values(by=['MTprime','MPhi'],ascending=[True,True])
for key in [3,4,1,0,2,5]:
    df = pd.DataFrame(limits[key], columns=["MTprime", "MPhi", "Limit (fb)"])
    df = df.sort_values(by=['MTprime','MPhi'],ascending=[True,True])
    labels = {
        0: 'limit_m2',
        1: 'limit_m1',
        2: 'exp',
        3: 'limit_p1',
        4: 'limit_p2',
        5: 'obs'
    }
    vals = df['Limit (fb)'].values
    joint_limits[labels[key]] = vals
joint_limits.to_csv('limits/summary_limits_B2G-22-001_raw.csv')

# Make combined files scaled by SM decay BR(t->bqq)
tbqq_BR = 0.991 * 0.6732 # Wqq taken from https://arxiv.org/pdf/2201.07861
joint_lims_tbqq = pd.DataFrame(limits[0],columns=["MTprime", "MPhi", "DROP"])
joint_lims_tbqq = joint_lims_tbqq.drop('DROP',axis=1)
joint_lims_tbqq = joint_lims_tbqq.sort_values(by=['MTprime','MPhi'],ascending=[True,True])
for key in [3,4,1,0,2,5]:
    df = pd.DataFrame(limits[key], columns=["MTprime", "MPhi", "Limit (fb)"])
    df = df.sort_values(by=['MTprime','MPhi'],ascending=[True,True])
    labels = {
        0: 'limit_m2',
        1: 'limit_m1',
        2: 'exp',
        3: 'limit_p1',
        4: 'limit_p2',
        5: 'obs'
    }
    vals = df['Limit (fb)'].values * tbqq_BR
    joint_lims_tbqq[labels[key]] = vals
joint_lims_tbqq.to_csv('limits/summary_limits_B2G-22-001.csv')


def scatter2d(arr, title, name):
    fig, ax = plt.subplots(figsize=(14, 12))
    mappable = plt.scatter(
        arr[:, 0],
        arr[:, 1],
        s=150,
        c=arr[:, 2],
        cmap="viridis",
        norm=matplotlib.colors.LogNorm(vmin=0.01, vmax=100),
    )
    plt.xlabel(r"$m_{T^{\prime}}$ (GeV)")
    plt.ylabel(r"$m_{\phi}$ (GeV)")
    plt.colorbar(mappable,label=title)
    #hep.cms.label("Work in Progress", data=True, lumi="138", ax=ax)
    hep.cms.label(loc=0, ax=ax, label='Preliminary', rlabel='', data=True)
    lumiText = r"138 $fb^{-1}$ (13 TeV)"
    hep.cms.lumitext(lumiText,ax=ax)
    plt.savefig(name, bbox_inches="tight")

def colormesh(xx, yy, lims, label, name):
    fig, ax = plt.subplots(figsize=(12, 8))
    pcol = plt.pcolormesh(xx, yy, lims, norm=matplotlib.colors.LogNorm(vmin=0.05, vmax=1e4), cmap="viridis", linewidth=0, rasterized=True)
    pcol.set_edgecolor('face')
    # plt.title(title)
    plt.xlabel(r"$m_{T^{\prime}}$ (GeV)")
    plt.ylabel(r"$m_{\phi}$ (GeV)")
    plt.colorbar(label=label)
    #hep.cms.label("Work in Progress", data=True, lumi="138", ax=ax)
    hep.cms.label(loc=0, ax=ax, label='Preliminary', rlabel='', data=True)
    lumiText = r"138 $fb^{-1}$ (13 TeV)"
    hep.cms.lumitext(lumiText,ax=ax)
    plt.savefig(name, bbox_inches="tight")

mxs = np.logspace(np.log10(800), np.log10(2999), 100, base=10)
mys = np.logspace(np.log10(74), np.log10(500), 100, base=10)

xx, yy = np.meshgrid(mxs, mys)

# Make plots for both raw and scaled limits
for i, lim_dict in enumerate([limits, limits_tbqq]):
    if i == 0:
        name = 'raw'
    else:
        name = 'tbqq'

    print(f'Plotting {name} limits')
    interpolated = {}
    grids = {}

    for key, val in lim_dict.items():
        interpolated[key] = interpolate.LinearNDInterpolator(val[:, :2], np.log(val[:, 2]))
        grids[key] = np.exp(interpolated[key](xx, yy))


    for key, grid in grids.items():
        if key == 0: label = '2.5'
        elif key == 1: label = '16.0'
        elif key == 2: label = '50.0'
        elif key == 3: label = '84.0'
        elif key == 4: label = '97.5'
        elif key == 5: label = 'Observed'
        if label == 'Observed':
            t = r'95% CL observed upper limits on $\sigma\mathcal{B}$ (fb)'
        else:
            if label == '50.0':
                t = r'95% CL median expected upper limits on $\sigma\mathcal{B}$ (fb)'
            else:
                t = r'95% CL {}% expected upper limits on $\sigma\mathcal{}$ (fb)'.format(label,"{B}")
        colormesh(xx, yy, grid, t, "plots/limit2D_interp_{}_{}_{}.pdf".format(label.replace('.','p'),'withCR' if args.withCR else 'noCR',name))
        colormesh(xx, yy, grid, t, "plots/limit2D_interp_{}_{}_{}.png".format(label.replace('.','p'),'withCR' if args.withCR else 'noCR',name))

    for key in range(6):
        if key == 0: label = '2.5'
        elif key == 1: label = '16.0'
        elif key == 2: label = '50.0'
        elif key == 3: label = '84.0'
        elif key == 4: label = '97.5'
        elif key == 5: label = 'Observed'
        val = limits[key]
        if label == 'Observed':
            t = r'95% CL observed upper limits on $\sigma\mathcal{B}$(fb)'
        else:
            if label == '50.0':
                t = r'95% CL median expected upper limits on $\sigma\mathcal{B}$(fb)'
            else:
                t = r'95% CL {}% expected upper limits on $\sigma\mathcal{}$(fb)'.format(label,"{B}")
        scatter2d(val, t, "plots/limit2D_scatter_{}_{}_{}.pdf".format(label.replace('.','p'),'withCR' if args.withCR else 'noCR',name))
        scatter2d(val, t, "plots/limit2D_scatter_{}_{}_{}.png".format(label.replace('.','p'),'withCR' if args.withCR else 'noCR',name))

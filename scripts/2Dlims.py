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
    mX = float(sample.split('/')[0].split('_')[0].split('-')[0])
    mY = float(sample.split('/')[0].split('_')[0].split('-')[1])
    return (mX, mY)

# 0-4 are m2,m1,exp,p1,p2 sigma limits, 5 is observed
limits = {0: [], 1: [], 2: [], 3: [], 4: [], 5: []}

files = glob.glob('*_fits/higgsCombine*workspace*.AsymptoticLimits.*')

files = [f for f in files if 'workspace' in f]
if args.withCR:
    files = [f for f in files if 'noCR' not in f]
else:
    files = [f for f in files if 'noCR' in f]

# Let x=Tprime, y=Phi
for sample in files:
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
        limit = limTree.limit * signalNorm
        limits[i].append([mx, my, limit])

for key in limits:
    limits[key] = np.array(limits[key])

for key, limit in limits.items():
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

def scatter2d(arr, title, name):
    fig, ax = plt.subplots(figsize=(14, 12))
    mappable = plt.scatter(
        arr[:, 0],
        arr[:, 1],
        s=150,
        c=arr[:, 2],
        cmap="turbo",
        norm=matplotlib.colors.LogNorm(vmin=0.01, vmax=100),
    )
    plt.xlabel(r"$m_{T^{\prime}}$ (GeV)")
    plt.ylabel(r"$m_{\phi}$ (GeV)")
    plt.colorbar(mappable,label=title)
    hep.cms.label("Work in Progress", data=True, lumi="138", ax=ax)
    plt.savefig(name, bbox_inches="tight")

def colormesh(xx, yy, lims, label, name):
    fig, ax = plt.subplots(figsize=(12, 8))
    _ = plt.pcolormesh(
        xx, yy, lims, norm=matplotlib.colors.LogNorm(vmin=0.05, vmax=1e4), cmap="turbo"
    )
    # plt.title(title)
    plt.xlabel(r"$m_{T^{\prime}}$ (GeV)")
    plt.ylabel(r"$m_{\phi}$ (GeV)")
    plt.colorbar(label=label)
    hep.cms.label("Work in Progress", data=True, lumi="138", ax=ax)
    plt.savefig(name, bbox_inches="tight")

mxs = np.logspace(np.log10(799), np.log10(3001), 100, base=10)
mys = np.logspace(np.log10(74), np.log10(501), 100, base=10)

xx, yy = np.meshgrid(mxs, mys)

interpolated = {}
grids = {}

for key, val in limits.items():
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
        t = f'Observed exclusion limits (fb)'
    else:
        if label == '50.0':
            t = f'Median expected exclusion limits (fb)'
        else:
            t = f'{label}% expected exclusion limits (fb)'
    colormesh(xx, yy, grid, t, "plots/limit2D_interp_{}_{}.pdf".format(label,'withCR' if args.withCR else 'noCR'))

for key in range(6):
    if key == 0: label = '2.5'
    elif key == 1: label = '16.0'
    elif key == 2: label = '50.0'
    elif key == 3: label = '84.0'
    elif key == 4: label = '97.5'
    elif key == 5: label = 'Observed'
    val = limits[key]
    if label == 'Observed':
        t = f'Observed exclusion limits (fb)'
    else:
        if label == '50.0':
            t = f'Median expected exclusion limits (fb)'
        else:
            t = f'{label}% expected exclusion limits (fb)'
    scatter2d(val, t, "plots/limit2D_scatter_{}_{}.pdf".format(label,'withCR' if args.withCR else 'noCR'))

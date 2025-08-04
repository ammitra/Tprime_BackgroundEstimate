import ROOT, uproot 
import matplotlib.pyplot as plt
import numpy as np
import mplhep as hep
from helpers import *
import os
import scipy

def add_cms_label(ax, year, data=True, label="Preliminary", loc=2, lumi=True, fontsize=36):
    if year == "all":
        hep.cms.label(
            label,
            data=data,
            lumi='138',
            year=None,
            ax=ax,
            loc=loc,
            fontsize=fontsize
        )
    else:
        hep.cms.label(
            label,
            data=data,
            #lumi=f"{LUMI[year] / 1e3:.0f}" if lumi else None,
            year=year,
            ax=ax,
            loc=loc,
            fontsize=fontsize
        )

# Create TH2s and save to root file for uproot
input_file = '1100-175_unblind_fits/postfitshapes_b.root'

# Get data and total background 
procs = ['TotalBkg','data_obs']
for y in ['16','16APV','17','18']:
    procs.append(f'TprimeB-1100-175_{y}')
histos_TH2 = {}
histos_TH2['SR_pass'] = get_hists(input_file,'SR_pass',procs,prefit=False)

out = ROOT.TFile.Open('PostfitDistributions_SR_pass.root','RECREATE')
out.cd()

for k,v in histos_TH2['SR_pass'].items():
    v.SetName(k)
    v.SetTitle(k)
    v.Write()

# Make a histogram of bkg uncertainty
bkg = histos_TH2['SR_pass']['TotalBkg']
unc = bkg.Clone('BkgUnc')
unc.Reset()
for i in range(1,bkg.GetNbinsX()+1):
    for j in range(1,bkg.GetNbinsY()+1):
        err = bkg.GetBinError(i,j)
        unc.SetBinContent(i,j,err)
unc.Write()
# Make a histogram of data uncert
data = histos_TH2['SR_pass']['data_obs']
unc = data.Clone('DataUnc')
unc.Reset()
for i in range(1,data.GetNbinsX()+1):
    for j in range(1,data.GetNbinsY()+1):
        err = data.GetBinError(i,j)
        unc.SetBinContent(i,j,err)
unc.Write()

# Make a histogram of total signal
dummy = histos_TH2['SR_pass']['data_obs']
SigTot = dummy.Clone('SigTot')
SigTot.Reset()
for y in ['16','16APV','17','18']:
    SigTot.Add(histos_TH2['SR_pass'][f'TprimeB-1100-175_{y}'])
# Now zero out the values outside the region general region so the plot doesn't look atrocious
for i in range(1,SigTot.GetNbinsX()+1):
    for j in range(1, SigTot.GetNbinsY()+1):
        if (i<4) and (j<6):
            SigTot.SetBinContent(i,j,0.0)
        elif (j>9):
            SigTot.SetBinContent(i,j,0.0)
        elif (i>7):
            SigTot.SetBinContent(i,j,0.0)
SigTot.Write()

out.Close()

TEST = ROOT.TFile.Open('SHAPES.root','RECREATE')
TEST.cd()
for k,h in histos_TH2['SR_pass'].items():
    h.Write()
TEST.Close()

# Use uproot to read the TH2s
f = 'PostfitDistributions_SR_pass.root'
data = uproot.open(f)['data_obs']
bkg  = uproot.open(f)['TotalBkg']
Bunc = uproot.open(f)['BkgUnc']
Dunc = uproot.open(f)['DataUnc'] 
sig  = uproot.open(f)['SigTot']

data, binX, binY = data.to_numpy()
bkg, binX, binY  = bkg.to_numpy()
Dunc, binX, binY  = Dunc.to_numpy()
Bunc, binX, binY  = Bunc.to_numpy()

print(binX)
print(binY)

sig_tot, binX, binY = sig.to_numpy()
sig_tot = sig_tot * 1.7621E-01 # scale by S+B r value

################################################################
# fig,ax=plt.subplots()
# hep.hist2dplot(sig_tot, binX, binY, ax=ax, flow=None, labels=False)
# fig.savefig('plots/pulls_TEST.png')
################################################################

data_minus_bkg = data - bkg
sigma = np.sqrt(abs(bkg - Bunc**2))
pull = data_minus_bkg / (sigma + 1e-1)
print(pull)

print(abs(pull.max()))

# Plot signal contours
sig_hist = sig_tot / sigma
levels = np.array([0.05, 0.5, 0.95]) * np.max(sig_hist)

# Create interpolated grid with 4x more points
x = np.array([(binX[i] + binX[i + 1]) / 2 for i in range(len(binX) - 1)])
y = np.array([(binY[i] + binY[i + 1]) / 2 for i in range(len(binY) - 1)])
x_interp = np.linspace(x.min(), x.max(), len(x) * 4)
y_interp = np.linspace(y.min(), y.max(), len(y) * 4)

# Interpolate signal histogram with increased smoothing
sig_interp = scipy.interpolate.RectBivariateSpline(
    y, x, sig_tot.T, s=8.
)  # Added smoothing parameter

print(sig_interp)

# Use edges instead of centers for interpolation range
x_edges = binX #np.array([1000.,1100.,1200.,1300.,1600.])#binX
y_edges = binY #np.array([700., 800.,  900., 1000., 1500.])#binY
x_interp = np.linspace(x_edges[0], x_edges[-1], len(x) * 4)
y_interp = np.linspace(y_edges[0], y_edges[-1], len(y) * 4)
X, Y = np.meshgrid(x_interp, y_interp)
Z = sig_interp(y_interp, x_interp)

################################################################
# fig,ax=plt.subplots()
# hep.hist2dplot(Z, ax=ax, flow=None, labels=False)
# fig.savefig('plots/Pulls_Z.png')
###############################################################


plt.style.use([hep.style.CMS])
fig, ax = plt.subplots(figsize=(12, 12))

ax.tick_params(axis='x', labelrotation=45)
ax.set_xlabel(r'$m_{\phi}^{rec}$ [GeV]', fontsize=36)
ax.set_ylabel(r'$m_{T^\prime}^{rec}$ [GeV]', fontsize=36)

# 2D Pull plot
#hep.hist2dplot(pull, binX, binY, ax=ax, flow=None, labels=False)
h2d = hep.hist2dplot(pull, binX, binY, cmap="viridis", ax=ax, cmin=-3.5, cmax=3.5)
h2d.cbar.set_label(r"(Data - Bkg.) / $\sigma$", fontsize=36)
h2d.cbar.ax.tick_params(labelsize=36)
h2d.pcolormesh.set_edgecolor("face")

sig_colour = "white"

# ax.contour(
#     X,
#     Y,
#     Z,
#     #levels=levels,
#     levels=np.array([0.15, 0.3, 0.45, 0.6, 0.75]),
#     colors=sig_colour,
#     # linestyles=["--", "-", "--"],
#     linewidths=5,
# )
# ax.clabel(cs, cs.levels, inline=True, fmt="%.2f", fontsize=12)


xticks = [100, 200, 300, 400, 500]
ax.set_xticks(xticks)
ax.set_xticklabels([f"{x:.0f}" for x in xticks], rotation=0, fontsize=36)

yticks = [1000, 1500, 2000, 2500, 3000, 3500]
ax.tick_params(axis="y", labelsize=36)
ax.set_yticks(yticks)
ax.set_yticklabels([f"{y:.0f}" for y in yticks])

# print(Z)
# print(cs.levels); exit()

# # Add legend for signal contours
# handles, labels = ax.get_legend_handles_labels()
# # Create proxy artist for contour lines
# contour_proxy = plt.Line2D([], [], color=sig_colour, linestyle="-", linewidth=5)
# handles.append(contour_proxy)
# labels.append(r'$X[1200]\to HY[900]$ / $\sigma$')
# ax.legend(
#     handles,
#     labels,
#     loc="upper right",
#     #bbox_to_anchor=(1.0, 0.98),  # Moved down from default 1.0
#     # fontsize=28,
#     frameon=False,
#     prop={"size": 40}
# )


ax.text(
    0.65,
    0.9,
    'SR Pass',
    transform=ax.transAxes,
    fontsize=40,
    fontproperties="Tex Gyre Heros:bold",
)

prelim=True
add_cms_label(
    ax, "all", data=True, label="Preliminary" if prelim else None, loc=0, fontsize=40
)
fig.savefig(f'plots/postfit2Dpulls_{"Preliminary" if prelim else "Final"}.pdf', bbox_inches='tight')
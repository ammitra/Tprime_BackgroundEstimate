import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
from matplotlib.lines import Line2D

MTs = [800,  900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000]
MPs_existing  = [75, 100, 125, 175, 200, 250, 350, 450, 500]
MPs_generated = [150, 225, 275, 300, 325, 375, 400, 425, 475]

existing_x = []
existing_y = []

interpolated_x = []
interpolated_y = []

for MT in MTs:
    for MP in MPs_existing:
        existing_x.append(MT)
        existing_y.append(MP)
    for MP in MPs_generated:
        interpolated_x.append(MT)
        interpolated_y.append(MP)

# fontsize
fs = 36
plt.rcParams.update({"font.size": fs})

plt.style.use([hep.style.CMS])
fig, ax = plt.subplots(dpi=200)

ax.tick_params(axis="both", which="major", labelsize=fs-4)

ax.set_xlim(600, 3200)
ax.set_ylim(50, 550)

######################## Y-axis (Phi) ################################
# Major ticks every 100, minor ticks every 25
major_ticks_Y = np.arange(50, 576, 100)
minor_ticks_Y = np.arange(50, 576, 25)

ax.set_yticks(major_ticks_Y)
ax.set_yticks(minor_ticks_Y, minor=True)

# Now draw lines indicating the binning 
# xbins = [60,80,100,120,140,160,180,200,220,260,300,560]
# ybins = [800,900,1000,1100,1200,1300,1400,1500,1700,2000,3500]
# ax.hlines(xbins, xmin=np.full_like(xbins, 800), xmax=np.full_like(xbins, 3500), linestyles='dashed', colors='gray') # phi masses are on y-axis
# ax.vlines(ybins, ymin=np.full_like(ybins, 60), ymax=np.full_like(ybins, 560), linestyles='dashed', colors='gray')

# Dict containing the mPhi value after which extrapolation doesn't work for each mT
bad = {800: 125, 900: 175, 1000: 200, 1100: 250, 1200: 250, 1300: 250, 1400: 250, 1500: 250, 1600: 250, 1700: 350, 1800: 350, 1900: 350, 2000: 350, 2100: 350, 2200: 350, 2300: 350, 2400: 350, 2500: 350, 2600: 350, 2700: 350, 2800: 350, 2900: 350, 3000: 350}
# Draw lines indicating where interpolation no longer holds
for mt, mp in bad.items():
    plt.hlines(y=mp-10, xmin=mt-50, xmax=mt+50, linestyle='solid', color='black')
plt.hlines(y=510, xmin=750, xmax=3050, linestyle='solid', color='black')
plt.vlines(x=750, ymin=115, ymax=510, linestyle='solid', color='black')
plt.vlines(x=3050, ymin=340, ymax=510, linestyle='solid', color='black')
plt.vlines(x=850, ymin=115, ymax=165, linestyle='solid', color='black')
plt.vlines(x=950, ymin=165, ymax=190, linestyle='solid', color='black')
plt.vlines(x=1050, ymin=190, ymax=240, linestyle='solid', color='black')
plt.vlines(x=1650, ymin=240, ymax=340, linestyle='solid', color='black')

# ax.scatter(existing_x, existing_y, c='#3f90da')
# ax.scatter(interpolated_x, interpolated_y, c='#bd1f01')

ax.plot(existing_x, existing_y, color='#3f90da', marker='o', fillstyle='full', linestyle='none')
#ax.plot(interpolated_x, interpolated_y, color='#bd1f01', marker='o', fillstyle='none', linestyle='none')
# Now add markers to the points we can interpolate
for mt, mp in bad.items():
    # loop over the interpolated sigs
    for MP in MPs_generated:
        if MP < mp:
            ax.plot(mt, MP, color='#bd1f01', marker='o', fillstyle='full', linestyle='none')
        else:
            # Don't plot anything
            #ax.plot(mt, MP, color="#ffffff", marker='o', fillstyle='full', linestyle='none')
            continue

circles = [
    #Line2D([0], [0], marker='o', color='#bd1f01', label='Interpolated (not used)', markerfacecolor='#bd1f01', fillstyle='none', markersize=15, linewidth=0),
    Line2D([0], [0], marker='o', color='#bd1f01', label='Interpolated', markerfacecolor='#bd1f01', markersize=15, linewidth=0),
    Line2D([0], [0], marker='o', color='#3f90da', label='Official', markerfacecolor='#3f90da', markersize=15, linewidth=0)
]

hep.cms.label(loc=0, ax=ax, label='', rlabel='', data=False, fontsize=fs)
ax.legend(handles=circles, loc='upper center', ncol=2, fontsize=fs-4)
ax.set_xlabel(r'$m_{T^\prime}$ [GeV]', fontsize=fs)
ax.set_ylabel(r'$m_{\phi}$ [GeV]',fontsize=fs)


plt.savefig('plots/signal_grid.pdf', bbox_inches='tight')
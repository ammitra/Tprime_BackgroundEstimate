from Interpolator import *
import os

'''
# Dict containing the mPhi value after which extrapolation doesn't work for each mT
bad = {800: 125, 900: 175, 1000: 200, 1100: 250, 1200: 250, 1300: 250, 1400: 250, 1500: 250, 1600: 250, 1700: 350, 1800: 350, 1900: 350, 2000: 350, 2100: 350, 2200: 350, 2300: 350, 2400: 350, 2500: 350, 2600: 350, 2700: 350, 2800: 350, 2900: 350, 3000: 350}

mts = [i for i in range(800,3100,100)]
for mt in mts:
    for mp in [150, 225, 275, 300, 325, 375, 400, 425, 475]:
        if mp > bad[mt]:
            print(f'no valid interpolation can be performed for {mt}-{mp}, skipping')
            continue
        if os.path.exists(f'rootfiles/THselection_TprimeB-{mt}-{mp}_16APV.root'): continue
        i = Interpolator(mt, mp, '16APV')
        #h = i.Interpolate(i.histos[0])
        i.InterpolateAllHists()
'''
if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-y', type=str, dest='year',
                        action='store', default='16',
                        help='Run 2 year')
    parser.add_argument('-s', type=str, dest='sigmass',
                        action='store', default='1800-125',
                        help='mass of Tprime and Phi cand')
    args = parser.parse_args()

    mt = int(args.sigmass.split('-')[0])
    mp = int(args.sigmass.split('-')[-1])

    i = Interpolator(mt, mp, args.year)
    i.InterpolateAllHists()
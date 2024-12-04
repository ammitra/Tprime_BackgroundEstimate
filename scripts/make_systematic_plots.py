from TwoDAlphabet import plot
from TwoDAlphabet.twoDalphabet import TwoDAlphabet

dir = '1800-125_unblind_fits'
twoD = TwoDAlphabet(dir,f'{dir}/runConfig.json',loadPrevious=True)
plot.make_systematic_plots(twoD)

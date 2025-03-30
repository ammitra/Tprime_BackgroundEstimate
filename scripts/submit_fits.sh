#!/bin/bash

# We will just hard-code some basic arguments that should be applicable to all fits (don't feel like coding CLI argument handling)
verbosity=2
tol=5
strat=1
rMin=-1
rMax=2

for mt in `seq 800 100 3000`; do
    for mp in 75 100 125 175 200 250 350 450 500; do
        sig="${mt}-${mp}"
        if [ ! -f "${sig}_unblind_fits/TprimeB-${sig}-SR0x0-CR0x0_area/card_original_2DAlphabet.txt" ]; then 
            echo "Workspace does not exist for ${sig}, skipping..."
        else
            echo "Submitting FitDiagnostics to condor for signal ${sig}"
            echo "python condor/submit_fits.py --sig ${sig} --verbosity ${verbosity} --tol ${tol} --strat ${strat} --rMin ${rMin} --rMax ${rMax}"
            python condor/submit_fits.py --sig $sig --verbosity $verbosity --tol $tol --strat $strat --rMin $rMin --rMax $rMax
        fi
    done
done
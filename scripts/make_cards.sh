#!/bin/bash

signals=`cat condor/valid_signals.txt`
for sig in $signals; do 
    if [ ! -f "${sig}_unblind_fits/TprimeB-${sig}-SR0x0-CR0x0_area/card_original_2DAlphabet.txt" ]; then 
        echo "Making combined card for signal ${sig}"
        python jointSRttbarCR.py -w "${sig}_unblind_" -s $sig --SRtf 0x0 --CRtf 0x0 --makeCard
    else
        echo "Combined card for signal ${sig} already exists, skipping..."
    fi
done
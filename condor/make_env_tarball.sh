#!/bin/bash
cd $CMSSW_BASE/../
tar --exclude-caches-all --exclude-vcs -cvzf CMSSW_14_1_0_pre4_env.tgz \
    --exclude=tmp --exclude=".scram" --exclude=".SCRAM" \
    --exclude=CMSSW_14_1_0_pre4/src/XHYbbWW \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/UncertPlots \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/Tprime*/plots_* \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/Tprime*/*.tgz \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/Tprime*/notneeded \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/ledger_* \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/binnings.p \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/runConfig.json \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/VHF_* \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/pre_automcstats_18Sept24_results \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/results_* \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/SimulFit_JEScorr_TTmcstatsfits \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/organized_hists.root \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/*.md \
    --exclude=CMSSW_14_1_0_pre4/src/twoD-env \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/autoMCstats/test_fit \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/Tprime*/*fit*.txt \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/Tprime*/*_command.txt \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/Tprime*/*.log \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/Tprime*/*.out \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/Tprime*/card_original_2DAlphabet.txt \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/Tprime*/ledger_* \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/Tprime*/PostFit*.txt \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime/*fits/Tprime*/nuisance_pulls.* \
    CMSSW_14_1_0_pre4
xrdcp -f CMSSW_14_1_0_pre4_env.tgz root://cmseos.fnal.gov//store/user/$USER/
cd $CMSSW_BASE/src/Tprime

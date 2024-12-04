#!/bin/bash

# This script will make the tarball of the CMSSW environment with this custom 2DAlphabet. It will be used to generate the workspaces on condor in parallel, since doing it locally will take ages

cd $CMSSW_BASE/../
    tar --exclude-caches-all --exclude-vcs -cvzf CMSSW_14_1_0_pre4_env.tgz \
    CMSSW_14_1_0_pre4/src/Tprime/autoMCstats \
    --exclude=tmp --exclude=".scram" --exclude=".SCRAM" \
    --exclude=CMSSW_14_1_0_pre4/src/HiggsAnalysis/CombinedLimit/docs \
    --exclude=CMSSW_14_1_0_pre4/src/HiggsAnalysis/CombinedLimit/data/benchmarks \
    --exclude=CMSSW_14_1_0_pre4/src/HiggsAnalysis/CombinedLimit/data/tutorials \
    --exclude=CMSSW_14_1_0_pre4/src/autoMCstats/organized_hists.root \
    --exclude=CMSSW_14_1_0_pre4/src/autoMCstats/backup* \
    --exclude=CMSSW_14_1_0_pre4/src/XHYbbWW \
    --exclude=CMSSW_14_1_0_pre4/src/Tprime \
    --exclude=CMSSW_14_1_0_pre4/src/for_tamas \
    --exclude=CMSSW_14_1_0_pre4/src/twoD-env \
    CMSSW_14_1_0_pre4
xrdcp -f CMSSW_14_1_0_pre4_env.tgz root://cmseos.fnal.gov//store/user/$USER/
cd $CMSSW_BASE/src/Tprime

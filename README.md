# $T^\prime \to t\phi$ fitting infrastructure

Repository containing the fitting infrastructure for the $T^\prime \to t \phi$ (fully hadronic) Run 2 analysis. 

### Installing 2DAlphabet
On `el9` architecture, `cmslpc-el9.fnal.gov`:


```
cmsrel CMSSW_14_1_0_pre4
cd CMSSW_14_1_0_pre4/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v10.0.1
cd ../../
git clone --branch CMSWW_14_1_0_pre4 git@github.com:JHU-Tools/CombineHarvester.git
cd CombineHarvester/
cd ..
scramv1 b clean
scramv1 b -j 16
git clone --branch el9_matplotlib_plotting git@github.com:JHU-Tools/2DAlphabet.git
python3 -m virtualenv twoD-env
source twoD-env/bin/activate
cd 2DAlphabet/
python setup.py develop
```


### 1) Offloading 2DAlphabet workspace creation to condor
**NOTE:** workspace creation takes *forever* due to the fact that there are 
* 4 MC processes (ttbar, W/Z+jets, signal)
* templates for each process for 4 years (16APV, 16, 17, 18)
* 10 shape nuisances per W/Z, signal process, each with up/down templates
* 200 extra mcstat nuisances for ttbar 

So the workspaces should really be generated in parallel on condor... 

To do so, first generate a tarball that gets shipped to FNAL EOS that contains Higgs Combine and 2DAlphabet
```
source condor/tar_env_2DAlphabet.sh
```
Then generate the arguments via: 
```
python condor/make_workspace_args.py
```
Then run workspace creation in parallel with 
```
python CondorHelper.py -r condor/run_makeworkspace.sh -i "joint_mcstats_onesig.json jointSRttbarCR.py parse_card_SRCR_mcstats.py" -a condor/workspace_args_tprime.txt
```

### 2) Get the workspaces 

Copies and unpacks the tarballs before cleaning them. 
```
source scripts/get_workspaces.sh
```

### 3) Running fits after workspace creation 

Locally: 
```
python jointSRttbarCR.py -s $sig -w "$sig"_ --SRtf $SRtf --CRtf $CRtf --strat $strat --tol $tol --rMin $rMin --rMax $rMax -v $verbosity --fit 
```

Condor:
```
python condor/submit_fits.py --sig $sig --verbosity $verbosity --tol $tol --strat $strat --rMin $rMin --rMax $rMax 
```

This will generate three files that need to be placed in their respective workspace directory:

* `initialFitWorkspace_$sig.root` - post-fit workspace w/ channel masks 
* `card_$sig.txt` - combined SR+CR datacard with appropriate per-region nuisances as modified by `parse_card_SRCR_mcstats.py`
* `fitDiagnosticsTest_${sig}.root` - post-fit B-only and S+B results 

### 4) Plotting post-fit distributions 

(Only works if you ran the fits locally) 
```
python jointSRttbarCR.py -s $sig -w "$sig"_ --SRtf $SRtf --CRtf $CRtf --plot
```

### 5) Goodness of Fit
You'll want to ship this off to condor. Comment out the call for `test_GoF_plot()` in the `__main__` function, then run: 
```
python jointSRttbarCR.py -s $sig -w "$sig"_ --SRtf $SRtf --CRtf $CRtf --strat $strat --tol $tol --rMin $rMin --rMax $rMax -v $verbosity --gof
```

It will automatically run GoF on data then ship the toys off to condor. It will complain about plotting since the toy files have not finished if you did not uncomment the plot command. Once the condor toys are finished, they will automatically get sent to the workspace directory. All you have to do is comment out the command to run the GoF, uncomment the command to plot the GoF, then re-run the above command. The condor generation is a bit weird, so you have to move the output root files to `/workspace/workspace/notneeded/tmp` first:

```
mv workspace/TPrimeB-$sig-SRtf$SRtf-CRtf$CRtf_area/notneeded/tmp/TPrimeB-$sig-SRtf$SRtf-CRtf$CRtf_area/*.root workspace/TPrimeB-$sig-SRtf$SRtf-CRtf$CRtf_area/notneeded/tmp/
```

and then rerun the GoF plot. 

### 6) Impacts 
Make sure to use `--blind` if you are still blinding the results - this will prevent the recovered signal strength from being included in the plot. 
```
python jointSRttbarCR.py -s $sig -w "$sig"_ --SRtf $SRtf --CRtf $CRtf --strat $strat --tol $tol --rMin $rMin --rMax $rMax -v $verbosity --impacts --blind
```

### 7) Limits 


### Notes on automcstats and other region-specific nuisances

This analysis simultaneously fits a ttbar control region alongside the signal region to help constrain the ttbar normalization and ttbar-specific nuisances (top-pT reweighting). The ttbar CR is formed from the events that have an Xbb-score less than 0.8 (orthogonal to SR) and the fail/pass regions are formed using the DeepAK8MD top tagger at the loose WP. 

Because of how the high ttbar statistics, MC statistical uncertainties are necessary for this analysis in both the SR and CR to provide a good fit. Combines `automcstats` functionality does not work for 2DAlphabet because the workspace uses `TH2` and `RooDataHists`, so we implement them manually. We manually create and apply ttbar MC statistical uncertainties to all of the ttbar in the Pass region of the CR, and to all ttbar in the Pass region of the SR *if* the nominal ttbar prefit yield in that bin is less than 20 events. 

In order to create region-specific ttbar nuisances ***that are not correlated between the SR and CR***, we use a script `parse_card_SRCR_mcstats.py` to modify the 2DAlphabet-created card. Because of how 2DAlphabet is set up, we have to generate MC statistical uncertainty templates for all ttbar processes in all regions, with conflicting names. To understand this, here is an example of an improper implementation:

Say we have a JSON with:
```json
"GLOBAL": {
    "FILE": "THselection_$process.root",
    "FILE_UP": "THselection_$process_$syst_up.root",
    "FILE_DOWN": "THselection_$process_$syst_down.root",
    "HIST": "MHvsMTH_$region__nominal",
    "HIST_UP": "MHvsMTH_$region__$syst_up",
    "HIST_DOWN": "MHvsMTH_$region__$syst_down",
    "path": "root://cmseos.fnal.gov//store/user/ammitra/topHBoostedAllHad/selection",
    "MCStatsPath": "autoMCstats",
    "MCStatsFile": "$process_MCstats.root",
    "SIGNAME": ["TprimeB-MT-MPHI"]
},
"PROCESSES": {
    "ttbar_16APV": {
        "SYSTEMATICS":[
            ...,
            "SR_pass_mcstats_1_1",
            "SR_pass_mcstats_1_2", 
            ...
        ]
    },
    ...
},
"SYSTEMATICS": {
    "SR_pass_mcstats_1_1": {
        "UP": "MCStatsPath/MCStatsFile:HIST_UP",
        "DOWN": "MCStatsPath/MCStatsFile:HIST_DOWN",
        "SIGMA": 1.0
    },
    ...
}
```

2DAlphabet *will not allow this*, because it thinks that the nuisance `SR_pass_mcstats_1_1` should be applied to process `ttbar_16APV` in *all regions*. This means that when it makes the workspace and does the `GLOBAL` find and replace, it will eventually search for the file+histogram, e.g.:

```
MCStatsPath/MCStatsFile:HIST_UP
autoMCstats/$process_MCstats.root:MHvsMTH_$region__$syst_up
autoMCstats/ttbar_16APV_MCstats.root:MHvsMTH_SR_fail__SR_pass_mcstats_1_1
```

As you can see, the histogram `MHvsMTH_SR_fail__SR_pass_mcstats_1_1` doesn't make any sense - it implies a statistical uncertainty on the `(1,1)` bin of the `SR_pass`, in the `SR_fail` region. This is an unavoidable issue facing the current (as of Nov.18, 2024) version of 2DAlphabet. 

My solution is for `autoMCstats/generate_autoMCstats.py` to generate histograms for all possible combinations of regions and bins, even if they don't make sense. The histograms which wouldn't make sense (like in the example above) just get set to some dummy value. 

The script `parse_card_SRCR_mcstats.py` then goes through the default Combine card that 2DAlphabet creates and modifies the nuisance parameter lines so that they are only applicable in the appropriate regions. A short summary of the fixes the script makes to the cards is:

* ensures that `PNetXbb_mistag` is applied only to ttbar in the SR (since PNet Xbb tagger is not used in the CR)
* ensures that `DAK8Top_tag` is applied only to ttbar in the CR (since DAK8MD top tagger is not used in the SR)
* ensures that all SR mcstats uncertainties are applied only to ttbar in the SR pass
* ensures that all CR mcstats uncertainteis are applied only to ttbar in the CR pass


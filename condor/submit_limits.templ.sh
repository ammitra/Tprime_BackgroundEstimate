#!/bin/bash
# shellcheck disable=SC2154,SC2046,SC1091,SC2086,SC1036,SC1088,SC1098

####################################################################################################
# Script for running bias test
#
# Author: Raghav Kansal, adapted Amitav Mitra
####################################################################################################

echo "Starting job on $$(date)" # Date/time of start of job
echo "Running on: $$(uname -a)" # Condor job is running on this node
echo "System software: $$(cat /etc/redhat-release)" # Operating System on that node

####################################################################################################
# Get my tarred CMSSW with combine already compiled
####################################################################################################

source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp -s root://cmseos.fnal.gov//store/user/ammitra/CMSSW_14_1_0_pre4_env.tgz .
export SCRAM_ARCH=el9_amd64_gcc12

echo "scramv1 project CMSSW CMSSW_14_1_0_pre4"
scramv1 project CMSSW CMSSW_14_1_0_pre4

echo "extracting tar"
tar -xf CMSSW_14_1_0_pre4_env.tgz
rm CMSSW_14_1_0_pre4_env.tgz
echo "CMSSW_14_1_0_pre4/src/"
cd CMSSW_14_1_0_pre4/src/
echo "pwd"
pwd
#echo "scramv1 b ProjectRename"
#scramv1 b ProjectRename # this handles linking the already compiled code - do NOT recompile
eval `scramv1 runtime -sh` # cmsenv is an alias not on the workers
echo $$CMSSW_BASE "is the CMSSW we have on the local worker node"
cd ../..

echo "ls -lh"
ls -lh 

##############################################################
#                   First run limits on the card             #
##############################################################
# Modify the card to point to the current directory instead of one above (this is a 2DAlphabet remnant)
echo "sed -i 's-../base.root-./base.root-g' card.txt"
sed -i 's-../base.root-./base.root-g' card.txt
# Run the limits on the card
(set -x; combine -M AsymptoticLimits -d "card_${sig}.txt" --saveWorkspace -v 2 -n "_${sig}_card" -s $seed)
(set -x; combine -M AsymptoticLimits -d "initialFitWorkspace_${sig}.root" --snapshotName initialFit --saveWorkspace -v 2 -n "_${sig}_workspace" -s $seed)

echo "ls -lh"
ls -lh
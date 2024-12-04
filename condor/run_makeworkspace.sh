#!/bin/bash
echo "Run script starting"
echo "Running on: `uname -a`"
echo "System software: `cat /etc/redhat-release`"

# Set up pre-compiled CMSSW env
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/ammitra/CMSSW_14_1_0_pre4_env.tgz ./
export SCRAM_ARCH=el9_amd64_gcc12
scramv1 project CMSSW CMSSW_14_1_0_pre4
echo "Unpacking compiled CMSSW environment tarball..."
tar -xzf CMSSW_14_1_0_pre4_env.tgz
rm CMSSW_14_1_0_pre4_env.tgz
mkdir tardir; cp tarball.tgz tardir/; cd tardir/
tar -xzf tarball.tgz; rm tarball.tgz
cp -r * ../CMSSW_14_1_0_pre4/src/Tprime/; cd ../CMSSW_14_1_0_pre4/src/

# CMSREL and virtual env setup
echo 'IN RELEASE'
pwd
ls
echo 'scramv1 runtime -sh'
eval `scramv1 runtime -sh`
echo $CMSSW_BASE "is the CMSSW we have on the local worker node"
rm -rf twoD-env
echo 'python3 -m venv twoD-env'
python3 -m venv twoD-env
echo 'source twoD-env/bin/activate'
source twoD-env/bin/activate
echo "$(which python3)"

# set up 2DAlphabet
cd 2DAlphabet
pwd
ls
echo "STARTING 2DALPHABET SETUP...."
python setup.py develop
echo "FINISHING 2DALPHABET SETUP...."
cd ../Tprime

# xrootd debug & certs
#export XRD_LOGLEVEL=Debug
export X509_CERT_DIR=/cvmfs/grid.cern.ch/etc/grid-security/certificates/

# Get args
workspace=$2

echo "python jointSRttbarCR.py " $*
python jointSRttbarCR.py $*

echo "tar -czvf ${2}fits.tar.gz ${2}fits"
tar -czvf "${2}fits.tar.gz" "${2}fits"

xrdcp -f *.gz root://cmseos.fnal.gov//store/user/ammitra/topHBoostedAllHad/workspaces/

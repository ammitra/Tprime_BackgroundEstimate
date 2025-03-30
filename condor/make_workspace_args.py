import glob, os

# Use snapshots, since this will only get signal files that have been successfully processed
inDir = '/uscms/home/ammitra/nobackup/TopPhi_analysis/CMSSW_12_3_5/src/TopHBoostedAllHad/dijet_nano/*.txt'
snapshotFiles = glob.glob(inDir)

# First, just check which of the snapshot files actually have entries. If they have no entries, then we need to redo them.
for snf in snapshotFiles:
    if 'Tprime' not in snf: continue
    num_lines = sum(1 for _ in open(snf,'r'))
    if num_lines == 0:
        print(f'ERROR: Snapshot file {snf} has zero entries...')

signalFiles = [i.split('/')[-1].split('.')[0].split('_')[0] for i in snapshotFiles if ('Tprime' in i) and ('_18' in i)]

f = open('condor/Tprime_signals.txt','r')
signames = [i.strip() for i in f.readlines()]
f.close()

out = open('condor/workspace_args_tprime.txt','w')
for sig in signames:
    # format is MT-MPHI
    MT   = sig.split('-')[0]
    MPHI = sig.split('-')[1]
    SRtf = '0x0'
    CRtf = '0x0'

    out.write(f'-w {MT}-{MPHI}_unblind_ -s {MT}-{MPHI} --SRtf {SRtf} --CRtf {CRtf} --make\n')

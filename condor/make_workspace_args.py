import glob

# Use snapshots, since this will only get signal files that have been successfully processed
inDir = '/uscms/home/ammitra/nobackup/TopPhi_analysis/CMSSW_11_1_4/src/TopHBoostedAllHad/dijet_nano/*.txt'
snapshotFiles = glob.glob(inDir)
signalFiles = [i.split('/')[-1].split('.')[0].split('_')[0] for i in snapshotFiles if ('Tprime' in i) and ('_18' in i)]

f = open('condor/Tprime_signals.txt','r')
signames = [i.strip() for i in f.readlines()]
f.close()

out = open('condor/workspace_args_tprime.txt','w')
for sig in signames:
    # format is TprimeB-MT-MPHI
    MT   = sig.split('-')[1]
    MPHI = sig.split('-')[2]
    SRtf = '0x0'
    CRtf = '0x0'

    out.write(f'-w {MT}-{MPHI}_unblind_ -s {MT}-{MPHI} --SRtf {SRtf} --CRtf {CRtf} --make\n')

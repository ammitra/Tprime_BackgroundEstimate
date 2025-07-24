'''
Script to fit the signal shapes with a double-sided crystal ball function and record the fit function parameters for later linear interpolation.
'''
import ROOT
from ROOT import TFile, RooRealVar, RooArgList, RooDataHist, RooHistPdf, RooFit, RooArgSet, RooMomentMorphFuncND, RooBinning, RooWrapperPdf

ROOT.gROOT.SetBatch(True)

# X = mPhi
xMin = 60
xMax = 560
nX   = 50

# Y = mT
yMin = 800
yMax = 3500
nY   = 27

def create_RDH_PDF(h):
    '''Create a RooDataHist and RooHistPdf from a TH2'''
    xvar = RooRealVar('mPhi','mPhi',xMin,xMax)
    yvar = RooRealVar('mT','mT',yMin,yMax)
    RAL_myvars = RooArgList(xvar,yvar)
    RAS_myvars = RooArgSet(RAL_myvars)
    RDH = RooDataHist('RDH','RDH',RAL_myvars,h)
    RHP = RooHistPdf('RHP','RHP',RAS_myvars,RDH)
    return RDH, RHP

def getBin(binning, val):
    '''Get the bin number corresponding to a given value in a RooBinning object'''
    if (val > binning.highBound()):
        return binning.numBins()
    else:
        return binning.binNumber(val)
    
def plot(frameX, frameY, RDH, model, mPhi, mT, year, pf, syst):
    RDH.plotOn(frameX, RooFit.LineColor(ROOT.kBlue))
    RDH.plotOn(frameY, RooFit.LineColor(ROOT.kBlue))
    model.plotOn(frameX, RooFit.LineColor(ROOT.kRed))
    model.plotOn(frameY, RooFit.LineColor(ROOT.kRed))
    c = ROOT.TCanvas('c','c',800,600)
    c.Divide(2,1)
    c.cd(1)
    frameX.Draw()
    c.cd(2)
    frameY.Draw()
    c.Print(f'plots/{mT}-{mPhi}-{pf}__{syst}_{year}_fitResult.pdf')

def fit(inFile, ws, outFile, x, y, year, histName, syst, pf, mPhi, mT):
    # Load the file, get histogram, convert to RooHistPdf
    try:
        f = TFile.Open(inFile)
    except:
        print(f'File {inFile} does not exist, skipping...')
        return
    h = f.Get(histName)
    nEvents = h.Integral()
    RDH, RHP = create_RDH_PDF(h)
    f.Close()
    # Set up the DSCB objects in X and Y. Unfortunately, these parameters are mostly not known a-priori and hard to estimate initial values for.
    muX = RooRealVar(f"muX-{mT}-{mPhi}-{pf}__{syst}_{year}","muX",float(mPhi), 60. ,560.)
    wdX = RooRealVar(f"wdX-{mT}-{mPhi}-{pf}__{syst}_{year}","wdX",20., 0.001 ,100.)
    a1X = RooRealVar(f"a1X-{mT}-{mPhi}-{pf}__{syst}_{year}","a1X",3. ,0.001 ,100.)
    p1X = RooRealVar(f"p1X-{mT}-{mPhi}-{pf}__{syst}_{year}","p1X",3. ,0.1 ,100.)
    a2X = RooRealVar(f"a2X-{mT}-{mPhi}-{pf}__{syst}_{year}","a2X",3. ,0.001 ,100.)
    p2X = RooRealVar(f"p2X-{mT}-{mPhi}-{pf}__{syst}_{year}","p2X",3. ,0.001 ,100.)
    muY = RooRealVar(f"muY-{mT}-{mPhi}-{pf}__{syst}_{year}","muY",float(mT), 1. ,4000.)
    wdY = RooRealVar(f"wdY-{mT}-{mPhi}-{pf}__{syst}_{year}","wdY",140. ,0.001 ,500.)
    a1Y = RooRealVar(f"a1Y-{mT}-{mPhi}-{pf}__{syst}_{year}","a1Y",10. ,0.001 ,100.)
    p1Y = RooRealVar(f"p1Y-{mT}-{mPhi}-{pf}__{syst}_{year}","p1Y",10. ,0.001 ,100.)
    a2Y = RooRealVar(f"a2Y-{mT}-{mPhi}-{pf}__{syst}_{year}","a2Y",10. ,0.001 ,100.)
    p2Y = RooRealVar(f"p2Y-{mT}-{mPhi}-{pf}__{syst}_{year}","p2Y",10. ,0.001 ,100.)
    cbX = ROOT.RooCrystalBall(f"DSCBX-{mT}-{mPhi}-{pf}__{syst}_{year}","DSCBX",x,muX,wdX,a1X,p1X,a2X,p2X)
    cbY = ROOT.RooCrystalBall(f"DSCBY-{mT}-{mPhi}-{pf}__{syst}_{year}","DSCBY",y,muY,wdY,a1Y,p1Y,a2Y,p2Y)
    # Create the model as a product of the two DSCBs
    model = ROOT.RooProdPdf(f"model-{mT}-{mPhi}-{pf}__{syst}_{year}","model", RooArgList(cbX, cbY))
    # Fit the model to the RooDataHist for the given signal
    fitResult = model.fitTo(RDH,ROOT.RooFit.Save())
    # Plot the fit result
    plot(x.frame(), y.frame(), RDH, model, mPhi, mT, year, pf, syst)

    # Save out all the information to a CSV
    # out = open(f'params/{mT}-{mPhi}-{pf}__{syst}_{year}_fitResult.csv','w')
    # parNames = ['mT','mPhi']
    # parVals  = [str(mT),str(mPhi)]
    # parErrs  = []
    # pars = fitResult.floatParsFinal()
    # for i in range(len(pars)):
    #     par  = pars.at(i)
    #     name = str(par.getTitle())
    #     val  = str(par.getVal())
    #     err  = par.getError()
    #     parNames.append(name)
    #     parVals.append(val)
    # parNames.append('nEvents')
    # parVals.append(str(nEvents))
    # out.write(','.join(parNames)+'\n')
    # out.write(','.join(parVals))
    n = ROOT.RooConstVar(f'nEvents-{mT}-{mPhi}-{pf}__{syst}_{year}',f'nEvents-{mT}-{mPhi}-{pf}__{syst}_{year}',nEvents)
    ws.Import(n, ROOT.RooFit.Silence(True))


    # The RooWorkspace::import function can't be used in PyROOT because import is a reserved python keyword. For this reason, an alternative with a capitalized name is provided: 
    ws.Import(cbX,   ROOT.RooFit.Silence(True))
    ws.Import(cbY,   ROOT.RooFit.Silence(True))
    ws.Import(model, ROOT.RooFit.Silence(True), ROOT.RooFit.RenameConflictNodes('_copy'))
    # ws.Import(x, ROOT.RooFit.Silence(True))
    # ws.Import(y, ROOT.RooFit.Silence(True))
    outFile.cd()

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    # parser.add_argument('-s', type=str, dest='signal',
    #                     action='store', required=True,
    #                     help='Signal name in form mT-mPhi')
    parser.add_argument('-y', type=str, dest='year',
                        action='store', required=True,
                        help='Run II year')
    args = parser.parse_args()


    MTs = [800,  900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000]
    MPs = [75, 100, 125, 175, 200, 250, 350, 450, 500]

    # RooRealVars for X and Y
    x = RooRealVar('mPhi','mPhi',xMin,xMax)
    y = RooRealVar('mT','mT',yMin,yMax)


    for year in [args.year]:
        outFile = ROOT.TFile.Open(f'params/AllFitShapes_{year}.root','RECREATE')
        ws = ROOT.RooWorkspace('w')
        outFile.cd()
        for MT in MTs:
            for MP in MPs:
                signal = f'{MT}-{MP}'
                #eosFile = f'root://cmsxrootd.fnal.gov//store/user/ammitra/topHBoostedAllHad/selection/THselection_TprimeB-{signal}_{year}.root'
                eosFile = f'root://cmseos.fnal.gov//store/user/ammitra/topHBoostedAllHad/selection/THselection_TprimeB-{signal}_{year}.root'
                inFile = eosFile

                try:
                    testFile = TFile.Open(inFile)
                except:
                    print(f'File {inFile} does not exist, skipping...')
                    continue

                allHists = [i.GetName() for i in testFile.GetListOfKeys()]
                for region in ['SR','ttbarCR']:
                        for pf in ['fail','pass']:
                            pf_name = f'{region}_{pf}'

                            #histName = f'MHvsMTH_{pf_name}__nominal'
                            #fit(inFile, ws, outFile, x, y, year, histName, pf_name, MP, MT)
                            

                            region_hists = [i for i in allHists if pf_name in i]
                            for histName in region_hists:
                                #histName = f'MHvsMTH_{pf_name}__nominal'
                                syst = histName.split('__')[-1]
                                fit(inFile, ws, outFile, x, y, year, histName, syst, pf_name, MP, MT)
                            
        ws.Write()
        outFile.Close()

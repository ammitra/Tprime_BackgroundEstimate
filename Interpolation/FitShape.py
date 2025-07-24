'''
Script to fit the signal shapes with a double-sided crystal ball function and record the fit function parameters for later linear interpolation.
'''
import ROOT
from ROOT import TFile, RooRealVar, RooArgList, RooDataHist, RooHistPdf, RooFit, RooArgSet, RooMomentMorphFuncND, RooBinning, RooWrapperPdf

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
    
def plot(frameX, frameY, RDH, model, mPhi, mT):
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
    c.Print(f'plots/{mT}-{mPhi}_fitResult.pdf')

def fit(inFile, year, histName, mPhi, mT):
    # RooRealVars for X and Y
    x = RooRealVar('mPhi','mPhi',xMin,xMax)
    y = RooRealVar('mT','mT',yMin,yMax)
    # Load the file, get histogram, convert to RooHistPdf
    f = TFile.Open(inFile)
    h = f.Get(histName)
    nEvents = h.Integral()
    RDH, RHP = create_RDH_PDF(h)
    f.Close()
    # Set up the DSCB objects in X and Y. Unfortunately, these parameters are mostly not known a-priori and hard to estimate initial values for.
    muX = RooRealVar(f"muX-{mT}-{mPhi}","muX",float(mPhi), 60. ,560.)
    wdX = RooRealVar(f"wdX-{mT}-{mPhi}","wdX",20., 0.001 ,100.)
    a1X = RooRealVar(f"a1X-{mT}-{mPhi}","a1X",5., 0.001, 100.)
    p1X = RooRealVar(f"p1X-{mT}-{mPhi}","p1X",15., 2., 100.)
    a2X = RooRealVar(f"a2X-{mT}-{mPhi}","a2X",5., 0.001, 100.)
    p2X = RooRealVar(f"p2X-{mT}-{mPhi}","p2X",5., 0.001, 100.)
    muY = RooRealVar(f"muY-{mT}-{mPhi}","muY",float(mT), 0.001 ,4000.)
    wdY = RooRealVar(f"wdY-{mT}-{mPhi}","wdY",140., 0.001, 500.)
    a1Y = RooRealVar(f"a1Y-{mT}-{mPhi}","a1Y",10., 0.001 ,100.)
    p1Y = RooRealVar(f"p1Y-{mT}-{mPhi}","p1Y",10., 0.001 ,100.)
    a2Y = RooRealVar(f"a2Y-{mT}-{mPhi}","a2Y",10., 0.001 ,100.)
    p2Y = RooRealVar(f"p2Y-{mT}-{mPhi}","p2Y",10., 0.001 ,100.)
    cbX = ROOT.RooCrystalBall(f"DSCBX-{mT}-{mPhi}","DSCBX",x,muX,wdX,a1X,p1X,a2X,p2X)
    cbY = ROOT.RooCrystalBall(f"DSCBY-{mT}-{mPhi}","DSCBY",y,muY,wdY,a1Y,p1Y,a2Y,p2Y)
    # Create the model as a product of the two DSCBs
    model = ROOT.RooProdPdf(f"model","model", RooArgList(cbX, cbY))
    # Fit the model to the RooDataHist for the given signal
    fitResult = model.fitTo(RDH,ROOT.RooFit.Save())
    # Plot the fit result
    plot(x.frame(), y.frame(), RDH, model, mPhi, mT)
    # Save out all the information to a CSV
    out = open(f'params/{mT}-{mPhi}_{year}_fitResult.csv','w')
    parNames = ['mT','mPhi']
    parVals  = [mT,mPhi]
    parErrs  = []
    pars = fitResult.floatParsFinal()
    for i in range(len(pars)):
        par  = pars.at(i)
        name = str(par.getTitle())
        val  = str(par.getVal())
        err  = par.getError()
        parNames.append(name)
        parVals.append(val)
    parNames.append('nEvents')
    parVals.append(str(nEvents))
    out.write(','.join(parNames)+'\n')
    out.write(','.join(parVals))
    # Save the functions and PDFs to a RooWorkspace
    outFile = TFile.Open(f'params/{mT}-{mPhi}_{year}_ws.root','RECREATE')
    ws = ROOT.RooWorkspace('w')
    # The RooWorkspace::import function can't be used in PyROOT because import is a reserved python keyword. For this reason, an alternative with a capitalized name is provided: 
    ws.Import(cbX,   ROOT.RooFit.Silence(True))
    ws.Import(cbY,   ROOT.RooFit.Silence(True))
    ws.Import(model, ROOT.RooFit.Silence(True), ROOT.RooFit.RenameConflictNodes('_copy'))
    ws.Import(x, ROOT.RooFit.Silence(True))
    ws.Import(y, ROOT.RooFit.Silence(True))
    outFile.cd()
    ws.Write()
    outFile.Close()

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-s', type=str, dest='signal',
                        action='store', required=True,
                        help='Signal name in form mT-mPhi')
    parser.add_argument('-y', type=str, dest='year',
                        action='store', required=True,
                        help='Run II year')
    args = parser.parse_args()

    eosFile = f'root://cmsxrootd.fnal.gov//store/user/ammitra/topHBoostedAllHad/selection/THselection_TprimeB-{args.signal}_{args.year}.root'

    inFile = eosFile
    histName = 'MHvsMTH_SR_pass__nominal'
    mT   = args.signal.split('-')[0]
    mPhi = args.signal.split('-')[-1]

    fit(inFile, args.year, histName, mPhi, mT)
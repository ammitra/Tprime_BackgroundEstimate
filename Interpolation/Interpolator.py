'''
Class to handle interpolation between two existing signal mass points.
'''
import ROOT


MTs = [800,  900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000]
MPs_existing  = [75, 100, 125, 175, 200, 250, 350, 450, 500]
MPs_generated = [150, 225, 275, 300, 325, 375, 400, 425, 475]

# X = mPhi
xMin = 60
xMax = 560
nX   = 50

# Y = mT
yMin = 800
yMax = 3500
nY   = 27

class Interpolator:
    def __init__(self, mT, mPhi, year):
        self.m1, self.m2 = self._get_interp_pairs(mPhi)
        self.mT = mT
        self.mPhi = mPhi
        self.signal = f'{mT}-{mPhi}'
        # RooRealVars
        self.x = ROOT.RooRealVar('mPhi','mPhi',xMin,xMax)
        self.y = ROOT.RooRealVar('mT','mT',yMin,yMax)
        self.year = year
        self.histos = self._get_histos()
        self.f1, self.f2 = self._get_file_pairs()
        # memory management
        self.allVars = []

    def _get_interp_pairs(self, mPhi):
        '''Determines the two existing signals between which to interpolate'''
        m1 = None
        m2 = None
        for mp in MPs_existing:
            if mp <= mPhi:
                m1 = mp
            else:
                m2 = mp
                break
        return m1, m2
    
    def _get_yield_pairs(self, hist):
        '''Gets the yields for the m1 and m2, given a run2 year and histogram'''
        yields = []
        for f in [self.f1, self.f2]:
            h = f.Get(hist)
            y = h.Integral()
            yields.append(y)
        return yields
    
    def _get_file_pairs(self):
        files = []
        for m in [self.m1, self.m2]:
            sig = f'{self.mT}-{m}'
            eosFile = f'root://cmseos.fnal.gov//store/user/ammitra/topHBoostedAllHad/selection/THselection_TprimeB-{sig}_{self.year}.root'
            try:
                f = ROOT.TFile.Open(eosFile)
            except:
                raise FileNotFoundError(f'ERROR: file {eosFile} not found...')
            files.append(f)
        return files          

    def _get_histos(self):
        '''Gets all histograms for a given year'''
        sig = f'{self.mT}-{self.m1}'
        eosFile = f'root://cmseos.fnal.gov//store/user/ammitra/topHBoostedAllHad/selection/THselection_TprimeB-{sig}_{self.year}.root'
        try:
            f = ROOT.TFile.Open(eosFile)
        except:
            raise FileNotFoundError(f'ERROR: file {eosFile} not found...')
        allHists = [i.GetName() for i in f.GetListOfKeys() if ('cutflow' not in i.GetName() and '_CR_' not in i.GetName())]
        return allHists
    
    def _create_RDH_PDF(self, h):
        '''Create a RooDataHist and RooHistPdf from a TH2'''
        xvar = ROOT.RooRealVar('mPhi','mPhi',xMin,xMax)
        yvar = ROOT.RooRealVar('mT','mT',yMin,yMax)
        RAL_myvars = ROOT.RooArgList(xvar,yvar)
        RAS_myvars = ROOT.RooArgSet(RAL_myvars)
        RDH = ROOT.RooDataHist('RDH','RDH',RAL_myvars,h)
        RHP = ROOT.RooHistPdf('RHP','RHP',RAS_myvars,RDH)
        return RDH, RHP

    def _getBin(self, binning, val):
        '''Get the bin number corresponding to a given value in a RooBinning object'''
        if (val > binning.highBound()):
            return binning.numBins()
        else:
            return binning.binNumber(val)
        
    def _linearInterpolate(self, x, x1, y1, x2, y2):
        return y1 + ( (x - x1) * (y2 - y1) ) / (x2 - x1)

    def FitShape(self, f, histName):
        '''Fit a given histogram with a 2D DSCB function. Return the PDFs along x and y'''
        h = f.Get(histName)
        RDH, RHP = self._create_RDH_PDF(h)
        print('fitting shape...')
        # Set up the DSCB objects in X and Y. Unfortunately, these parameters are mostly not known a-priori and hard to estimate initial values for.
        muX = ROOT.RooRealVar(f"muX-{self.mT}-{self.mPhi}","muX",float(self.mPhi), 60. ,560.)
        wdX = ROOT.RooRealVar(f"wdX-{self.mT}-{self.mPhi}","wdX",20., 0.001 ,100.)
        a1X = ROOT.RooRealVar(f"a1X-{self.mT}-{self.mPhi}","a1X",5., 0.001, 100.)
        p1X = ROOT.RooRealVar(f"p1X-{self.mT}-{self.mPhi}","p1X",15., 2., 100.)
        a2X = ROOT.RooRealVar(f"a2X-{self.mT}-{self.mPhi}","a2X",5., 0.001, 100.)
        p2X = ROOT.RooRealVar(f"p2X-{self.mT}-{self.mPhi}","p2X",5., 0.001, 100.)
        muY = ROOT.RooRealVar(f"muY-{self.mT}-{self.mPhi}","muY",float(self.mT), 0.001 ,4000.)
        wdY = ROOT.RooRealVar(f"wdY-{self.mT}-{self.mPhi}","wdY",140., 0.001, 500.)
        a1Y = ROOT.RooRealVar(f"a1Y-{self.mT}-{self.mPhi}","a1Y",10., 0.001 ,100.)
        p1Y = ROOT.RooRealVar(f"p1Y-{self.mT}-{self.mPhi}","p1Y",10., 0.001 ,100.)
        a2Y = ROOT.RooRealVar(f"a2Y-{self.mT}-{self.mPhi}","a2Y",10., 0.001 ,100.)
        p2Y = ROOT.RooRealVar(f"p2Y-{self.mT}-{self.mPhi}","p2Y",10., 0.001 ,100.)
        cbX = ROOT.RooCrystalBall(f"DSCBX-{self.mT}-{self.mPhi}","DSCBX",self.x,muX,wdX,a1X,p1X,a2X,p2X)
        cbY = ROOT.RooCrystalBall(f"DSCBY-{self.mT}-{self.mPhi}","DSCBY",self.y,muY,wdY,a1Y,p1Y,a2Y,p2Y)
        # Create the model as a product of the two DSCBs
        model = ROOT.RooProdPdf(f"model","model", ROOT.RooArgList(cbX, cbY))
        # Fit the model to the RooDataHist for the given signal
        fitResult = model.fitTo(RDH,ROOT.RooFit.Save())
        for v in [muX, wdX, a1X, p1X, a2X, p2X, muY, wdY, a1Y, p1Y, a2Y, p2Y, cbX, cbY, model, fitResult]:
            self.allVars.append(v)
        return cbX, cbY
    
    def Interpolate(self, histName):
        '''Interpolate between the two signal shapes for a given histo'''
        print('interpolating')
        # Get the PDFs for the existing signals
        pdf1x, pdf1y = self.FitShape(self.f1, histName)
        pdf2x, pdf2y = self.FitShape(self.f2, histName)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        # Get the alpha parameter to morph the pdf
        alpha = 1.-(float(self.mPhi) - float(self.m1)/float(self.m2) - float(self.m1))
        rmass = ROOT.RooRealVar(f'rmass-{self.mT}-{self.mPhi}', "rmass", alpha, 0., 1.)
        # Perform the morph
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        pdf_mx = ROOT.RooIntegralMorph(f'morph_{self.mT}-{self.mPhi}-{histName}_X', f'morph_{self.mT}-{self.mPhi}-{histName}_X', pdf1x, pdf2x, self.x, rmass)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        pdf_my = ROOT.RooIntegralMorph(f'morph_{self.mT}-{self.mPhi}-{histName}_Y', f'morph_{self.mT}-{self.mPhi}-{histName}_Y', pdf1y, pdf2y, self.y, rmass)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        # Create the product of the two PDFs to get the 2D shape 
        pdf_out = ROOT.RooProdPdf(f"{self.mT}-{self.mPhi}-{histName}",f"{self.mT}-{self.mPhi}-{histName} INTERPOLATED", ROOT.RooArgList(pdf_mx, pdf_my))

        hist = pdf_out.createHistogram(histName, self.x, ROOT.RooFit.Binning(50,60.,560.), ROOT.RooFit.YVar(self.y,ROOT.RooFit.Binning(27,800.,3500.)))
        # Now get the yields for m1 and m2 for this region so we can interpolate between
        n1, n2 = self._get_yield_pairs(histName)
        m_n = self._linearInterpolate(float(self.mPhi), float(self.m1), n1, float(self.m2), n2)
        hist.Scale(m_n)
        return hist

    def InterpolateAllHists(self):
        fOut = ROOT.TFile.Open(f'rootfiles/THselection_TprimeB-{self.mT}-{self.mPhi}_{self.year}.root', 'RECREATE')
        fOut.cd()
        with ROOT.TDirectory.TContext(fOut):
            for histName in self._get_histos():
                hOut = self.Interpolate(histName)
                hOut.SetDirectory(fOut)
                fOut.cd()
                hOut.SetName(hOut.GetName().replace('__mPhi_mT',''))
                hOut.Write()
        fOut.Close()
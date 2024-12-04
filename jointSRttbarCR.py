from time import time
import ROOT
from TwoDAlphabet import plot
from TwoDAlphabet.twoDalphabet import MakeCard, TwoDAlphabet
from TwoDAlphabet.alphawrap import BinnedDistribution, ParametricFunction
from TwoDAlphabet.helpers import make_env_tarball, cd, execute_cmd
from TwoDAlphabet.ftest import FstatCalc
import os
import numpy as np

def _get_other_region_names(pass_reg_name):
    return pass_reg_name, pass_reg_name.replace('SR_fail','ttbarCR_pass')

def _select_signal(row, args):
    signame = args[0]
    poly_order = args[1]
    tt_poly_order = args[2]
    if row.process_type == 'SIGNAL':
        if signame in row.process:
            return True
        else:
            return False
    elif 'Background' in row.process:
        if row.process == 'Background_SR_fail':
            print(f'Adding {row.process} for tf {poly_order} describing QCD in SR FAIL')
            return True
        elif row.process == f'Background_SR_pass_{poly_order}':
            print(f'Adding {row.process} for tf {poly_order} describing QCD in SR PASS')
            return True
        elif row.process == f'Background_ttbarCR_fail':
            print(f'Adding {row.process} for tf {tt_poly_order} describing QCD in ttbarCR FAIL')
            return True
        elif row.process == f'Background_ttbarCR_pass_{tt_poly_order}':
            print(f'Adding {row.process} for tf {tt_poly_order} describing QCD in ttbarCR PASS')
            return True
        else:
            return False
    else:
        return True

def _generate_constraints(nparams):
    out = {}
    for i in range(nparams):
        if i == 0:
            out[i] = {"MIN":-500,"MAX":500}
        else:
            out[i] = {"MIN":-500,"MAX":500}
    return out

_rpf_options = {
    '0x0': {
        'form': '(@0)',
        'constraints': _generate_constraints(1)
    },
    '1x0': {
        'form': '(@0+@1*x)',
        'constraints': _generate_constraints(2)
    },
    '0x1': {
        'form': '(@0+@1*y)',
        'constraints': _generate_constraints(2)
    },
    '1x1': {
        'form': '(@0+@1*x)*(@2+@3*y)',
        'constraints': _generate_constraints(4)
    },
    '2x1': {
        'form': '(@0+@1*x+@2*x**2)*(@3+@4*y)',
        'constraints': _generate_constraints(5)
    },
    '2x2': {
        'form': '(@0+@1*x+@2*x**2)*(@3+@4*y*@5*y**2)',
        'constraints': _generate_constraints(6)
    },
    '3x2': {
        'form': '(@0+@1*x+@2*x**2+@3*x**3)*(@4+@5*y)',
        'constraints': _generate_constraints(6)
    }
}

def test_make(SRorCR='',fr={}, json=''):
    twoD = TwoDAlphabet('{}fits'.format(SRorCR),json,loadPrevious=False,findreplace=fr)
    qcd_hists = twoD.InitQCDHists()

    binning, _ = twoD.GetBinningFor('SR_fail')

    # Set up QCD estimate in SR_fail
    fail_name = 'Background_SR_fail'
    qcd_f = BinnedDistribution(fail_name, qcd_hists['SR_fail'], binning, constant=False)
    twoD.AddAlphaObj('Background_SR_fail', 'SR_fail', qcd_f, title='QCD')

    # set up QCD estimate in ttbarCR_fail
    ttfail_name = 'Background_ttbarCR_fail'
    qcd_ftt = BinnedDistribution(ttfail_name, qcd_hists['ttbarCR_fail'], binning, constant=False)
    twoD.AddAlphaObj('Background_ttbarCR_fail','ttbarCR_fail', qcd_ftt, title='QCD')

    # Try all TFs for the SR and ttbarCR
    for opt_name, opt in _rpf_options.items():
        # TF for SR_fail -> SR_pass
        qcd_rpf_SR = ParametricFunction(
            'Background_SR_rpf_%s'%opt_name, binning, opt['form'],
            constraints = opt['constraints']
        )
        # TF for ttbarCR_fail -> ttbarCR_pass
        qcd_rpf_ttbarCR = ParametricFunction(
            'Background_ttbarCR_rpf_%s'%opt_name, binning, opt['form'],
            constraints = opt['constraints']
        )

        # QCD estimate in SR pass
        qcd_p = qcd_f.Multiply(fail_name.replace('fail','pass')+'_'+opt_name, qcd_rpf_SR)
        twoD.AddAlphaObj('Background_SR_pass_%s'%opt_name, 'SR_pass', qcd_p, title='QCD')
        # QCD estimate in ttbarCR pass
        qcd_ptt = qcd_ftt.Multiply(ttfail_name.replace('fail','pass')+'_'+opt_name, qcd_rpf_ttbarCR)
        twoD.AddAlphaObj('Background_ttbarCR_pass_%s'%opt_name, 'ttbarCR_pass', qcd_ptt, title='QCD')

    twoD.Save()

def test_fit(SRorCR='', signal='', SRtf='', CRtf='', defMinStrat=0, extra='--robustHesse 1', rMin=-1, rMax=10, verbosity=2, set_params=False):
    working_area = '{}fits'.format(SRorCR)
    twoD = TwoDAlphabet(working_area, '{}/runConfig.json'.format(working_area), loadPrevious=True)

    subset = twoD.ledger.select(_select_signal, 'TprimeB-{}'.format(signal), SRtf, CRtf)

    ###############################################################################
    # WARNING ---------------------------------------------------------------------
    # This script is designed to fit the SR+CR where automcstats for ttbar are 
    # modeled in either ttbarCR_pass or ttbarCR_pass AND SR_pass. 
    # For the former, use "parse_cards.py"
    # For the latter, use "parse_card_SRCR_mcstats.py"
    # and ensure the proper systematics are described in the json. 
    # Also, the Xbb mistag parameter is specific to the SR and the DAK8 top tag 
    # parameter is specific to the CR. So these params are fixed in the parse_card 
    # routine. 
    ###############################################################################
    from parse_card_SRCR_mcstats import parse_card
    print('Making 2DAlphabet card')
    twoD.MakeCard(subset, 'TprimeB-{}-SR{}-CR{}_area'.format(signal, SRtf, CRtf))
    # rename the 2DAlphabet-produced card
    print('Creating new card with automcstats for ttbar only in ttbarCR and SR pass')
    execute_cmd(f'mv {working_area}/TprimeB-{signal}-SR{SRtf}-CR{CRtf}_area/card.txt {working_area}/TprimeB-{signal}-SR{SRtf}-CR{CRtf}_area/card_original_2DAlphabet.txt')
    # create the new card with mcstats only in ttbarCR pass
    parse_card(f'{working_area}/TprimeB-{signal}-SR{SRtf}-CR{CRtf}_area/card_original_2DAlphabet.txt')
    execute_cmd(f'mv card_new.txt {working_area}/TprimeB-{signal}-SR{SRtf}-CR{CRtf}_area/card.txt')
    execute_cmd(f'mv DEBUG.txt {working_area}/TprimeB-{signal}-SR{SRtf}-CR{CRtf}_area/DEBUG_card.txt')

    # Use postfit b-only results as starting point for s+b fits (helps the s+b fits converge for some signal mass pts...)
    if set_params:
        print('Obtaining postfit b-only parameter values...')
        setParams = {}
        f = ROOT.TFile.Open(f'{working_area}/TprimeB-{signal}-SR{SRtf}-CR{CRtf}_area/fitDiagnosticsTest.root','READ')
        fit_b = f.Get('fit_b')
        fit_b_pars = fit_b.floatParsFinal()
        for par in fit_b_pars:
            setParams[f'{par.getTitle()}'] = f'{par.getVal()}'
        f.Close()
    else:
        setParams={}

    # now we can run the ML fit for this signal
    twoD.MLfit('TprimeB-{}-SR{}-CR{}_area'.format(signal,SRtf,CRtf),rMin=rMin,rMax=rMax,setParams=setParams,verbosity=verbosity,defMinStrat=defMinStrat,extra=extra)

def test_plot(SRorCR='', signal='', SRtf='', CRtf=''):
    working_area = '{}fits'.format(SRorCR)
    twoD = TwoDAlphabet(working_area, '{}/runConfig.json'.format(working_area), loadPrevious=True)
    subset = twoD.ledger.select(_select_signal, 'TprimeB-{}'.format(signal), SRtf, CRtf)

    # First make the nuisance pulls without mcstats params
    regex='^(?!.*(_bin_|_par|_mcstats_))'
    diffnuis_cmd = f"python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py {working_area}/TprimeB-{signal}-SR{SRtf}-CR{CRtf}_area/fitDiagnosticsTest.root --abs -g {working_area}/TprimeB-{signal}-SR{SRtf}-CR{CRtf}_area/nuisance_pulls_noMCstats.root --all --regex='{regex}'"
    execute_cmd(diffnuis_cmd)
    # Make a PDF of the output
    nuis_file = ROOT.TFile.Open(f'{working_area}/TprimeB-{signal}-SR{SRtf}-CR{CRtf}_area/nuisance_pulls_noMCstats.root')
    nuis_can = nuis_file.Get('nuisances')
    nuis_can.Print(f'{working_area}/TprimeB-{signal}-SR{SRtf}-CR{CRtf}_area/nuisance_pulls_noMCstats.pdf','pdf')
    nuis_file.Close()

    # customize the plots to include region definitions
    subtitles = {
        "SR_fail": r"$ParticleNet_{TvsQCD}$ Pass;$ParticleNetMD_{Xbb}$ Fail",
        "SR_pass": r"$ParticleNet_{TvsQCD}$ Pass;$ParticleNetMD_{Xbb}$ Pass",
        "ttbarCR_fail": r"$ParticleNet_{TvsQCD}$ Pass;$DeepAK8MD_{TvsQCD}$ Fail",
        "ttbarCR_pass": r"$ParticleNet_{TvsQCD}$ Pass;$DeepAK8MD_{TvsQCD}$ Pass"
    }
    regions = [['SR'],['ttbarCR'],['SR_fail','SR_pass','ttbarCR_pass']]
    twoD.StdPlots('TprimeB-{}-SR{}-CR{}_area'.format(signal,SRtf,CRtf), subset, subtitles=subtitles, regionsToGroup=regions)

def test_GoF(SRorCR, signal, SRtf='', CRtf='', condor=True, extra='', appendName=''):
    #assert SRorCR == 'CR'
    working_area = '{}fits'.format(SRorCR)
    twoD = TwoDAlphabet(working_area, '{}/runConfig.json'.format(working_area), loadPrevious=True)
    signame = 'TprimeB-'+signal
    if not os.path.exists(twoD.tag+'/'+signame+'-SR{}-CR{}_area/card.txt'.format(SRtf,CRtf)):
        subset = twoD.ledger.select(_select_signal, signame, SRtf, CRtf)
        twoD.MakeCard(subset, 'TprimeB-{}-SR{}-CR{}_area'.format(signal, SRtf, CRtf))
    if condor == False:
        twoD.GoodnessOfFit(
            signame+'-SR{}-CR{}_area'.format(SRtf,CRtf), ntoys=500, freezeSignal=0,
            condor=False, card_or_w='initialFitWorkspace.root', extra=extra, appendName=appendName
        )
    else:
        twoD.GoodnessOfFit(
            signame+'-SR{}-CR{}_area'.format(SRtf,CRtf), ntoys=500, freezeSignal=0,
            condor=True, njobs=50, card_or_w='initialFitWorkspace.root', extra=extra, appendName=appendName
        )

def test_GoF_plot(SRorCR, signal, SRtf='', CRtf='', condor=True, appendName=''):
    '''Plot the GoF in ttbar<SRorCR>/TprimeB-<signal>_area (condor=True indicates that condor jobs need to be unpacked)'''
    signame = 'TprimeB-'+signal
    plot.plot_gof(f'{SRorCR}fits','{}-SR{}-CR{}_area'.format(signame,SRtf,CRtf), condor=condor, appendName=appendName)

def load_RPF(twoD, signal='1800-125', SRtf='', CRtf=''):
    params_to_set = twoD.GetParamsOnMatch('rpf.*', 'TprimeB-{}-SR{}-CR{}_area'.format(signal,SRtf,CRtf), 'b')
    return {k:v['val'] for k,v in params_to_set.items()}

def test_SigInj(SRorCR, r, signal='1800-125', SRtf='', CRtf='', extra='', rMin=-1, rMax=10,strat=0, condor=True, set_params=False, scale_rpf=1.0):
    '''Perform a signal injection test'''
    twoD = TwoDAlphabet('{}fits'.format(SRorCR), '{}fits/runConfig.json'.format(SRorCR), loadPrevious=True)
    params = load_RPF(twoD,signal,SRtf,CRtf)

    if set_params:
        import ROOT
        print('Obtaining postfit b-only parameter values...')
        setParams = {}
        working_area = f'{signal}_JEScorr_fits'
        f = ROOT.TFile.Open(f'{working_area}/TprimeB-{signal}-SR{SRtf}-CR{CRtf}_area/fitDiagnosticsTest.root','READ')
        fit_b = f.Get('fit_b')
        fit_b_pars = fit_b.floatParsFinal()
        for par in fit_b_pars:
            setParams[f'{par.getTitle()}'] = f'{par.getVal()}'
        f.Close()
        params.update(setParams)

    if scale_rpf != 1.0:
        print(params)
        print("Scaling rpf params for sig injection")
        for rpf_name, rpf_val in params.items():
            if ("par0" in rpf_name) and ('SR' in rpf_name):
                print(f'\tScaling {rpf_name} by a factor of {scale_rpf}')
                # Sometimes we want to inflate bkg to check if positive signal bias comes from low stats
                # par0 sets the overall scale
                params[rpf_name] = rpf_val*scale_rpf
        print(params)

    twoD.SignalInjection(
        'TprimeB-{}-SR{}-CR{}_area'.format(signal,SRtf,CRtf),
        injectAmount = r,       # amount of signal to inject (r=0 <- bias test)
        ntoys = 500,
        njobs = 50,
        blindData = False,      # working with toy data, no need to blind
        card_or_w = 'initialFitWorkspace.root',
        setParams = params,     # give the toys the same RPF params
        verbosity = 0,
        extra = extra,
        rMin = rMin,
        rMax = rMax,
        defMinStrat = strat,
        condor = condor)

def test_SigInj_plot(SRorCR, r, signal='1800-125', SRtf='', CRtf='', condor=False):
    plot.plot_signalInjection('{}fits'.format(SRorCR),'TprimeB-{}-SR{}-CR{}_area'.format(signal,SRtf,CRtf), injectedAmount=r, condor=condor)


def test_Impacts(SRorCR,signal='1800-125',SRtf='',CRtf='', rMin=-1, rMax=10, strat=0, extra='', blind=False):
    twoD = TwoDAlphabet('{}fits'.format(SRorCR), '{}fits/runConfig.json'.format(SRorCR), loadPrevious=True)

    twoD.Impacts(
        'TprimeB-{}-SR{}-CR{}_area'.format(signal,SRtf,CRtf), 
        rMin=rMin, 
        rMax=rMax, 
        cardOrW='initialFitWorkspace.root --snapshotName initialFit',
        defMinStrat=strat, 
        extra=extra,
        blind=blind
    )

def test_limits(SRorCR, signal, SRtf, CRtf):
    working_area = '{}fits'.format(SRorCR)
    twoD = TwoDAlphabet(working_area, '{}/runConfig.json'.format(working_area), loadPrevious=True)
    twoD.Limit(
        subtag='TprimeB-{}-SR{}-CR{}_area'.format(signal, SRtf, CRtf),
        blindData=False,        # BE SURE TO CHANGE THIS IF YOU NEED TO BLIND YOUR DATA
        verbosity=2,
        condor=False
    )

def test_analyze(SRorCR, signal, SRtf, CRtf):
    working_area = '{}fits'.format(SRorCR)
    twoD = TwoDAlphabet(working_area, '{}/runConfig.json'.format(working_area), loadPrevious=True)
    twoD.AnalyzeNLL(subtag='TprimeB-{}-SR{}-CR{}_area'.format(signal, SRtf, CRtf),workspace='higgsCombineTest.FitDiagnostics.mH120.root:w')

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-w', type=str, dest='workspace',
                        action='store', default='jointSRttbarCR',
                        help='workspace name')
    parser.add_argument('-s', type=str, dest='sigmass',
                        action='store', default='1800-125',
                        help='mass of Tprime and Phi cand')
    parser.add_argument('--json', type=str, dest='json', 
                        action='store', default='joint_mcstats_onesig.json',
                        help='path to JSON file for making the initial workspace')
    parser.add_argument('--SRtf', type=str, dest='SRtf',
                        action='store', required=True,
                        help='TF parameterization for SR tf')
    parser.add_argument('--CRtf', type=str, dest='CRtf',
                        action='store', required=True,
                        help='TF parameterization for CR tf')
    parser.add_argument('--condor', dest='condor',
                        action='store_true',
                        help='If passed as argument, use Condor for methods')
    parser.add_argument('--make', dest='make',
                        action='store_true', 
                        help='If passed as argument, create 2DAlphabet workspace')
    parser.add_argument('--fit', dest='fit',
                        action='store_true',
                        help='If passed as argument, fit with the given TFs')
    parser.add_argument('--setParams', dest='setParams',
                        action='store_true',
                        help='Uses the b-only parameter values in s+b fit (helps some signal s+b fits converge)')
    parser.add_argument('--plot', dest='plot',
                        action='store_true',
                        help='If passed as argument, plot the result of the fit with the given TFs')
    parser.add_argument('--gof', dest='gof',
                        action='store_true',
                        help='If passed as argument, run GoF test for the fit with the given TFs')
    parser.add_argument('--rinj', type=float, dest='rinj',
                        action='store', default='0.0',
                        help='Value of signal strength to inject')
    parser.add_argument('--inject', dest='inject',
                        action='store_true',
                        help='If passed as argument, run signal injection test for the fit with the given TFs')
    parser.add_argument('--scaleRPF',dest='scaleRPF',
                        action='store',type=float, default=1.0,
                        help='Amount by which to scale the RPF to inflate bkgs in the signal injection test')
    parser.add_argument('--impacts', dest='impacts',
                        action='store_true',
                        help='If passed as argument, run impacts for the fit with the given TFs')
    parser.add_argument('--limit', dest='limit',
                        action='store_true',
                        help='If passed as argumnet, run the limit for the fit with the given TFs')
    parser.add_argument('--analyzeNLL', dest='analyzeNLL',
                        action='store_true',
                        help='Analyze NLL as function of all nuisances')
    parser.add_argument('--blind', dest='blind',
                        action='store_true',
                        help='blind impact plot')

    # Fit options
    parser.add_argument('--strat', dest='strat',
                        action='store', default='0',
                        help='Default minimizer strategy')
    parser.add_argument('--tol', dest='tol',
                        action='store', default='0.1',
                        help='Default minimizer tolerance')
    parser.add_argument('--robustFit', dest='robustFit',
                        action='store_true',
                        help='If passed as argument, uses robustFit algo')
    parser.add_argument('--robustHesse', dest='robustHesse',
                        action='store_true',
                        help='If passed as argument, uses robustHesse algo')
    parser.add_argument('--rMin', dest='rMin',
                        action='store', default='-1',
                        help='Minimum allowed signal strength')
    parser.add_argument('--rMax', dest='rMax',
                        action='store', default='10',
                        help='Maximium allowed signal strength')
    parser.add_argument('-v', dest='verbosity',
                        action='store', default='2',
                        help='Combine verbosity')

    args = parser.parse_args()

    if args.make:
        MT   = args.sigmass.split('-')[0]
        MPHI = args.sigmass.split('-')[-1]
        fr = {'TprimeB-MT-MPHI':f'TprimeB-{MT}-{MPHI}'}
        test_make(args.workspace, fr=fr, json=args.json)
    if args.fit:
        if (args.robustFit) and (args.robustHesse):
            raise ValueError('Cannot use both robustFit and robustHesse algorithms simultaneously') 
        elif (args.robustFit) or (args.robustHesse):
            if args.robustFit:
                algo = f'--robustFit 1'
            else:
                algo = f'--robustHesse 1'
        else:
            algo = ''
        test_fit(
            args.workspace, 
            args.sigmass, 
            SRtf=args.SRtf, 
            CRtf=args.CRtf, 
            defMinStrat=int(args.strat), 
            extra=f'{algo} --cminDefaultMinimizerTolerance {args.tol}',
            rMin=args.rMin,
            rMax=args.rMax,
            verbosity=args.verbosity,
            set_params=args.setParams
        )
    if args.plot:
        test_plot(args.workspace, args.sigmass, SRtf=args.SRtf, CRtf=args.CRtf)
    if args.gof:
        # mask the SR "HIGH" in the gof
        params=','
        masks=[]
        for region in ['SR_fail','SR_pass','ttbarCR_fail','ttbarCR_pass']:
            for channel in ['LOW','SIG','HIGH']:
                    if ('SR' in region) or ('ttbarCR' in region):
                        if (channel == 'HIGH'):
                            masks.append(f'mask_{region}_{channel}=1')
                        else:
                            masks.append(f'mask_{region}_{channel}=0')
                    else:
                        masks.append(f'mask_{region}_{channel}=0')
        params_for_eval = params.join(masks)
        # print(f'USING THE FOLLOWING CHANNEL MASKS: {masks}')
        # test_GoF(
        #     args.workspace, 
        #     args.sigmass, 
        #     SRtf=args.SRtf, 
        #     CRtf=args.CRtf, 
        #     condor=args.condor, 
        #     extra=''#f'--setParametersForEval {params_for_eval}'
        # )
        test_GoF_plot(args.workspace, args.sigmass, SRtf=args.SRtf, CRtf=args.CRtf, condor=args.condor)
    if args.inject:
        if (args.robustFit) and (args.robustHesse):
            raise ValueError('Cannot use both robustFit and robustHesse algorithms simultaneously')
        elif (args.robustFit) or (args.robustHesse):
            if args.robustFit:
                algo = f'--robustFit 1'
            else:
                algo = f'--robustHesse 1'
        else:
            algo = ''
        #test_SigInj(args.workspace, args.rinj, args.sigmass, args.SRtf, args.CRtf, condor=args.condor, rMin=args.rMin, rMax=args.rMax, strat=int(args.strat), extra=f'{algo} --cminDefaultMinimizerTolerance {args.tol}',set_params=args.setParams,scale_rpf=args.scaleRPF)
        test_SigInj_plot(args.workspace, args.rinj, args.sigmass, args.SRtf, args.CRtf, condor=args.condor)
    if args.impacts:
        if (args.robustFit) and (args.robustHesse):
            raise ValueError('Cannot use both robustFit and robustHesse algorithms simultaneously')
        elif (args.robustFit) or (args.robustHesse):
            if args.robustFit:
                algo = f'--robustFit 1'
            else:
                algo = f'--robustHesse 1'
        else:
            algo = ''
        test_Impacts(args.workspace, args.sigmass, args.SRtf, args.CRtf, rMin=args.rMin, rMax=args.rMax, strat=int(args.strat), extra=f'{algo} --cminDefaultMinimizerTolerance {args.tol}',blind=args.blind)
    if args.limit:
        test_limits(args.workspace, args.sigmass, args.SRtf, args.CRtf)
    if args.analyzeNLL:
        test_analyze(args.workspace, args.sigmass, args.SRtf, args.CRtf)


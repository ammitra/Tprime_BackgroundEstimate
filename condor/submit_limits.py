'''
NOTE: This script requires that the fits were produced and exist in the signal directory. 

First run: python condor/submit_fits.py --sig $sig --verbosity $verbosity --tol $tol --strat $strat --rMin $rMin --rMax $rMax 
Then run: python scripts/handle_FitDiagnostics_CondorOutput.py

Then you can run this script for the given signal mass point.
'''
import os 
from pathlib import Path
import argparse
from string import Template

def setup():
    t2_local_prefix = "/eos/uscms/"
    t2_prefix = "root://cmseos.fnal.gov"
    
    proxy = '/uscms/home/ammitra/x509up_u56971'

    username = os.environ["USER"]
    submitdir = Path(__file__).resolve().parent

    return t2_local_prefix, t2_prefix, proxy, username, submitdir

def write_template(templ_file: str, out_file: Path, templ_args: dict, safe: bool = False):
    """Write to ``out_file`` based on template from ``templ_file`` using ``templ_args``"""

    with Path(templ_file).open() as f:
        templ = Template(f.read())

    with Path(out_file).open("w") as f:
        if not safe:
            f.write(templ.substitute(templ_args))
        else:
            f.write(templ.safe_substitute(templ_args))

def main(args):
    t2_local_prefix, t2_prefix, proxy, username, submitdir = setup()
    prefix = f"AsymptoticLimits"
    local_dir = Path(f"condor/limits/{args.sig}/{prefix}")

    # make local directory for output
    logdir = local_dir / "logs"
    logdir.mkdir(parents=True, exist_ok=True)

    jdl_templ = f"{submitdir}/submit_limits.templ.jdl"
    sh_templ = f"{submitdir}/submit_limits.templ.sh"

    # get the location of base.root
    if not args.interpolated:
        base_root_dir = Path(f'{args.sig}_unblind_fits')
    else:
        base_root_dir = Path(f'{args.sig}-INTERPOLATED_unblind_fits')

    local_jdl = Path(f'{local_dir}/{prefix}.jdl')
    local_log = Path(f'{local_dir}/{prefix}.log')

    # Arguments for jdl 
    jdl_args = {
        "dir": local_dir,
        "base_root_dir": base_root_dir,
        "prefix": prefix,
        "sig": args.sig
    }
    write_template(jdl_templ, local_jdl, jdl_args)


    # Arguments for condor shell script
    # The arguments for the masked CR have to be added here, annoyingly
    #   ${maskCRargs}
    #   ${setCRparams} 
    #   ${freezeCRparams}
    localsh = f"{local_dir}/{prefix}.sh"
    sh_args = {
        "sig": args.sig,
        "seed": args.seed,
        "strat": args.strat,
        "tol": args.tol,
        "rmax": args.rmax,
        "maskCRargs": "mask_SR_fail_LOW=0,mask_SR_fail_SIG=0,mask_SR_fail_HIGH=0,mask_SR_pass_LOW=0,mask_SR_pass_SIG=0,mask_SR_pass_HIGH=0,mask_ttbarCR_fail_LOW=1,mask_ttbarCR_fail_SIG=1,mask_ttbarCR_fail_HIGH=1,mask_ttbarCR_pass_LOW=1,mask_ttbarCR_pass_SIG=1,mask_ttbarCR_pass_HIGH=1",
        "setCRparams": "var{ttbarCR.*_mcstats.*}=0,rgx{ttbarCR.*_mcstats.*}=0,var{Background_ttbarCR.*_bin.*}=0,rgx{Background_ttbarCR.*_bin.*}=0,Background_ttbarCR_rpf_0x0_par0=0,DAK8Top_tag=0",
        "freezeCRparams": "var{ttbarCR.*_mcstats.*},rgx{ttbarCR.*_mcstats.*},var{Background_ttbarCR.*_bin.*},rgx{Background_ttbarCR.*_bin.*},DAK8Top_tag,Background_ttbarCR_rpf_0x0_par0"
    }
    write_template(sh_templ, localsh, sh_args)

    os.system(f"chmod u+x {localsh}")

    if local_log.exists():
        local_log.unlink()

    os.system(f"condor_submit {local_jdl}")
    print("To submit ", local_jdl)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sig", help="signal name", type=str, required=True)
    parser.add_argument("--seed", default=123456, help="seed", type=int)
    parser.add_argument("--strat", default=0, help="strat", type=int)
    parser.add_argument("--tol", default=10, help="tol", type=float)
    parser.add_argument("--rmax", default=4, help="rMax", type=float)
    parser.add_argument("--interpolated", help="signal is interpolated", action='store_true')
    args = parser.parse_args()

    main(args)
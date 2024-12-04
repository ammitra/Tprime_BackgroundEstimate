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
    base_root_dir = Path(f'{args.sig}_unblind_fits')

    local_jdl = Path(f'{local_dir}/{prefix}.jdl')
    local_log = Path(f'{local_dir}/{prefix}.log')

    # Arguments for jdl 
    jdl_args = {
        "dir": local_dir,
        "prefix": prefix,
        "sig": args.sig
    }
    write_template(jdl_templ, local_jdl, jdl_args)


    # Arguments for condor shell script
    localsh = f"{local_dir}/{prefix}.sh"
    sh_args = {
        "sig": args.sig,
        "seed": args.seed
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
    args = parser.parse_args()

    main(args)
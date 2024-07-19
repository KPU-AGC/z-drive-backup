#!/home/agc/mambaforge-pypy3/envs/fastqc/bin/python3
__description__ =\
"""
Purpose: To streamline the process of archiving NGS runs from the Z-drive.
"""
__author__ = "Erick Samera"
__version__ = "0.5.1"
__comments__ = "Functional"
# --------------------------------------------------
from argparse import (
    Namespace,
    ArgumentParser,
    RawTextHelpFormatter)
import pathlib
import subprocess
import datetime
# --------------------------------------------------
def get_args() -> Namespace:
    """ Get command-line arguments """
    parser = ArgumentParser(
        usage="%(prog)s [options]",
        description=__description__,
        epilog=f"v{__version__} : {__author__} | {__comments__}",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        '-z',
        '--z-drive',
        dest='z_drive_ngs_dir',
        metavar='<PATH>',
        type=pathlib.Path,
        required=True,
        help='path to NGS run directory (/path/to/NGS/run/on/Z-drive/{date}-{run}_{information}) [REQUIRED]')
    parser.add_argument(
        '-d',
        '--dest',
        dest='archive_dir',
        metavar='<PATH>',
        type=pathlib.Path,
        default=pathlib.Path('/mnt/data/archive/NGS_runs/'),
        help='archive destination path [Default: /mnt/data/archive/NGS_runs/]')
    parser.add_argument(
        '-R',
        '--resolve',
        dest='resolve_arg',
        action='store_true',
        help='try to resolve path from NGS directory ({date}-{run}_{information}) [Default: False]')
    parser.add_argument(
        '-D',
        '--dry-run',
        dest='dry_run_arg',
        action='store_true',
        help='dry run, don\'t copy any files [Default: False]')
    parser.add_argument(
        '--show-fastqc',
        dest='show_fastqc_arg',
        action='store_true',
        help='show progress from fastqc analysis [Default: False]')
    parser.add_argument(
        '--show-multiqc',
        dest='show_multiqc_arg',
        action='store_true',
        help='show progress from multiqc analysis [Default: False]')
    parser.add_argument(
        '-t',
        '--threads',
        dest='threads',
        metavar='<int>',
        type=int,
        default=32,
        help='number of threads to run fastqc analysis [Default: 32]')

    args = parser.parse_args()
    # parser errors and processing
    # --------------------------------------------------
    if args.resolve_arg:
        args.z_drive_ngs_dir = pathlib.Path('/mnt/Z/Raw-data/NGS/').joinpath(args.z_drive_ngs_dir)
    if not args.z_drive_ngs_dir.exists():
        parser.error(f'ERROR! NGS run {args.z_drive_ngs_dir.name} ({args.z_drive_ngs_dir}) doesn\'t exist! Double-check your path!')

    return args
# --------------------------------------------------
def _find_fastq_files(input_dir: pathlib.Path, dry_run_arg: bool = True) -> pathlib.Path:
    """
    """
    command = f'find {input_dir.resolve()} -name "*.fastq.gz"'
    result = subprocess.run(command, capture_output=True, shell=True)
    print_log('DEBUG', f"Found fastq files in directory: '{pathlib.Path(result.stdout.decode().splitlines()[0]).parent}'.")
    if result.stdout.decode().splitlines()[0].strip(): return pathlib.Path(result.stdout.decode().splitlines()[0]).parent
    print_log('FATAL',"Couldn't find any FASTQ files! Quitting!")
    quit()
def _find_miseq_output(input_dir: pathlib.Path, dry_run_arg: bool = True) -> pathlib.Path:
    """
    """
    print_log('DEBUG',f'Trying to find MiSeqOutput directory in {input_dir} ...')
    dirs = [i for i in input_dir.glob('*') if (i.is_dir() and i.name not in ('analysis', 'docs'))]
    for dir in dirs:
        if all([
            all([True if i in '0123456789' else False for i in dir.name.split('_')[0]]),
            len(dir.name.split('_')) == 4,
            len(dir.name.split('-')) == 2]):
            print_log('DEBUG', f"Found MiSeqOutput directory: '{dir}'.")
            return dir
    print_log('FATAL', 'No MiSeq output directory! Quitting!')
    quit()
def _do_fastqc(input_dir: pathlib.Path, fastqc_out_dir: pathlib.Path, dry_run_arg: bool = True, show_fastqc_arg: bool = True, threads: int = 32) -> None:
    """
    """
    fastq_files = [str(file) for file in input_dir.glob('*.fastq*')]
    print_log('DEBUG', f'Found {len(fastq_files)} files to process in {input_dir}.')
    print_log('INFO', f'Running fastqc using {threads} threads ...')
    command = f'fastqc -t {threads} -o {fastqc_out_dir} ' + ' '.join(fastq_files)
    if not dry_run_arg: subprocess.run(command, shell=True, capture_output=not show_fastqc_arg)
    return None
def _do_multiqc(input_dir: pathlib.Path, dry_run_arg: bool = True, show_multiqc_arg = False) -> None:
    """
    """
    print_log('INFO', f'Running multiqc on fastqc analysis dir: {input_dir} ...')
    command = f'multiqc {input_dir} --interactive --outdir {input_dir.parent} --filename multiqc.html'
    if not dry_run_arg: subprocess.run(command, shell=True, capture_output=not show_multiqc_arg)
    run_name = input_dir.parent.parent.name
    source_html_path = input_dir.parent.joinpath('multiqc.html')
    dest_html_path = input_dir.parent.parent.joinpath(f'{run_name}.html')
    command = f'cp {source_html_path} {dest_html_path}'
    if not dry_run_arg: subprocess.run(command, shell=True)
    return None
def _check_outputs(input_dir: pathlib.Path, dry_run: bool, show_fastqc_arg: bool, show_multiqc_arg: bool, threads: int) -> bool:
    """
    Checks the input directory.
    """
    
    print_log('INFO', f"Checking directory structure ...")
    if not input_dir.joinpath('analysis/fastqc').exists():
        if not dry_run: input_dir.joinpath('analysis/fastqc').mkdir(exist_ok=True, parents=True)
        print_log('INFO', f"Created directory directory structure.")
    else: print_log('WARN', 'Analysis directory exists!')

    print_log('INFO', f"Checking fastqc analysis ...")
    if not list(input_dir.joinpath('analysis/fastqc').glob('*.html')):
        MiSeq_output_dir = _find_miseq_output(input_dir, dry_run)
        fastq_dir = _find_fastq_files(MiSeq_output_dir, dry_run)
        _do_fastqc(fastq_dir, input_dir.joinpath('analysis/fastqc'), dry_run, show_fastqc_arg, threads)
        print_log('INFO', f"Performed fastqc analysis!")
    else: print_log('WARN', f"Fastqc analysis already exists!")

    print_log('INFO', f"Checking multiqc analysis ...")
    if not input_dir.joinpath('analysis').joinpath('multiqc.html').exists():
        _do_multiqc(input_dir.joinpath('analysis/fastqc'), dry_run, show_multiqc_arg)
        print_log('INFO', f"Performed multiqc analysis!")
    else: print_log('WARN', f"Multiqc analysis already exists!")
    return None
def _perform_archive(input_dir: pathlib.Path, destination_dir: pathlib.Path, dry_run: bool) -> bool:
    """
    """
    print_log('INFO', f"Checking destination {destination_dir} for {input_dir.name} ...")
    if not destination_dir.joinpath(input_dir.name).exists():
        print_log('INFO', f'Copying {input_dir} to {destination_dir} ...')
        if not dry_run: subprocess.run(f'cp -r {input_dir} {destination_dir}', shell=True)
        print_log('INFO', f'Copied {input_dir} to {destination_dir}!')
    else: print_log('WARN', f"Destination {destination_dir.joinpath(input_dir.name)} already exists!")
    return None
def print_log(level: str, message: str) -> None:
    """
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level.upper()}: {message}")
    return None
def main() -> None:
    """
    """
    args = get_args()

    print_log('INFO', f"Found directory: '{args.z_drive_ngs_dir}'.")
    _check_outputs(args.z_drive_ngs_dir, args.dry_run_arg, args.show_fastqc_arg, args.show_multiqc_arg, args.threads)
    _perform_archive(args.z_drive_ngs_dir, args.archive_dir, args.dry_run_arg)

    print_log('INFO', f"BACKUP COMPLETE !")
    return None
# --------------------------------------------------
if __name__ == '__main__':
    main()

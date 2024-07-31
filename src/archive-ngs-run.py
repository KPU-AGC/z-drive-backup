#!/home/agc/mambaforge-pypy3/envs/fastqc/bin/python3
__description__ =\
"""
Purpose: To streamline the process of archiving NGS runs from the Z-drive.
"""
__author__ = "Erick Samera, Kevin Saulog"
__version__ = "0.8.0"
__comments__ = "added dependencies check (duh), also fixed md5 behaviour"
# --------------------------------------------------
from argparse import (
    Namespace,
    ArgumentParser,
    RawTextHelpFormatter)
import pathlib
# --------------------------------------------------
import subprocess
import datetime
import logging
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
        '--check-phiX',
        dest='do_phix_arg',
        action='store_true',
        help='perform PhiX analysis on Undetermined reads [Default: False]')
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
    logging.debug(f"Found fastq files in directory: '{pathlib.Path(result.stdout.decode().splitlines()[0]).parent}'.")
    if result.stdout.decode().splitlines()[0].strip(): return pathlib.Path(result.stdout.decode().splitlines()[0]).parent
    logging.critical("Couldn't find any FASTQ files! Quitting!")
    quit()
def _find_miseq_output(input_dir: pathlib.Path, dry_run_arg: bool = True) -> pathlib.Path:
    """
    """
    logging.debug(f'Trying to find MiSeqOutput directory in {input_dir} ...')
    dirs = [i for i in input_dir.glob('*') if (i.is_dir() and i.name not in ('analysis', 'docs'))]
    for dir in dirs:
        if all([
            all([True if i in '0123456789' else False for i in dir.name.split('_')[0]]),
            len(dir.name.split('_')) == 4,
            len(dir.name.split('-')) == 2]):
            logging.debug(f"Found MiSeqOutput directory: '{dir}'.")
            return dir
    logging.critical('No MiSeq output directory! Quitting!')
    quit()
def _do_fastqc(input_dir: pathlib.Path, fastqc_out_dir: pathlib.Path, dry_run_arg: bool = True, show_fastqc_arg: bool = True, threads: int = 32) -> None:
    """
    """
    fastq_files = [str(file) for file in input_dir.glob('*.fastq*')]
    logging.debug(f'Found {len(fastq_files)} files to process in {input_dir}.')
    logging.info(f'Running fastqc using {threads} threads ...')
    command = f'fastqc -t {threads} -o {fastqc_out_dir} ' + ' '.join(fastq_files)
    if not dry_run_arg: subprocess.run(command, shell=True, capture_output=not show_fastqc_arg)
    return None
def _do_multiqc(input_dir: pathlib.Path, dry_run_arg: bool = True, show_multiqc_arg = False) -> None:
    """
    """
    logging.info(f'Running multiqc on fastqc analysis dir: {input_dir} ...')
    command = f'multiqc {input_dir} --interactive --outdir {input_dir.parent} --filename multiqc.html'
    if not dry_run_arg: subprocess.run(command, shell=True, capture_output=not show_multiqc_arg)
    run_name = input_dir.parent.parent.name
    source_html_path = input_dir.parent.joinpath('multiqc.html')
    dest_html_path = input_dir.parent.parent.joinpath(f'{run_name}.html')
    command = f'cp {source_html_path} {dest_html_path}'
    if not dry_run_arg: subprocess.run(command, shell=True)
    return None
def _generate_md5(input_dir: pathlib.Path) -> None:
    """
    """
    logging.info(f'Generating md5 hash of {input_dir} ...')
    commmand = f"(cd {input_dir} && find . -type f -print0 | xargs -0 md5sum | sort -k2) > {input_dir.parent.joinpath('checksum.md5')}"
    result = subprocess.run(commmand, shell=True, capture_output=True)
    logging.info(f'Generated md5 hash of {input_dir} .')
    return None
def _check_md5(z_drive_dir: pathlib.Path, local_archive_dir: pathlib.Path) -> bool:
    """
    """
    z_drive_dir = _find_miseq_output(z_drive_dir)
    local_archive_dir = _find_miseq_output(local_archive_dir)

    _generate_md5(z_drive_dir)
    _generate_md5(local_archive_dir)

    logging.info(f'Comparing md5 hashes of {z_drive_dir} and {local_archive_dir} ...')
    with open(z_drive_dir.parent.joinpath('checksum.md5')) as z_drive_checksum_file: z_drive_checksum =  z_drive_checksum_file.read()
    with open(local_archive_dir.parent.joinpath('checksum.md5')) as local_checksum_file: local_checksum =  local_checksum_file.read()

    logging.info(f'Comparing md5 hashes of {z_drive_dir} and {local_archive_dir} .')
    if z_drive_checksum == local_checksum: 
        logging.info(f'md5 hashes validated .')
        return True
    else:
        logging.critical(f'md5 hashes invalid! Something went wrong!')
        return False
def _analyze_phix(input_fastq_dir: pathlib.Path, destination_dir: pathlib.Path, show_fastqc_arg: bool, threads: int):
    """
    """
    
    logging.info(f'Finding Undetermined reads in {input_fastq_dir} ...')
    undetermined_reads: list[pathlib.Path] = list(input_fastq_dir.glob('Undetermined*'))
    if len(undetermined_reads) != 2:
        return ValueError("Expected exactly two (R1/R2) Undetermined reads files.")
    logging.info(f'Found Undetermined reads in {input_fastq_dir}.')

    undetermined_read_1, undetermined_read_2 = None, None
    for file in undetermined_reads:
        read_orientation = file.stem.split('_')[3]
        if '1' in read_orientation:
            undetermined_read_1 = file
        elif '2' in read_orientation:
            undetermined_read_2 = file
        else:
            raise ValueError(f"Unexpected read orientation '{read_orientation}' in file {file}.")
    if not all([undetermined_read_1, undetermined_read_2]): raise ValueError("Both read orientations 'R1' and 'R2' must be present.")

    dest_file: pathlib.Path = destination_dir.joinpath('aln.sam')

    command = f'bowtie2 -x /home/agc/Documents/ref/genomes/phiX/phix174 -1 {undetermined_read_1} -2 {undetermined_read_2} -S {dest_file}'
    try: subprocess.run(command, shell=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        logging.critical(f"Alignment failed.\n{exc.returncode}\n{exc.output}")
        return SyntaxError
    # looks for alignment file
    samfile = list(destination_dir.glob('*sam'))
    if not samfile:
        logging.critical(f"SAM file not found.")
        return ValueError

    # separate forward and reverse files
    command = f'samtools fastq -1 {destination_dir.joinpath("PhiX.R1.fastq.gz")} -2 {destination_dir.joinpath("PhiX.R2.fastq.gz")} {" ".join([str(file) for file in samfile])}'
    try: subprocess.run(command, shell=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        logging.critical(f"Separation of reads failed.\n{exc.returncode}\n{exc.output}")
        return SyntaxError

    fw_fastq = list(destination_dir.glob('*.R1.fastq*'))[0]
    rv_fastq = list(destination_dir.glob('*.R2.fastq*'))[0]

    if not fw_fastq or not rv_fastq:
        logging.critical('fastq not found')
        return LookupError

    command = f'fastqc -t {threads} -o {destination_dir} {fw_fastq} {rv_fastq} {undetermined_read_1} {undetermined_read_2}'
    try: subprocess.run(command, shell=True, stdout=None if not show_fastqc_arg else subprocess.PIPE, stderr=None if not show_fastqc_arg else subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        logging.critical(f"FastQC of reads failed.\n{exc.returncode}\n{exc.output}")
        return SyntaxError

    command = f'multiqc {destination_dir}'
    try: subprocess.run(command, shell=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        logging.critical(f"MultiQC failed.\n{exc.returncode}\n{exc.output}")
        return SyntaxError
def _check_outputs(input_dir: pathlib.Path, dry_run: bool, do_phix_arg: bool, show_fastqc_arg: bool, show_multiqc_arg: bool, threads: int) -> bool:
    """
    Checks the input directory.
    """

    # Check directory structure
    logging.info(f'Checking directory structure ...')
    if not input_dir.joinpath('analysis/fastqc').exists():
        if not dry_run: input_dir.joinpath('analysis/fastqc').mkdir(exist_ok=True, parents=True)
        logging.info(f"Created directory structure .")
    else: logging.warning('Analysis directory exists!')


    # Check fastqc analysis
    logging.info(f'Checking fastqc analysis ...')
    if not list(input_dir.joinpath('analysis/fastqc').glob('*.html')):
        MiSeq_output_dir = _find_miseq_output(input_dir, dry_run)
        fastq_dir = _find_fastq_files(MiSeq_output_dir, dry_run)
        _do_fastqc(fastq_dir, input_dir.joinpath('analysis/fastqc'), dry_run, show_fastqc_arg, threads)
        logging.info(f'Performed fastqc analysis!')
    else: logging.warning('Fastqc analysis already exists!')


    # Check MultiQC analysis
    logging.info(f"Checking multiqc analysis ...")
    if not input_dir.joinpath('analysis').joinpath('multiqc.html').exists():
        _do_multiqc(input_dir.joinpath('analysis/fastqc'), dry_run, show_multiqc_arg)
        logging.info(f"Performed multiqc analysis!")
    else: logging.warning('MultiQC analysis already exists!')


    # Check phiX analysis
    if do_phix_arg:
        logging.info(f"Checking phiX analysis ...")
        if not input_dir.joinpath('analysis/phiX').exists():
            if not dry_run:
                input_dir.joinpath('analysis/phiX').mkdir(exist_ok=True)
                MiSeq_output_dir = _find_miseq_output(input_dir, dry_run)
                fastq_dir = _find_fastq_files(MiSeq_output_dir, dry_run)
                _analyze_phix(fastq_dir, input_dir.joinpath('analysis/phix'), show_fastqc_arg, threads)
            logging.info(f"Performed phiX analysis!")
        else: logging.warning(f"phiX analysis already exists!")
    else: logging.info(f"phiX analysis not specified .")
    return None
def _perform_archive(input_dir: pathlib.Path, destination_dir: pathlib.Path, dry_run: bool) -> bool:
    """
    """
    logging.info(f"Checking destination {destination_dir} for {input_dir.name} ...")
    if not destination_dir.joinpath(input_dir.name).exists():
        logging.info(f'Copying {input_dir} to {destination_dir} ...')
        if not dry_run: subprocess.run(f'cp -r {input_dir} {destination_dir}', shell=True)
        logging.info(f'Copied {input_dir} to {destination_dir}!')
    else: logging.warning(f'Destination {destination_dir.joinpath(input_dir.name)} already exists!')
    return None
def _check_dependencies(software_list: list) -> None:
    """
    """
    for tool in software_list:
            try:
                subprocess.run([tool, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise RuntimeError(f"{tool} is not installed.")
    return None
# --------------------------------------------------
def main() -> None:
    """
    """
    args = get_args()
    _check_dependencies(['fastqc', 'multiqc', 'samtools', 'bowtie2'])

    runtime = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    logging.basicConfig(
        encoding='utf-8',
        level=logging.INFO,
        handlers=[
            logging.FileHandler(pathlib.Path('/mnt/data/archive/archive_logs').joinpath(f'{runtime}_{args.z_drive_ngs_dir.stem}.log')),
            logging.StreamHandler()],
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(levelname)s : %(message)s')

    logging.info(f"Found NGS run directory: '{args.z_drive_ngs_dir}' .")
    _check_outputs(args.z_drive_ngs_dir, args.dry_run_arg, args.do_phix_arg, args.show_fastqc_arg, args.show_multiqc_arg, args.threads)
    # consider adding phiX analysis here as a separate "module" ? -Erick
    _perform_archive(args.z_drive_ngs_dir, args.archive_dir, args.dry_run_arg)

    if not _check_md5(args.z_drive_ngs_dir, args.archive_dir.joinpath(args.z_drive_ngs_dir.stem)): 
        logging.critical("CATASTROPHIC FAILURE SOMEWHERE !")
        return None
    
    logging.info("BACKUP COMPLETE !")
    return None
# --------------------------------------------------
if __name__ == '__main__':
    main()

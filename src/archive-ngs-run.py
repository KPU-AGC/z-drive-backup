#!/home/agc/mambaforge-pypy3/envs/fastqc/bin/python3
__description__ =\
"""
Purpose: To streamline the process of archiving NGS runs from the Z-drive.
"""
__author__ = "Erick Samera, Kevin Saulog"
__version__ = "0.7.1"
__comments__ = "Added md5 checking; TODO: test in prod"
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
        '--show-fastqc',
        dest='show_fastqc_arg',
        action='store_true',#!/home/agc/mambaforge-pypy3/envs/fastqc/bin/python3
__description__ =\
"""
Purpose: To streamline the process of archiving NGS runs from the Z-drive.
"""
__author__ = "Erick Samera, Kevin Saulog"
__version__ = "0.5.1"
__comments__ = "Functional"
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
    commmand = f"(cd {input_dir} && find . -type f -print0 | xargs -0 md5sum) > {input_dir.parent.joinpath('checksum.md5')}"
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
def _analyze_phix(input_dir: pathlib.Path, destination_dir: pathlib.Path, threads):
    undetermined_buckets = [str(file) for file in input_dir.glob('Undetermined*')]
    # Expecting 2 undetermined files
    if len(undetermined_buckets) != 2:
        return ValueError

    for file in undetermined_buckets:
        read_orientation = file.split('_')[3]
        if '1' in read_orientation:
            ud_1 = file
        elif '2' in read_orientation:
            ud_2 = file
        else:
            print('Orientation not found or im stupid')
    
    dest_file = destination_dir / 'aln.sam'
    
    command = f'bowtie2 -x /home/agc/Documents/ref/genomes/phiX/phix174 -1 {ud_1} -2 {ud_2} -S {str(dest_file)}'
    try: 
        subprocess.run(command, shell=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        print(f'Alignment failed.', exc.returncode, exc.output)
        return SyntaxError
    # looks for alignment file
    samfile = destination_dir.glob('*sam')
    if not samfile:
        print(f'Samfile not found')
        return ValueError

    # separate forward and reverse files
    command = f'samtools fastq -1 phix_freads -2 phix_rreads {str(samfile)}'
    try:
        subprocess.run(command, shell=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        print(f'Separation of reads failed.', exc.returncode, exc.output)
        return SyntaxError
    
    fw_fastq = destination_dir.glob('*freads*')
    rv_fastq = destination_dir.glob('*rreads*')

    if not fw_fastq or not rv_fastq:
        print('Fastq not found')
        return LookupError

    command = f'fastqc -t {threads} -o {destination_dir} {fw_fastq} {rv_fastq} {ud_1} {ud_2}'
    try:
        subprocess.run(command, shell=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        print(f'Fastqc failed.', exc.returncode, exc.output)
        return SyntaxError
    
    command = f'multiqc {destination_dir}'
    try:
        subprocess.run(command, shell=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        print(f'Multiqc failed.', exc.returncode, exc.output)
        return SyntaxError
def _check_outputs(input_dir: pathlib.Path, dry_run: bool, show_fastqc_arg: bool, show_multiqc_arg: bool, threads: int) -> bool:
    """
    Checks the input directory.
    """
    
    # Check directory structure
    logging.info(f'Checking directory structure ...')
    if not input_dir.joinpath('analysis/fastqc').exists():
        if not dry_run: input_dir.joinpath('analysis/fastqc').mkdir(exist_ok=True, parents=True)
        logging.info(f"Created directory directory structure.")
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
    logging.info(f"Checking phiX analysis ...")
    if not input_dir.joinpath('analysis/phiX').exists():
        if not dry_run: input_dir.joinpath('analysis/phiX').mkdir(exist_ok=True)
        _analyze_phix(fastq_dir, input_dir.joinpath('analysis/phix'), threads)
        logging.info(f"Performed phiX analysis!")
    else: logging.warning(f"phiX analysis already exists!")


    # Check phiX analysis

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
# --------------------------------------------------
def main() -> None:
    """
    """
    args = get_args()

    runtime = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    logging.basicConfig(
        encoding='utf-8',
        level=logging.INFO,
        handlers=[
            logging.FileHandler(pathlib.Path('/mnt/data/archive/archive_logs').joinpath(f'{runtime}_{args.z_drive_ngs_dir.stem}.log')),
            logging.StreamHandler()],
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(levelname)s : %(message)s')

    logging.info(f"Found directory: '{args.z_drive_ngs_dir}'.")
    _check_outputs(args.z_drive_ngs_dir, args.dry_run_arg, args.show_fastqc_arg, args.show_multiqc_arg, args.threads)
    # consider adding phiX analysis here as a separate "module" ? -Erick
    _perform_archive(args.z_drive_ngs_dir, args.archive_dir, args.dry_run_arg)
    if _check_md5(args.z_drive_ngs_dir, args.archive_dir.joinpath(args.z_drive_ngs_dir.stem)): logging.info("BACKUP COMPLETE !")
    else: logging.critical("CATASTROPHIC FAILURE SOMEWHERE !")
    return None
# --------------------------------------------------
if __name__ == '__main__':
    main()
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
    commmand = f"(cd {input_dir} && find . -type f -print0 | xargs -0 md5sum) > {input_dir.parent.joinpath('checksum.md5')}"
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
def _analyze_phix(input_dir: pathlib.Path, destination_dir: pathlib.Path, threads):
    undetermined_buckets = [str(file) for file in input_dir.glob('Undetermined*')]
    # Expecting 2 undetermined files
    if len(undetermined_buckets) != 2:
        return ValueError

    for file in undetermined_buckets:
        read_orientation = file.split('_')[3]
        if '1' in read_orientation:
            ud_1 = file
        elif '2' in read_orientation:
            ud_2 = file
        else:
            print('Orientation not found or im stupid')
    
    dest_file = destination_dir / 'aln.sam'
    
    command = f'bowtie2 -x /home/agc/Documents/ref/genomes/phiX/phix174 -1 {ud_1} -2 {ud_2} -S {str(dest_file)}'
    try: 
        subprocess.run(command, shell=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        print(f'Alignment failed.', exc.returncode, exc.output)
        return SyntaxError
    # looks for alignment file
    samfile = destination_dir.glob('*sam')
    if not samfile:
        print(f'Samfile not found')
        return ValueError

    # separate forward and reverse files
    command = f'samtools fastq -1 phix_freads -2 phix_rreads {str(samfile)}'
    try:
        subprocess.run(command, shell=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        print(f'Separation of reads failed.', exc.returncode, exc.output)
        return SyntaxError
    
    fw_fastq = destination_dir.glob('*freads*')
    rv_fastq = destination_dir.glob('*rreads*')

    if not fw_fastq or not rv_fastq:
        print('Fastq not found')
        return LookupError

    command = f'fastqc -t {threads} -o {destination_dir} {fw_fastq} {rv_fastq} {ud_1} {ud_2}'
    try:
        subprocess.run(command, shell=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        print(f'Fastqc failed.', exc.returncode, exc.output)
        return SyntaxError
    
    command = f'multiqc {destination_dir}'
    try:
        subprocess.run(command, shell=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        print(f'Multiqc failed.', exc.returncode, exc.output)
        return SyntaxError
def _check_outputs(input_dir: pathlib.Path, dry_run: bool, show_fastqc_arg: bool, show_multiqc_arg: bool, threads: int) -> bool:
    """
    Checks the input directory.
    """
    
    # Check directory structure
    logging.info(f'Checking directory structure ...')
    if not input_dir.joinpath('analysis/fastqc').exists():
        if not dry_run: input_dir.joinpath('analysis/fastqc').mkdir(exist_ok=True, parents=True)
        logging.info(f"Created directory directory structure.")
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
    logging.info(f"Checking phiX analysis ...")
    if not input_dir.joinpath('analysis/phiX').exists():
        if not dry_run: input_dir.joinpath('analysis/phiX').mkdir(exist_ok=True)
        _analyze_phix(fastq_dir, input_dir.joinpath('analysis/phix'), threads)
        logging.info(f"Performed phiX analysis!")
    else: logging.warning(f"phiX analysis already exists!")


    # Check phiX analysis

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
# --------------------------------------------------
def main() -> None:
    """
    """
    args = get_args()

    runtime = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    logging.basicConfig(
        encoding='utf-8',
        level=logging.INFO,
        handlers=[
            logging.FileHandler(pathlib.Path('/mnt/data/archive/archive_logs').joinpath(f'{runtime}_{args.z_drive_ngs_dir.stem}.log')),
            logging.StreamHandler()],
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(levelname)s : %(message)s')

    logging.info(f"Found directory: '{args.z_drive_ngs_dir}'.")
    _check_outputs(args.z_drive_ngs_dir, args.dry_run_arg, args.show_fastqc_arg, args.show_multiqc_arg, args.threads)
    # consider adding phiX analysis here as a separate "module" ? -Erick
    _perform_archive(args.z_drive_ngs_dir, args.archive_dir, args.dry_run_arg)
    if _check_md5(args.z_drive_ngs_dir, args.archive_dir.joinpath(args.z_drive_ngs_dir.stem)): logging.info("BACKUP COMPLETE !")
    else: logging.critical("CATASTROPHIC FAILURE SOMEWHERE !")
    return None
# --------------------------------------------------
if __name__ == '__main__':
    main()

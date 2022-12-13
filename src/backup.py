#!/usr/bin/env python3
__description__ =\
"""
Purpose: Script for robust backup of the Z-drive.
"""
__author__ = "Erick Samera"
__version__ = "1.0.0"
__comments__ = "stable enough"
# --------------------------------------------------
from argparse import (
    Namespace,
    ArgumentParser,
    RawTextHelpFormatter)
from pathlib import Path
# --------------------------------------------------
import shutil
import logging
import json
from datetime import datetime
# --------------------------------------------------
def get_args(_configs) -> Namespace:
    """ Get command-line arguments """

    parser = ArgumentParser(
        description=__description__,
        epilog=f"v{__version__} : {__author__} | {__comments__}",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        'input_path',
        type=Path,
        help="(INPUT) the root path of the flash-drive from where files will be copied")
    parser.add_argument(
        '--instrument',
        dest='instrument',
        choices=_configs['instruments'],
        metavar="NAME",
        required=True,
        help=f"(DESTINATION) target instrument folder on the Z-drive, CHOOSE: {sorted(_configs['instruments'].keys())}")
    parser.add_argument(
        '--check',
        action='store_true',
        help=f"do not copy files, just identify files that do not already exist on the Z-drive.")

    args = parser.parse_args()

    # parser errors and processing
    # --------------------------------------------------
    args.destination_path = Path(_configs['instruments'][args.instrument])
    args.log_path = Path(_configs['log_output'])

    return args
# --------------------------------------------------
def _copy_to_drive(_input_path: Path, _destination_path: Path, _directory_changes: dict, ) -> None:
    """
    Function uses shutil to copy input files to destination from a list of directory changes.

    Paramaters:
        _input_path: Path
            path of input directory, should be the root
        _destination_path: Path
            path of destination directory, should be the instrument
        _directory_changes: dict
            "new_files": list of files that do not exist in the destination
            "updated_files": list of files that do exist, but have been updated

    Returns:
        None
    """

    logging.info("Starting backup ...")

    success_count = 0
    failed_transfers = []

    # iterate over directory changes and perform backup
    for file in _directory_changes['new_files']:
        logging.info(f"Copying {file} ...")
        try:
            # copy the file and all metadata
            if _input_path.joinpath(file).is_file(): shutil.copy2(_input_path.joinpath(file), _destination_path.joinpath(file))
            # dirs don't copy their metadata, just make a dir
            elif _input_path.joinpath(file).is_dir(): _destination_path.joinpath(file).mkdir()
            logging.info(f"Successfully copied {file} .")
            success_count += 1
        except:
            # proceed with the other files but log that this one failed
            logging.warning(f"Error occured trying to copy file: {file}")
            failed_transfers.append(file)

    failed_transfers_str: str = '\n'.join(failed_transfers)
    if failed_transfers: logging.warning(f"Backup finished. Successfully copied {success_count} file(s); {len(failed_transfers)} file(s) failed:\n{failed_transfers_str}")
    else: logging.info(f"Backup finished. Successfully copied {success_count} file(s).")
    return None
def _identify_changes(_input_path: Path, _destination_path: Path) -> dict:
    """
    Function identifies identifies differences between paths and returns a dictionary of changes.

    Parameters:
        _input_path: Path
            path of input directory, should be the root
        _destination_path: Path
            path of destination directory, should be the instrument

    Returns:
        _directory_changes: dict
            "new_files": list of files that do not exist in the destination
            "updated_files": list of files that do exist, but have been updated
    """

    new_files: list = []
    updated_files: list = []

    # recursive list of files in the input, relative to input
    for file in _input_path.glob('**/*'):
        adjusted_path = file.resolve().relative_to(_input_path.resolve())
        if not _destination_path.joinpath(adjusted_path).exists(): new_files.append(adjusted_path)
        elif all([
            _destination_path.joinpath(adjusted_path).exists(),
            _input_path.joinpath(adjusted_path).is_file(),
            _input_path.joinpath(adjusted_path).stat().st_mtime != _input_path.joinpath(adjusted_path).stat().st_mtime]):
            updated_files.append(adjusted_path)

    # counts
    updated_files_num: int = len(updated_files)
    num_files: int = len([thing for thing in new_files if _input_path.joinpath(thing).is_file()])
    num_dirs: int = len([thing for thing in new_files if _input_path.joinpath(thing).is_dir()])
    total: int = num_files + num_dirs

    # generate a human-readable list of updated files and inform that they won't be copied automatically
    updated_files_str: str = '\n'.join([f"\t{str(file)}" for file in updated_files])
    logging.info(f"Found {updated_files_num} modified file(s): \n{updated_files_str}")
    if updated_files_num: logging.info("These files will not be copied automatically!\n")

    # generate a human-readable list of files to copy
    new_files_str: str = '\n'.join([f"\t{str(file)}" for file in new_files])
    logging.info(f"Found {total} total new paths: {num_dirs} folder(s) and {num_files} file(s) :\n{new_files_str}\n")

    return {'new_files': new_files, 'updated_files': updated_files}
def _log_params(args: Namespace) -> None:
    """Log argparse arguments to logfile"""
    logging.info("Using config.json in src/")
    logging.info(f"Input path: {args.input_path}")
    logging.info(f"Instrument: {args.instrument}")
    logging.info(f"Destination path: {args.destination_path}\n")
    if args.check: logging.warning(f'Running --check; files will not be copied!\n')
    return None
def _parse_config() -> dict:
    """
    Function parses config file and returns a dictionary of config parameters.

    Parameters:
        None

    Returns:
        configs: dict
            "metadata": dict
            "instruments": dict
                instrument_name: (str) path to instrument raw data
            "log_output": (str) path of log output directory
    """

    config_path = Path(__file__).parent.joinpath('config.json')
    if config_path.exists():
        # parse the config file and check to make sure it's somewhat filled out
        with open(config_path) as config_file:
            configs = json.load(config_file)
        
        # check to make sure all "required" values are in the config file, raise error otherwise
        required_values = ('instruments', 'log_output')
        all_required_in_configs: bool = all([True for config_value in required_values if config_value in configs])
        if not all_required_in_configs: raise RuntimeError("Invalid config file! Try generating a new one.")
        
        # confirm that all paths are filled out properly in the config
        confirm_paths: bool = all([str(instr_path) for instr_path in configs['instruments'].values()])
        if not confirm_paths: raise RuntimeError("Make sure config files are properly configured!")
    else:
        # generate a config file
        instruments_list = ['GCMS', 'Gel-Images', 'HPLC', 'iScan', 'NGS', 'QuantStudio', 'SeqStudio', 'Tapestation']
        configs = {
            "metadata": {
                "author": __author__,
                "version": __version__,
                "comments": __comments__},
            "instruments":{instrument: "" for instrument in instruments_list}, 
            "log_output": ""}
        json.dump(configs, open(config_path, 'w'), indent = 4)
        RuntimeError("No config file detected. Generating one.")
    return configs
# --------------------------------------------------
def main() -> None:
    """ Insert docstring here """

    # parse config data first so choices can be used in argparse
    configs = _parse_config()
    args = get_args(configs)

    runtime = datetime.now().strftime('%Y%m%d-%H%M%S')
    logging.basicConfig(
        encoding='utf-8',
        level=logging.INFO,
        handlers=[
            logging.FileHandler(args.log_path.joinpath(f'{runtime}_{args.instrument}.log')),
            logging.StreamHandler()],
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(levelname)s : %(message)s')
    
    # log the parameters used
    _log_params(args)
    
    # identify directory changes between the paths
    try: directory_changes: dict = _identify_changes(args.input_path, args.destination_path)
    except:
        logging.critical("Critical error when trying to identify changes between directories!")
        quit()

    # copy files from the input to the destination
    if not args.check:
        try: _copy_to_drive(args.input_path, args.destination_path, directory_changes)
        except:
            logging.critical("Critical error when trying to performing backup!")
            quit()

    return None
# --------------------------------------------------
if __name__ == '__main__':
    main()
# z-drive-backup
A python script to facilitate the process of copying files to the Z-drive for archival.

## Table of contents
* [Requirements](#requirements)
* [Usage](#usage)
  * [1. Configure the config file](#1-configure-the-config-file)
  * [2. Running the script](#2-running-the-script)

## Requirements
* Python >= 3.10

This script was written in an environment with Python 3.10, but this script likely works with earlier and newer versions as well.
There are no third-party libraries required.


## Usage

### 1. Configure the config file
Before running the script, ensure that the config file is properly configured. A brief glance at the config file will show that it's essentially a json containing paths. Ensure that paths are properly set for each of the `instruments` and `log_output`.

Example:
```
"instruments": {
    "NGS": "#z-drive-mockup/raw-data/NGS"
    },
"log_output": "#z-drive-mockup/raw-data/"
```

### 2. Running the script
Again, make sure that the config file is properly configured! Afterwards, script usage is straight-forward:
```
backup.py --instrument <NAME> <input_path>
```

Assuming that the config file is properly configured, the script will accept a value from a list of valid instruments and paths (use `-h` to show them). The script will then walk through the input directory checking if the file exists in the destination directory with the following tree of logic:

* If file the does not exist, it is copied over.
* If file the file does exist, the modification time of the input file is compared with that of the destination file.
    * If they are different, this file is noted in the log, but otherwise not copied.
    * If they are the same, this file is probably already correctly archived.

The copying of every file is logged in terms of its success. Errors or warnings will be logged.

Logs will be output to the directory specified in the `config file`. In the event of a crash, the logfile will still be dumped. Check to see the success message at the bottom of the log file.
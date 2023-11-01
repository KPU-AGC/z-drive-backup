# z-drive-backup
A Powershell script to facilitate the process of copying files from local machines to the Z-drive for archival.

## Table of contents
* [Requirements](#requirements)
* [Usage](#usage)
  * [Directory structures](#directory-structures)
  * [Running the script](#1-running-the-script)

## Requirements
None. Powershell should come packaged in Windows.

## Usage
### Directory structures
When copying machines from local instruments to the Z-drive, especially using a USB drive, there are some particulars about directories to consider.
This script intends to copy directories containing sub-directories/files from local instruments. That is to say that a given directory should contain all files pertaining to a particular instrument that will be backed up. This directory containing sub-directories/files should also be named after the instrument from whence the files have originated.

> **Example:**
> 
> The USB should contain a directory named "SeqStudio". In that directory, there should be runs that will be backed up. Those runs will be backed up to the similarly-named Z-drive directory, "Raw-Data/SeqStudio".
> The intent is that all sub-directories and all files will be pathed correctly relative to these instrument-specific directories.
>
> `USB:/Seqstudio/{run files} -> Z:/Raw-Data/SeqStudio/{run files}`

Note: There is an option to ignore this structure. Copying between dissimilarly-named directories prompts the user for verification. Be mindful.

### 1. Running the script
Script usage is relatively easy.

  1. Navigate to the directory containing the backup script.
  
  2. Double-click the provided shortcut.
    Alternatively, run the script manually in Powershell using `.\z-drive-backup.ps1`.

  3. A prompt will appear for selecting a directory. Select the source instrument directory from where sub-directories/files will be copied.

  4. Another prompt will appear for selecting a directory. Select the destination instrument directory on the Z-drive to where sub-directories/files will be copied.
    **Note:** If at this point the source directory and destination directory are not identically named (see note above), a prompt will appear for verification of your choice.

  5. One more prompt should appear to perform backup or just check files. Selecting YES will perform a backup. Selecting NO will only check for files on the USB that are not already present on the Z-drive--this does not perform a backup.

**Note:** Files will not be overwritten. This is deliberate. If you have files that are modified after the fact, e.g., qPCR runs (`.eds`, `.edt`, etc.), those must be copied and overwritten manually.

Regardless of choice, logs will be saved in the specified logging directory for backups. Check to see the success message at the end of the log file.

## Changelog
* 1.0.0 (2023 November 01 ): Initial draft of document.
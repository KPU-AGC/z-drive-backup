<#
    Description: 
    This script is intended for backing up directories of raw data from instruments to the Z-drive.
    This implementation with dialog boxes and confirmation screens is intended to maximize accessibility and reduce potential error, especially
    those that are irrevocable.

    Author: Erick Samera
    Version: 1.0.0
    Comments: Stable enough
#>

# Imports
Add-Type -AssemblyName System.Windows.Forms

function SelectFolder($description) {
    <#
        .SYNOPSIS
            Function to select a folder using Windows FolderBrowserDialog box.

        .DESCRIPTION
            This function prompts users to select directories using native Windows dialog boxes.
            The purpose is to maximize accessibility over the previous method of command-line entry in Python.

        .PARAMETER description
            This parameter provides hopefully explicit instructions to the user.
        
        .EXAMPLE
            SelectFolder("Please select the SOURCE for backup. (FILES WILL BE COPIED FROM HERE)."
    #>

    $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
    $folderBrowser.Description = $description
    $result = $folderBrowser.ShowDialog()

    if ($result -eq "OK") {
        return $folderBrowser.SelectedPath
    } else {
        return $null
    }
}

$source = SelectFolder("Please select the SOURCE for backup. (FILES WILL BE COPIED FROM HERE).")
$destination = SelectFolder("Please select the DESTINATION for backup. (FILES WILL BE COPIED TO HERE).")

if ($null -eq $source -or $null -eq $destination) {
    Write-Output "Operation cancelled."
    exit
}

$sourceDirName = [System.IO.Path]::GetFileName($source)
$destinationDirName = [System.IO.Path]::GetFileName($destination)

<#
Check if the source and destination directory names match. This is especially to prevent writing to the wrong directory on the Z-drive where resolving conflicts may be difficult.
The intended usage of backup is that users will copy files in directories named after local machines to similarly named directories on the Z-drive for a given local machine.
Example:
Copy files from D:\SeqStudio {containing local files} -> Z:\Raw-Data\SeqStudio
#>
if ($sourceDirName -ne $destinationDirName) {
    $choice = [System.Windows.Forms.MessageBox]::Show("The source and destination directory names do not match. Are you sure you've selected the correct directories?", "Directory Mismatch", [System.Windows.Forms.MessageBoxButtons]::YesNo)
    
    if ($choice -eq "No") {
        Write-Output "Operation cancelled due to directory mismatch."
        exit
    }
}

$dateString = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$outputFile = "{Z-Drive-Log-Path}\${dateString}_$sourceDirName.txt"
# File transfers should be fully logged.
Start-Transcript -Path $outputFile -Append

<#
The intended purpose here is that users should be able to check for files on the local machine that are not present on the Z-drive especially prior to backing up.
To prevent accidental overwrite and as a safety-first measure, users should perform the check command.
#>
$choice = [System.Windows.Forms.MessageBox]::Show("Would you like to perform the backup? Click 'Yes' to backup or 'No' to just check missing files.", "Backup Choice", [System.Windows.Forms.MessageBoxButtons]::YesNo)
$performBackup = $choice -eq "Yes"

$sourceFiles = Get-ChildItem -Path $source -Recurse -File | ForEach-Object { $_.FullName.Replace($source, '') }
$destinationFiles = Get-ChildItem -Path $destination -Recurse -File | ForEach-Object { $_.FullName.Replace($destination, '') }

$sourceDirs = Get-ChildItem -Path $source -Recurse -Directory | ForEach-Object { $_.FullName.Replace($source, '') }
$destinationDirs = Get-ChildItem -Path $destination -Recurse -Directory | ForEach-Object { $_.FullName.Replace($destination, '') }

$missingFiles = $sourceFiles | Where-Object { $destinationFiles -notcontains $_ }
$missingDirs = $sourceDirs | Where-Object { $destinationDirs -notcontains $_ }

# Counters
$missingFileCount = 0
$missingDirCount = 0

$backedUpFileCount = 0
$backedUpDirCount = 0

if ($performBackup) {
    Write-Output "[$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")] Beginning backup of $sourceDirName to $destinationDirName !"
    } else {
    Write-Output "[$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")] Comparing $sourceDirName to $destinationDirName !"
}

foreach ($dir in $missingDirs) {
    $destinationPathDir = Join-Path -Path $destination -ChildPath $dir

    $missingDirCount++

    if ($performBackup) {
        Write-Output "[$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")] Backing up directory: $destinationPathDir ..."
        New-Item -ItemType Directory -Path $destinationPathDir | Out-Null
        $backedUpDirCount++
        Write-Output "[$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")] Backed up directory: $destinationPathDir ."
    } else {
        Write-Output "[$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")] Missing directory: $destinationPathDir ."
    }
}

foreach ($file in $missingFiles) {
    $sourcePath = Join-Path -Path $source -ChildPath $file
    $destinationPath = Join-Path -Path $destination -ChildPath $file

    $missingFileCount++
    if ($performBackup) {
        Write-Output "[$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")] Backing up: $sourcePath to $destinationPath ..."
        Copy-Item -Path $sourcePath -Destination $destinationPath
        $backedUpFileCount++
        Write-Output "[$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")] Backed up: $sourcePath to $destinationPath"
    } else {
        Write-Output "[$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")] Missing file: $sourcePath"
    }
}

if ($performBackup) {
    Write-Output "[$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")] Finished backup of $sourceDirName to $destinationDirName !"
    Write-Output ""
    Write-Output "Total dirs missing: $missingDirCount"
    Write-Output "Total files missing: $missingFileCount"
    Write-Output ""
    Write-Output "Total dirs backed up: $backedUpDirCount/$missingDirCount"
    Write-Output "Total files backed up: $backedUpFileCount/$missingFileCount"

    } else {
    Write-Output "[$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")] Finished comparing $sourceDirName to $destinationDirName !"
    Write-Output ""
    Write-Output "Total dirs missing: $missingDirCount"
    Write-Output "Total files missing: $missingFileCount"
}

Stop-Transcript
Read-Host "Press Enter to exit..."
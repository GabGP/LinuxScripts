# ezin (Easy Install) - Installation on Linux

**ezin** is an interactive Bash script designed to automate the installation of pre-compiled Linux software distributed as `.tar` or `.zip` archives.

## Features

* Supports `.zip`, `.tar`, `.tar.gz`, `.tar.xz`, and `.tar.bz2`.
* Archive "Bomb" Protection
* Intelligent `.desktop` File Management

## Requirements

This script relies on standard Linux utilities. On modern distributions (like Fedora, Ubuntu, or Arch), most of these are pre-installed. 

* **`file`**
* **`tar`**
* **`unzip`**
* **`sed`** (For text manipulation and fixing relative paths)
* **`desktop-file-utils`** (Provides the `update-desktop-database` command)

> **Fedora/RHEL Users:** If you are missing dependencies, install them via:
> `sudo dnf install file tar unzip sed desktop-file-utils`

## Usage

Make sure the script is executable before running it for the first time:
`chmod +x ezin.sh`

Pass where your downloaded archive is an argument. Otherwise, it will prompt you for the file path.

`sudo ./ezin.sh /home/user/Downloads/software-1.2.3.tar.xz`

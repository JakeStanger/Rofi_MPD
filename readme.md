# Rofi MPD

This is a simple MPD client for quickly adding albums or tracks using Rofi. 
It supports a variety of modes, and can group longer albums by disc number (or even disc name).

## Installation

Unsurprisingly, you will require both MPD and Rofi to be installed. You will also require Python >= 3.6.

### Python Package

You can install the [pypi](https://pypi.org/project/Rofi-MPD/) package using `pip3 install Rofi-MPD`. 

Make sure wherever it is installed to is on your path. You can check with `pip3 show Rofi-MPD`.

### Arch Linux

Arch users can install the [rofi-mpd-git](https://aur.archlinux.org/packages/rofi-mpd-git/) package.

### Ubuntu

Users of Ubuntu or its derivatives can add my PPA and install the package from there:

```bash
sudo add-apt-repository ppa:jakestanger/ppa
sudo apt-get update
sudo apt install python3-rofi-mpd
```

### Debian

A `.deb` can be downloaded from [the releases page](https://github.com/JakeStanger/Rofi_MPD/releases/latest).

### NixOS

I have a pull request currently open [here](https://github.com/NixOS/nixpkgs/pull/69877). 
For now you can grab the derivation from [here](https://github.com/NixOS/nixpkgs/blob/05a287a4269e3d7512d7122fa60fe67ca404f9a4/pkgs/applications/audio/rofi-mpd/default.nix)
and add it to an overlay.

### Other

Clone this repo somewhere, then run:

```bash
pip3 install -r requirements.txt
```

You may wish to use the provided script, in which case it needs to be marked as executable:

```bash
chmod +x bin/rofi-mpd
```

## Usage

If installed using a package manager, a script should have automatically been put on your path:

```bash
rofi-mpd # Normal usage
rofi-mpd -h # See help
```

If not, you can either do:
```bash
python3 rofi_mpd/rofi_mpd.py
# or
bin/rofi-mpd
```

By default, a list of artists is shown.

The program will take a second or so to load data from MPD. This data is cached for 10 minutes in the database file.

|  Short |  Long             | Description                                                 | Default                               |
|--------|-------------------|-------------------------------------------------------------|---------------------------------------|
| -h     | --help            | Shows CLI help and exits                                    |                                       |
| -b     | --albums          | Shows a list of all albums                                  |                                       |
|  -t    | --tracks          | Shows a list of tracks                                      |                                       |
| -a     | -all              |  Shows a mixture of all artists, albums and tracks          |                                       |
| -m     | --music-directory | Specifies the path to your music library                    | ~/Music                               |
| -c     | --host            | Specifies the MPD server host                               | localhost                             |
| -p     | --port            | Specifies the MPD server port                               | 6600                                  |
| -d     | --database        | Specifies the database file to read cached data from        | ~/.local/share/rofi-mpd/database.json |
| -i     | --case-sensitive  | Enables case sensitivity                                    | False                                 |
|  -r    | --args            | Space-separated command line arguments to be passed to Rofi | []                                    |
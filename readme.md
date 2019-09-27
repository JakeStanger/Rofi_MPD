# Rofi MPD
This is a very basic MPD client written in Python using Rofi. It allows you to add songs and nothing
else. I made it because I wanted to be able to quickly add songs and albums to MPD without fiddling
with ncmpcpp's awkward search.

By default your default Rofi theme is used. You can parse rofi command line arguments in.

You obviously require Rofi and MPD to be installed (and running in the case of MPD).

## Installation

### Python Package

You can install the [pypi](https://pypi.org/project/Rofi-MPD/) package using `pip3 install Rofi-MPD`. 

Make sure wherever it is installed to is on your path. You can check with `pip3 show Rofi-MPD`.

### Arch Linux

Arch users can install the [rofi-mpd-git](https://aur.archlinux.org/packages/rofi-mpd-git/) package.

### Ubuntu

Users of Ubuntu or Ubuntu derivatives can add my PPA and install the package from there:

```bash
sudo add-apt-repository ppa:jakestanger/ppa
sudo apt-get update
sudo apt install python3-rofi-mpd
```

A `.deb` can also be downloaded from the releases page.

### Other

Clone this repo somewhere.

## Usage
* If necessary change the line `client.connect('localhost', 6600)` to match your hostname and port.
* Install dependencies with `pip install -r requirements.txt`
* Run program with `python main.py`
* See help for the program with `python main.py -h`. Includes different modes for running
the program and settings.
* Probably add a keybinding to launch it for you so you can run it from anywhere.

## Modes
These are all the possible outcomes from each mode. Obviously adding a track will close the program; you will not have to go through any further menus.
* Regular: Artist -> Album -> Track -> Disc / Add -> Add
* -b Albums: Album -> Track -> Disc / Add -> Add
* -t Track: Track -> Disc / Add - > Add
* -a All: Artist + Album + Track -> Album / Track / Add -> Track / Add -> Disc / Add - > Add
* -c Host: Use the specified MPD host
* -p Port: Use the specified MPD port
* -d Database: Use the specified database

# Rofi MPD
This is a very basic MPD client written in Python using Rofi. It allows you to add songs and nothing
else. I made it because I wanted to be able to quickly add songs and albums to MPD without fiddling 
with ncmpcpp's awkward search.

By default your default Rofi theme is used. You can parse rofi command line arguments in.

## Usage
* Clone this repo somewhere.
* If necessary change the line `client.connect('localhost', 6600)` to match your hostname and port.
* Install dependencies with `pip install -r requirements.txt`
* Run program with `python main.py`
* See help for the program with `python main.py -h`. Includes different modes for running
the program and settings.
* Probably add a keybinding to launch it for you so you can run it from anywhere.

## Modes
These are all the possible outcomes from each mode. Obviously adding a track will close the program; you will not have to go through any further menus.
* Regular: Artist -> Album -> Track -> Disc / Add -> Add
* Albums: Album -> Track -> Disc / Add -> Add
* Track: Track -> Disc / Add - > Add
* All: Artist + Album + Track -> Album / Track / Add -> Track / Add -> Disc / Add - > Add

## Showcase
![Alt Text](https://files.jakestanger.com/projects/rofi-mpd2.gif)

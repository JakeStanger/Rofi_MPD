# Rofi MPD
This is a very basic MPD client written in Python using Rofi. It allows you to add songs and nothing
else. I made it because I wanted to be able to quickly add songs and albums to MPD without fiddling 
with ncmpcpp's awkward search.

This uses your default Rofi theme. It currently only supports

## Usage
* Clone this repo somewhere.
* If necessary change the line `client.connect('localhost', 6600)` to match your hostname and port.
* Install dependencies with `pip install -r requirements.txt`
* Run program with `python main.py`
* Probably add a keybinding to launch it for you so you can run it from anywhere.

![Alt Text](https://files.jakestanger.com/projects/rofi-mpd.gif)

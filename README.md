# Kaylee

Kaylee is a somewhat fancy speech recognizer that will run commands and perform
other functions when a user speaks loosely preset sentences.  It is based on
[Blather](https://gitlab.com/jezra/blather) by [Jezra](http://www.jezra.net/),
but adds a lot of features that go beyond the original purpose of Blather.

## Requirements

1. pocketsphinx
2. gstreamer-1.0 (and what ever plugin has pocketsphinx support)
3. gstreamer-1.0 base plugins (required for ALSA)
4. python-gobject (required for GStreamer and the GTK-based UI)

**Note:** it may also be required to install `pocketsphinx-hmm-en-hub4wsj`


## Usage

1. Move commands.tmp to ~/.config/kaylee/commands.conf and fill the file with
sentences and command to run
2. Run blather.py.  This will generate ~/.local/share/kaylee/sentences.corpus
based on sentences in the 'commands' file, then use
<http://www.speech.cs.cmu.edu/tools/lmtool.html> to create and save a new
language model and dictionary.
    * For GTK UI, run blather.py -i g
    * To start a UI in 'continuous' listen mode, use the -c flag
    * To use a microphone other than the system default, use the -m flag
3. Start talking

**Note:** to start Kaylee without needing to enter command line options all the
time, copy options.json.tmp to ~/.config/kaylee/options.json and edit
accordingly.

### Examples

* To run Kaylee with the GTK UI and start in continuous listen mode:
`./blather.py -i g -c`

* To run Kaylee with no UI and using a USB microphone recognized and device 2:
`./blather.py -m 2`

* To have Kaylee pass the matched sentence to the executed command:
`./blather.py -p`

**explanation:** if the commands.conf contains:
`good morning world: example_command.sh`
then 3 arguments, 'good', 'morning', and 'world' would get passed to
example_command.sh as `example_command.sh good morning world`

* To run a command when a valid sentence has been detected:
	`./blather.py --valid-sentence-command=/path/to/command`
	**note:** this can be set in the options.yml file
* To run a command when a invalid sentence has been detected:
	`./blather.py --invalid-sentence-command=/path/to/command`
	**note:** this can be set in the options.yml file

### Finding the Device Number of a USB microphone
There are a few ways to find the device number of a USB microphone.

* `cat /proc/asound/cards`
* `arecord -l`

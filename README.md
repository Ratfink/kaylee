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
5. python-requests (required for automatic language updating)

**Note:** it may also be required to install `pocketsphinx-hmm-en-hub4wsj`


## Usage

1. Move options.json.tmp to ~/.config/kaylee/options.json and fill the
   "commands" section of the file with sentences to speak and commands to run.
2. Run kaylee.py.  This will generate ~/.local/share/kaylee/sentences.corpus
   based on sentences in the "commands" section of options.json, then use the
   [Sphinx Knowledge Base Tool](http://www.speech.cs.cmu.edu/tools/lmtool.html)
   to create and save a new language model and dictionary.
    * For GTK UI, run kaylee.py -i g
    * To start a UI in 'continuous' listen mode, use the -c flag
    * To use a microphone other than the system default, use the -m flag
3. Start talking!

**Note:** default values for command-line arguments may be specified in the
options.json file.

### Examples

* To run Kaylee with the GTK UI, starting in continuous listen mode:
  `./kaylee.py -i g -c`

* To run Kaylee with no UI and using a USB microphone recognized as device 2:
  `./kaylee.py -m 2`

* To have Kaylee pass each word of the matched sentence as a separate argument
  to the executed command: `./kaylee.py -p`

* To run a command when a valid sentence has been detected:
  `./kaylee.py --valid-sentence-command=/path/to/command`

* To run a command when a invalid sentence has been detected:
  `./kaylee.py --invalid-sentence-command=/path/to/command`

### Finding the Device Number of a USB microphone
There are a few ways to find the device number of a USB microphone.

* `cat /proc/asound/cards`
* `arecord -l`

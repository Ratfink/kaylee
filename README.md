# Kaylee

Kaylee is a somewhat fancy speech recognizer that will run commands and perform
other functions when a user speaks loosely preset sentences.  It is based on
[Blather](https://gitlab.com/jezra/blather) by [Jezra](http://www.jezra.net/),
but adds a lot of features that go beyond the original purpose of Blather.

## Requirements

1. pocketsphinx
2. gstreamer-1.0 (and what ever plugin has pocket sphinx support)
3. gstreamer-1.0 base plugins (required for alsa)
5. pygtk (only required for the Gtk based UI)
6. pyyaml (only required for reading the options file)

**Note:** it may also be required to install `pocketsphinx-hmm-en-hub4wsj`


## Usage

1. Move commands.tmp to ~/.config/blather/commands.conf and fill the file with
sentences and command to run
2. Run blather.py, this will generate ~/.config/blather/sentences.corpus based
on sentences in the 'commands' file
3. Quit Kaylee (there is a good chance it will just segfault)
4. Go to <http://www.speech.cs.cmu.edu/tools/lmtool.html> and upload the
sentences.corpus file
5. Download the resulting XXXX.lm file to the ~/.config/blather/language
directory and rename to file to 'lm'
6. Download the resulting XXXX.dic file to the ~/.config/blather/language
directory and rename to file to 'dic'
7. Run blather.py
    * For GTK UI, run blather.py -i g
    * To start a UI in 'continuous' listen mode, use the -c flag
    * To use a microphone other than the system default, use the -m flag
8. Start talking

**Note:** to start Kaylee without needing to enter command line options all the
time, copy options.yaml.tmp to ~/.config/blather/options.yaml and edit
accordingly.

### Bonus

~~Once the sentences.corpus file has been created, run the language_updater.sh
script to automate the process of creating and downloading language files.~~

Kaylee now updates the language automatically.  You should never need to run
language_updater.sh manually.

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

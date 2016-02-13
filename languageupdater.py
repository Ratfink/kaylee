# This is part of Kaylee
# -- this code is licensed GPLv3
# Copyright 2015-2016 Clayton G. Hobbs
# Portions Copyright 2013 Jezra

import re

import requests

from hasher import Hasher

class LanguageUpdater:

    def __init__(self, config):
        self.config = config
        self.hasher = Hasher(config)

    def update_language_if_changed(self):
        """Test if the language has changed, and if it has, update it"""
        if self.language_has_changed():
            self.update_language()
            self.save_language_hash()

    def language_has_changed(self):
        """Use hashes to test if the language has changed"""
        self.stored_hash = self.hasher['language']

        # Calculate the hash the language file has right now
        hasher = self.hasher.get_hash_object()
        with open(self.config.strings_file, 'rb') as sfile:
            buf = sfile.read()
            hasher.update(buf)
        self.new_hash = hasher.hexdigest()

        return self.new_hash != self.stored_hash

    def update_language(self):
        """Update the language using the online lmtool"""
        print('Updating language using online lmtool')

        host = 'http://www.speech.cs.cmu.edu'
        url = host + '/cgi-bin/tools/lmtool/run'

        # Submit the corpus to the lmtool
        response_text = ""
        with open(self.config.strings_file, 'rb') as corpus:
            files = {'corpus': corpus}
            values = {'formtype': 'simple'}

            r = requests.post(url, files=files, data=values)
            response_text = r.text

        # Parse response to get URLs of the files we need
        path_re = r'.*<title>Index of (.*?)</title>.*'
        number_re = r'.*TAR([0-9]*?)\.tgz.*'
        for line in response_text.split('\n'):
            # If we found the directory, keep it and don't break
            if re.search(path_re, line):
                path = host + re.sub(path_re, r'\1', line)
            # If we found the number, keep it and break
            elif re.search(number_re, line):
                number = re.sub(number_re, r'\1', line)
                break

        lm_url = path + '/' + number + '.lm'
        dic_url = path + '/' + number + '.dic'

        self._download_file(lm_url, self.config.lang_file)
        self._download_file(dic_url, self.config.dic_file)

    def save_language_hash(self):
        self.hasher['language'] = self.new_hash
        self.hasher.store()

    def _download_file(self, url, path):
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)

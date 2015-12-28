# This is part of Kaylee
# -- this code is licensed GPLv3
# Copyright 2013 Jezra
# Copyright 2015 Clayton G. Hobbs

import hashlib
import json
import re

import requests

class LanguageUpdater:

    def __init__(self, config):
        self.config = config

    def update_language_if_changed(self):
        """Test if the language has changed, and if it has, update it"""
        if self.language_has_changed():
            self.update_language()
            self.save_language_hash()

    def language_has_changed(self):
        """Use SHA256 hashes to test if the language has changed"""
        # Load the stored hash from the hash file
        try:
            with open(self.config.hash_file, 'r') as f:
                hashes = json.load(f)
            self.stored_hash = hashes['language']
        except (IOError, KeyError, TypeError):
            # No stored hash
            self.stored_hash = ''

        # Calculate the hash the language file has right now
        hasher = hashlib.sha256()
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

        # Prepare request
        files = {'corpus': open(self.config.strings_file, 'rb')}
        values = {'formtype': 'simple'}

        # Send corpus to the server
        r = requests.post(url, files=files, data=values)

        # Parse response to get URLs of the files we need
        path_re = r'.*<title>Index of (.*?)</title>.*'
        number_re = r'.*TAR[0-9]*?\.tgz.*'
        for line in r.text.split('\n'):
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
        new_hashes = {'language': self.new_hash}
        with open(self.config.hash_file, 'w') as f:
            json.dump(new_hashes, f)

    def _download_file(self, url, path):
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)

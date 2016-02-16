#!/usr/bin/env python
# This is part of Kaylee
# -- this code is licensed GPLv3
# Copyright 2015-2016 Clayton G. Hobbs
# Portions Copyright 2013 Jezra

import re

# Define the mappings from words to numbers
class NumberParser:
    zero = {
        'zero': 0
    }

    ones = {
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9
    }

    special_ones = {
        'ten': 10,
        'eleven': 11,
        'twelve': 12,
        'thirteen': 13,
        'fourteen': 14,
        'fifteen': 15,
        'sixteen': 16,
        'seventeen': 17,
        'eighteen': 18,
        'ninteen': 19
    }

    tens = {
        'twenty': 20,
        'thirty': 30,
        'fourty': 40,
        'fifty': 50,
        'sixty': 60,
        'seventy': 70,
        'eighty': 80,
        'ninty': 90
    }

    hundred = {
        'hundred': 100
    }

    exp = {
        'thousand': 1000,
        'million': 1000000,
        'billion': 1000000000
    }

    allowed = [
        'and'
    ]

    def __init__(self):
        self.number_words = []
        for word in sorted(self.zero.keys()):
            self.number_words.append(word)
        for word in sorted(self.ones.keys()):
            self.number_words.append(word)
        for word in sorted(self.special_ones.keys()):
            self.number_words.append(word)
        for word in sorted(self.tens.keys()):
            self.number_words.append(word)
        for word in sorted(self.hundred.keys()):
            self.number_words.append(word)
        for word in sorted(self.exp.keys()):
            self.number_words.append(word)
        self.mandatory_number_words = self.number_words.copy()
        for word in sorted(self.allowed):
            self.number_words.append(word)

    def parse_number(self, text_line):
        """
        Parse numbers from natural language into ints

        TODO: Throw more exceptions when invalid numbers are detected.  Only
        allow certian valueless words within numbers.  Support zero.
        """
        value = 0
        partial_value = 0
        last_list = None

        # Split text_line by commas, whitespace, and hyphens
        text_line = text_line.strip()
        text_words = re.split(r'[,\s-]+', text_line)
        # Parse the number
        for word in text_words:
            if word in self.zero:
                if last_list is not None:
                    raise ValueError('Invalid number')
                value = 0
                last_list = self.zero
            elif word in self.ones:
                if last_list in (self.zero, self.ones, self.special_ones):
                    raise ValueError('Invalid number')
                value += self.ones[word]
                last_list = self.ones
            elif word in self.special_ones:
                if last_list in (self.zero, self.ones, self.special_ones, self.tens):
                    raise ValueError('Invalid number')
                value += self.special_ones[word]
                last_list = self.special_ones
            elif word in self.tens:
                if last_list in (self.zero, self.ones, self.special_ones, self.tens):
                    raise ValueError('Invalid number')
                value += self.tens[word]
                last_list = self.tens
            elif word in self.hundred:
                if last_list not in (self.ones, self.special_ones, self.tens):
                    raise ValueError('Invalid number')
                value *= self.hundred[word]
                last_list = self.hundred
            elif word in self.exp:
                if last_list in (self.zero, self.exp):
                    raise ValueError('Invalid number')
                partial_value += value * self.exp[word]
                value = 0
                last_list = self.exp
            elif word not in self.allowed:
                raise ValueError('Invalid number')
            # Debugging information
            #print(word, value, partial_value)
        # Finish parsing the number
        value += partial_value
        return value

    def parse_all_numbers(self, text_line):
        nums = []
        t_numless = ''

        # Split text_line by commas, whitespace, and hyphens
        text_words = re.split(r'[,\s-]+', text_line.strip())
        # Get a string of word classes
        tw_classes = ''
        for word in text_words:
            if word in self.mandatory_number_words:
                tw_classes += 'm'
            elif word in self.allowed:
                tw_classes += 'a'
            else:
                tw_classes += 'w'

        # For each string of number words:
        last_end = 0
        for m in re.finditer('m[am]*m|m', tw_classes):
            # Get the number words
            num_words = ' '.join(text_words[m.start():m.end()])
            # Parse the number and store the value
            try:
                nums.append(self.parse_number(num_words))
            except ValueError:
                nums.append(-1)
            # Add words to t_numless
            t_numless += ' '.join(text_words[last_end:m.start()]) + ' %d '
            last_end = m.end()
        t_numless += ' '.join(text_words[last_end:])

        return (t_numless.strip(), nums)

if __name__ == '__main__':
    np = NumberParser()
    # Get the words to translate
    text_line = input('Enter a string: ')
    # Parse it to an integer
    value = np.parse_all_numbers(text_line)
    # Print the result
    print(value)

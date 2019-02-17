# SOURCE: https://www.kaggle.com/reppic/predicting-english-pronunciations

import os
import random

LIMIT_DICT = True

DICT_PATH = os.path.join('data/', 'cmudict-0.7b.txt')

# Setting min and max word length to simplify data set
MAX_WORD_LEN = 15
MIN_WORD_LEN = 2


def load_clean_phonetic_dictionary():

    def is_alt_spelling(word):
        # Alternate words appear as "Alternate(1)"
        # This checks if words has "(?)" at the end
        return word[-1] == ')'and word[-2].isdigit() and word[-3] == '('

    def should_skip(word):
        # skip words with characters not in the following set
        if not word.isalpha():
            return True
        if len(word) > MAX_WORD_LEN:
            return True
        if len(word) < MIN_WORD_LEN:
            return True
        return False

    phonetic_dict = {}
    with open(DICT_PATH, "r") as cmu_dict:
        for line in cmu_dict:

            # Skip commented lines
            if line[0:3] == ';;;':
                continue

            data = line.strip().split('  ')
            word = data[0]

            # Remove the "(?)" from alternate pronuncations
            # Skipping for now alternates for now!
            # not sure what to do with them
            if is_alt_spelling(word):
                #word = word[:-3]
                continue

            if should_skip(word):
                continue

            phonemes = []
            for phoneme in data[1].split():
                if phoneme[-1].isdigit():
                    phonemes.append(phoneme[:-1])
                else:
                    phonemes.append(phoneme)

            # This allows for multiple pronunciations
            # (i.e. each word has a list of pronuncations)
            # if word not in phonetic_dict:
            #     phonetic_dict[word] = []
            # phonetic_dict[word].append(phonemes)

            # This works for dict with NO alternate pronuncations
            phonetic_dict[word] = phonemes

    if LIMIT_DICT: # limit dataset to X number of words
        phonetic_dict = {key:phonetic_dict[key]
                         for key in random.sample(list(phonetic_dict.keys()), 50)}
    return phonetic_dict

# phonetic_dict = load_clean_phonetic_dictionary()
# for key in phonetic_dict:
#    print(key, phonetic_dict[key])

# SOURCE: https://www.kaggle.com/reppic/predicting-english-pronunciations

import os
import random

LIMIT_DICT = True

DICT_PATH = os.path.join('data/', 'cmudict-0.7b.txt')

arpabet_dictionary = {
'AA': 'a',
'AE': '@',
'AH': 'A',
'AO': 'c',
'AW': 'W',
'AY': 'Y',
'B': 'b',
'CH': 'C',
'D': 'd',
'DH': 'D',
'EH': 'E',
'ER': 'R',
'EY': 'e',
'F': 'f',
'G': 'g',
'HH': 'h',
'IH': 'I',
'IY': 'i',
'JH': 'J',
'K': 'k',
'L': 'l',
'M': 'm',
'N': 'n',
'NG': 'G',
'OW': 'o',
'OY': 'O',
'P': 'p',
'R': 'r',
'S': 's',
'SH': 'S',
'T': 't',
'TH': 'T',
'UH': 'U',
'UW': 'u',
'V': 'v',
'W': 'w',
'Y': 'y',
'Z': 'z',
'ZH': 'Z'
}

def is_alt_spelling(word):
    # Alternate words appear as "Alternate(1)"
    # This checks if words has "(?)" at the end
    return word[-1] == ')'and word[-2].isdigit() and word[-3] == '('

def should_skip(word,alpha, min, max):
    # skip words with symbols not in english alphabet
    if not word.isalpha():
        return True
    if len(word) > max:
        return True
    if len(word) < min:
        return True
    # skip words with characters not in set alpha
    for letter in word:
        if letter.lower() not in alpha:
            return True
    return False

# Function takes a set of excepted characters in alphabet: alpha
# integer, size which is the number of words loading into phonetic dictionary
# integers min and max which are the min and max word length to be loaded into dictionary
def load_clean_phonetic_dictionary(alpha, min, max, size = False):
    # Setting min and max word length to simplify data set

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

            if should_skip(word, alpha, min, max):
                continue

            phonemes = ""
            for phoneme in data[1].split():
                if phoneme[-1].isdigit():
                    phonemes += (arpabet_dictionary[phoneme[:-1]])
                else:
                    phonemes += (arpabet_dictionary[phoneme])

            # This allows for multiple pronunciations
            # (i.e. each word has a list of pronuncations)
            # if word not in phonetic_dict:
            #     phonetic_dict[word] = []
            # phonetic_dict[word].append(phonemes)

            # This works for dict with NO alternate pronuncations
            phonetic_dict[word] = phonemes

    if size: # limit dataset to X number of words
        phonetic_dict = {key:phonetic_dict[key]
                         for key in random.sample(list(phonetic_dict.keys()), size)}
    return phonetic_dict

# phonetic_dict = load_clean_phonetic_dictionary()
# for key in phonetic_dict:
#    print(key, phonetic_dict[key])

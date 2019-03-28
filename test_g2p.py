import clean_data
import ISL_G2P

# ************ Test Helper Functions *************

# goal_out is expected string of 2-letter ARPAbet phonemse
# real_out is list of actual ourput with potential tuples representing semi-determinism
def is_possible_output(goal_out, real_out):
    return goal_out in find_all_possible_outs(real_out)

def find_all_possible_outs(output):
    list_of_possible_outs = []
    for x in output:
        if type(x) == tuple:
            for word in list_of_possible_outs:
                for y in x:
                    if y != '':
                        list_of_possible_outs = list_of_possible_outs + [word+y]
                if '' not in x:
                    list_of_possible_outs.remove(word)

            if len(list_of_possible_outs) == 0:
                for y in x:
                    list_of_possible_outs.append(y)

        else:
            for word in list_of_possible_outs:
                if x != '':
                    list_of_possible_outs = list_of_possible_outs + [word+x]
                    list_of_possible_outs.remove(word)
            if len(list_of_possible_outs) == 0:
                list_of_possible_outs.append(x)
    return list_of_possible_outs

# **************Test case 1: LD sibilant harmony, progressive, asymmetric (2-TSL)**************

# Sad Sas Test
#data = set([('a','a'),('s','s'),('S','S'),('sa', 'sa'), ('sS', 'ss'), ('ss', 'ss'), ('as', 'as'), ('aa', 'aa'), ('aS', 'aS'), ('Sa', 'Sa'), ('Ss', 'Ss'), ('SS', 'SS'), ('sas', 'sas'), ('saa', 'saa'), ('saS', 'sas'), ('sSs', 'sss'), ('sSS', 'sss'), ('sSa', 'ssa'), ('sss', 'sss'), ('ssS', 'sss'), ('ssa', 'ssa'), ('ass', 'ass'), ('asS', 'ass'), ('asa', 'asa'), ('aas', 'aas'), ('aaS', 'aaS'), ('aaa', 'aaa'), ('aSs', 'aSs'), ('aSS', 'aSS'), ('aSa', 'aSa'), ('Sas', 'Sas'), ('SaS', 'SaS'), ('Saa', 'Saa'), ('Sss', 'Sss'), ('SsS', 'Sss'), ('Ssa', 'Ssa'), ('SSs', 'SSs'), ('SSS', 'SSS'), ('SSa', 'SSa')])

# ISL Sas Test
#data = set([('a','a'),('s','s'),('S','S'),('sa', 'sa'), ('sS', 'ss'), ('ss', 'ss'), ('as', 'as'), ('aa', 'aa'), ('aS', 'aS'), ('Sa', 'Sa'), ('Ss', 'SS'), ('SS', 'SS'), ('sas', 'sas'), ('saa', 'saa'), ('saS', 'sas'), ('sSs', 'sss'), ('sSS', 'sss'), ('sSa', 'ssa'), ('sss', 'sss'), ('ssS', 'sss'), ('ssa', 'ssa'), ('ass', 'ass'), ('asS', 'ass'), ('asa', 'asa'), ('aas', 'aas'), ('aaS', 'aaS'), ('aaa', 'aaa'), ('aSs', 'aSS'), ('aSS', 'aSS'), ('aSa', 'aSa'), ('Sas', 'SaS'), ('SaS', 'SaS'), ('Saa', 'Saa'), ('Sss', 'SSS'), ('SsS', 'SSS'), ('Ssa', 'SSa'), ('SSs', 'SSS'), ('SSS', 'SSS'), ('SSa', 'SSa')])

# alpha = ['s','S','a']

# Nasal Vowel Test

# data = set([("VNC", "VNC"), ("CVN", "CVN"), ("CNC", "CNC"), ("NNC", "NNC"), ("NNV", "NNN"), ("VNN", "VNN"), ("NVN", "NNN"), ("VCN", "VCN"),
# ("CCV", "CCV"), ("CN", "CN"), ("VVC", "VVC"), ("NVC", "NNC"), ("CC", "CC"), ("NV", "NN"), ("NC", "NC"), ("VNV", "VNN"), ("VCV", "VCV"),
# ("CCN", "CCN"), ("N", "N"), ("CNV", "CNN"), ("NN", "NN"), ("C", "C"), ("NCC", "NCC"), ("CV", "CV"), ("CNN", "CNN"), ("VN", "VN"),
# ("VVN", "VVN"), ("VC", "VC"), ("NCV", "NCV"), ("CVC", "CVC"), ("VV", "VV"), ("VCC", "VCC"), ("NCN", "NCN"), ("V", "V"), ("NVV", "NNN"),
# ("CVV", "CVV"), ("CCC", "CCC"), ("VVV", "VVV"), ("NNN", "NNN")])

# alpha = ['C','N','C']

# G2P Test
alpha = map(chr, range(97, 123))
size = 1000
word_min = 2
word_max = 12
phonetic_dict = clean_data.load_clean_phonetic_dictionary(alpha, word_min, word_max, size)
CMU_data = set([(key.lower(), phonetic_dict[key])for key in phonetic_dict])

#data = set([('c','K'),('t','T'),('a','A'),('tt','TT'),('aa','aA'),('ca','KA'),('ac','AK'),('ta','TU'),('at','AT'),('ct','KT'),('tc','TK')])

k = 4

test1 = ISL_G2P.PTT(CMU_data,set(alpha))

# target = open('graphs/ptt.dot','w')
# target.write(ISL_G2P.print_FST(test1))

test1.onward('','')

# target = open('graphs/onward.dot','w')
# target.write(ISL_G2P.print_FST(test1))

ISL_G2P.ISLFLAv2(test1,k)

# target = open('graphs/isfla.dot','w')
# target.write(ISL_G2P.print_FST(test1))



inputs = set([x[0] for x in CMU_data])
test_passed = True
for word in inputs:
    output = test1.transduce(word)
    goal_out = phonetic_dict[word.upper()]
    if not is_possible_output(goal_out, output):
        print ":("
        print goal_out, word
        print output
        print find_all_possible_outs(output)
        test_passed = False

if test_passed:
    print 'test 1 passed!'
    print len(inputs)
    print inputs

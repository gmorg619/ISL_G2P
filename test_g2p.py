import clean_data
import error_handler
import ISL_G2P

# ************ Test Helper Functions *************

# goal_out is expected string of 2-letter ARPAbet phonemse
# real_out is list of actual ourput with potential tuples representing semi-determinism
def is_possible_output(goal_out, real_out):
    return goal_out in find_all_possible_outs(real_out)

# output is a list representing a semideterministic strings
# returns solution set for all possible strings derived from our list
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

# Returns true if s1 is a subsequence of s2. m is
# length of s1 and n is length of s2
def is_sub_seq(s1, s2, m, n):
    # Base Cases
    if m == 0:
        return True
    if n == 0:
        return False

    # If last characters of two strings are matching
    if s1[m-1] == s2[n-1]:
        return is_sub_seq(s1, s2, m-1, n-1)

    # If last characters are not matching
    return is_sub_seq(s1, s2, m, n-1)

# Returns true if s is a subsequence of and string in solution set of l.
def subseq_check(s, l):
    for x in find_all_possible_outs(l):
        if is_sub_seq(s, x, len(s), len(x)):
            return True
        if is_sub_seq(x, s, len(x), len(s)):
            return True
    return False

# G2P Test
alpha = map(chr, range(97, 123))
size  = 500
word_min = 1
word_max = 5
singleton_dict = clean_data.load_clean_phonetic_dictionary(alpha, 2,2, True)
new_dict = {}
for key in singleton_dict.keys():
    if key[0] not in new_dict.keys():
        new_dict[key[0]] = singleton_dict[key][0]

phonetic_dict = clean_data.load_clean_phonetic_dictionary(alpha, word_min, word_max)
print len(phonetic_dict)

phonetic_dict.update(new_dict)
CMU_data = set([(key.lower(), phonetic_dict[key])for key in phonetic_dict])

k = 4

test1 = ISL_G2P.PTT(CMU_data,set(alpha))

test1.onward('','')

ISL_G2P.ISLFLAv2(test1,k)


new_words  = clean_data.load_clean_phonetic_dictionary(alpha, 5, 12, False, 50)
novel_data = set([(key.lower(), new_words[key])for key in new_words])

session_errors = error_handler.ErrorHandler()
words_correct  = 0
subsequences   = 0
inputs_so_far  = len(novel_data)


while inputs_so_far != 1000:

    set_errors  = error_handler.ErrorHandler()
    set_correct = 0
    set_seqs = 0

    inputs = set([x[0] for x in novel_data])
    for word in inputs:
        out_set  = test1.transduce(word)
        goal_out = new_words[word.upper()]
        if not is_possible_output(goal_out, out_set):
            min_wer = 100
            min_out = ""
            for out in find_all_possible_outs(out_set):
                out_wer = error_handler.ErrorHandler()
                out_wer.calculate_errors(out, goal_out)
                out_wer = out_wer.get_wer()
                if out_wer < min:
                    min_wer = out_wer
                    min_out = out
            min_out_error = error_handler.ErrorHandler()
            min_out_error.calculate_errors(min_out, goal_out)
            # print min_out, goal_out
            # min_out_error.error_report()
            set_errors.calculate_errors(min_out, goal_out)
            session_errors.calculate_errors(min_out, goal_out)
            if subseq_check(goal_out, out_set):
                #print "but its a subsquence!"
                subsequences +=1
                set_seqs += 1


        else:
            set_errors.add_ref_num(goal_out)
            session_errors.add_ref_num(goal_out)
            words_correct += 1
            print "{}: Passed!".format(word)

    set_errors.error_report()
    print "{} word correct out of {} possible words".format(set_correct, 50)
    print "{} subsequences correct out of {} possible words".format(set_seqs, 50)
    #input = raw_input("Press enter to run test of 20 words ")
    new_words  = clean_data.load_clean_phonetic_dictionary(alpha, 6, 12, False, 50)
    novel_data = set([(key.lower(), new_words[key])for key in new_words])
    inputs_so_far +=50

session_errors.error_report()
print "{} word correct out of {} possible words".format(words_correct, inputs_so_far)
print "{} subsequences correct out of {} possible words".format(subsequences, inputs_so_far)

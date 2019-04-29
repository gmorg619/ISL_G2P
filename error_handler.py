#
#   Two Classes to Deal with Word Error rate
#       1. Error_Handler (handles the errors for a session)
#       2. Error (Handles the errors for one utterance)
#

class ErrorHandler:

    def __init__(self):
        self.reference_num = 0
        self.omitted = 0
        self.inserted = 0
        self.substituted = 0
        self.wer = 0

    def calculate_errors(self, hyp_str, reference):
        debug = False
        ref_list = list(reference)
        self.reference_num += len(ref_list)
        n = len(ref_list)
        hyp_list = list(hyp_str)
        h_n = len(hyp_list)
        #print ref_list, hyp_list

        i = 0
        while i < n and i < h_n:
            if ref_list[i] != hyp_list[i]:
                if i != n-1:
                    if hyp_list[i] == ref_list[i+1]:
                        if debug: print("Word \"%s\" was omitted" % ref_list[i])
                        self.omitted += 1
                        hyp_list.insert(i-1,"")
                        h_n = len(hyp_list)
                    elif i != h_n-1:
                        if hyp_list[i+1] == ref_list[i]:
                            if debug: print("Word \"%s\" was inserted" % hyp_list[i])
                            self.inserted +=1
                            del hyp_list[i]
                            h_n = len(hyp_list)
                        else:
                            self.substituted +=1
                            if debug: print("Word \"%s\" was substituted for \"%s\"" % (hyp_list[i], ref_list[i]))
                elif i != h_n-1:
                        if hyp_list[i+1] == ref_list[i]:
                            if debug: print("Word \"%s\" was inserted" % hyp_list[i])
                            self.inserted +=1
                            del hyp_list[i]
                            h_n = len(hyp_list)
                        else:
                            self.substituted +=1
                            if debug: print("Word \"%s\" was substituted for \"%s\"" % (hyp_list[i], ref_list[i]))
                else:
                    self.substituted +=1
                    if debug: print("Word \"%s\" was substituted for \"%s\"" % (hyp_list[i], ref_list[i]))
            i+=1
        if h_n > n:
            self.inserted += (h_n - n)
        elif h_n < n:
            self.omitted += (n - h_n)

    def add_ref_num(self, hyp):
        self.reference_num += len(hyp)

    def get_total_errors(self):
        return self.omitted + self.inserted + self.substituted

    def get_wer(self):
        self.wer = (self.get_total_errors()) / float(self.reference_num)
        return self.wer

    def error_report(self):
        print("Out of %d words. There were:" % self.reference_num)
        print("%d: Omitted Words" % self.omitted)
        print("%d: Inserted Words" % self.inserted)
        print("%d: Substituted Words" % self.substituted)
        print("For a total of %d errors out of %d words." % (self.get_total_errors(),self.reference_num))
        print("And a %f: Word Error Rate" % self.get_wer())

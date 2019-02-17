# Output Tier-based  Strictly Local Function Learning Algorithm
# Jane Chandlee
# Last updated: 16 July 2018

import copy
import itertools
from operator import itemgetter

# ***********Function for printing a FST in .dot format**************

def print_FST (f):
   fst = "digraph G { rankdir = LR "
   statelist = list(f.states.keys())

   for i in range(len(statelist)):
      if statelist[i] == '':
         fst += (str(i)+"[label=\"&#955;\"]")
      elif statelist[i][-1] == '#':
         fst += (str(i)+"[label=\"\",style=invis]")
      else:
         fst += (str(i)+"[label=\"" + str(statelist[i]) + "\"]")

   for q in f.transitions:
      for t in f.transitions[q]:
         fst += str(statelist.index(q)) + "->"+ str(statelist.index(t[2]))+ "[label = \"" + str(t[0]) + ":"
         if t[1] == '':
            fst += "&#955;\"]"
         else:
            fst += (str(t[1]) + "\"]")

   return (fst+"}")

# **************Auxiliary functions**************

# returns the set of prefixes for string w
def get_prefixes(w):
   return set([w[0:i] for i in range(len(w)+1)])

# returns the longest common prefix for a set of strings S
def lcp (S):
   if len(S) == 0:
      return ''
   common_prefs = set()
   common_prefs.update(get_prefixes(S.pop()))
   for w in S:
      common_prefs.intersection_update(get_prefixes(w))
   return max(common_prefs,key=len)

# returns the suffix of length n of a string
def suffix(s, k):
   if len(s) < k:
      return s
   else:
      return s[-k:]

# **************Prefix Tree Transducer (PTT) class**************

# PTT objects are initialized with the learner's input data (i.e., a set of input-output string pairs) and the alphabet (set).
# The attributes are:
# 1) STATES: a dictionary in which the keys are states and the value of a state is the set of states it has an incoming transition from.
# 2) TRANSITIONS: another dictionary with the states as keys and the values are tuples like (a,x,q') where a is the input symbol, x is the output string, and q' is the
# destination state.

class PTT:
   def __init__(self, data, alphabet):
      self.Sigma = alphabet.union(set(['#']))
      self.states, self.transitions = self.buildPTT(data)

   # Overloaded str method so you can call print on PTT objects
   def __str__(self):
      statelist = sorted(list(self.states))
      for s in statelist:
         print s
         if s in self.transitions:
            for t in self.transitions[s]:
               print '('+s+','+t[0]+') -> ('+t[1]+','+t[2]+')'
         print '\n'
      return ''

   def buildPTT(self,data):
      states = {('',''):set()}
      transitions = {('',''):set()}

      for iopair in data:

         prefs = get_prefixes(iopair[0]+'#').difference(set(['']))

         for p in prefs:

            if (p,'') not in states:
               states[(p,'')] = set([(p[:-1],'')])
            if (p,'') not in transitions:
               transitions[(p,'')] = set()

            if (p[:-1],'') not in transitions:
               if p[-1] == '#':
                  transitions[(p[:-1],'')] = set([('#',iopair[1],(p,''))])
               else:
                  transitions[(p[:-1],'')] = set([(p[-1],'',(p,''))])
            else:
               if p[-1] == '#':
                  transitions[(p[:-1],'')].add(('#',iopair[1],(p,'')))
               else:
                  transitions[(p[:-1],'')].add((p[-1],'',(p,'')))

      return states,transitions


   def get_trans(self,q,a):
      for t in self.transitions[q]:
         if t[0] == a:
            return (t[1],t[2])
      return (None,None)

   def transduce(self,s):
      output = ''
      state = ''
      for c in s:
         out,state = self.get_trans(state,c)
         output+=out
      return output

   def transduce_set(self,S):
      outputs = set()
      for s in S:
         outputs.add((s,self.transduce(s)))
      return outputs

   # recursive function, initially called with the initial state and the empty string (follows algorithm in de la Higuera (2010))
   # Note: this function doesn't seem to work properly when there is only one outgoing transition from the start state. Not sure why.
   def onward(self,q,u):

      for a in self.Sigma:
         out,dest = self.get_trans(q,a)
         if out != None:
            forward = self.onward(dest,a)
            self.transitions[q].remove((a,out,dest))
            self.transitions[q].add((a,out+forward[1],dest))

      outgoing_outputs = set([trans[1] for trans in self.transitions[q]])
      f = lcp(outgoing_outputs)
      if f:
         for a in self.Sigma:
            out,dest = self.get_trans(q,a)
            if out != None:
               self.transitions[q].remove((a,out,dest))
               self.transitions[q].add((a,out[len(f):],dest))

      return (q,f)

   def semideterministic(self,q):
      for t in self.transitions[q]:
         if type(t[1]) == tuple:
            return True
      return False

   def relabel(self):
      states = sorted(self.states.keys(),key=lambda x: len(x[0]))
      for q in states:
          if q != ('',''):
             origin = self.states[q].pop()
             for t in self.transitions[origin]:
                if t[2] == q:
                   newstatelabel = (q[0],origin[1]+t[1])
                   if newstatelabel != q:
                      self.transitions[origin].remove(t)
                      self.transitions[origin].add((t[0],t[1],newstatelabel))
                      self.states[newstatelabel] = set(origin)
                      self.transitions[newstatelabel] = set()
                      for t in self.transitions[q]:
                         self.transitions[newstatelabel].add(t)
                         self.states[t[2]].remove(q)
                         self.states[t[2]].add(newstatelabel)
                      del self.states[q]
                      del self.transitions[q]


# **********************Additional auxiliary functions for the learner***********************

# pushback function used in inner loop of the learner; removes the suffix v from the output of the incoming transition e and adds it as a prefix to all outputs
# of all outgoing transitions of the destination state of e
def pushback (T,v,e):
   #print 'pushback called with',v,e
   if v == '':
      return
   # Remove the edge e
   T.transitions[e[0]].remove((e[1],e[2],e[3]))
   # ...and replace it with one in which the output string does not include the suffix v
   T.transitions[e[0]].add((e[1],e[2][:len(e[2])-len(v)],e[3]))
   to_remove = set()
   to_add = set()
   # Replace all outgoing transitions of the destination state of e with one that adds v as a prefix to the output string
   for edge in T.transitions[e[3]]:
      #print edge
      if type(edge[1]) == tuple:
         newtuple = ()
         for s in edge[1]:
            newtuple+=(v+s,)
         to_add.add((edge[0],newtuple,edge[2]))
      else:
         to_add.add((edge[0],v+edge[1],edge[2]))
      to_remove.add(edge)

   T.transitions[e[3]].difference_update(to_remove)
   T.transitions[e[3]].update(to_add)

# searches T for non-determinism, returns true if none if found, otherwise returns two edges causing non-determinism (very inefficient!)
def subseq (T):
   for t in T.transitions:
      for e1 in T.transitions[t]:
         for e2 in T.transitions[t]:
            if e1 != e2 and e1[0] == e2[0]:
               if e1[2] < e2[2]:
                  return ((t,)+e1,(t,)+e2)
               else:
                  return ((t,)+e2,(t,)+e1)
   return 1

# returns the lexicographically first state in the state set Q
def first(Q):
   return sorted(Q)[0]

# returns the lexicographically last state in the state set Q
def last(Q):
   return sorted(Q)[-1]

# returns the next state in the lexicographically ordered state set Q after q.
# sts is a list of the states before any merging has taken place, so this function has to find
# the next state based on that list, but also make sure that state still exists in Q
def nextq(sts,Q,q):
   sortedQ = sorted(sts)
   i = sortedQ.index(q)
   cand = sortedQ[i+1]
   while not cand in Q and cand != last(sortedQ):
      i+=1
      cand = sortedQ[i+1]
   return cand

def create_new_output(output1, output2):
   if type(output1) == tuple:
      if output2 not in output1:
         return (output2,)+output1
      else:
         return output1
   elif type(output2) == tuple:
      if output1 not in output2:
         return (output1,)+output2
      else:
         return output2
   else:
      return (output1,output2)

# merges two states q1 and q2 in T
def merge (T,q1,q2):

   if len(q2[1]) < len(q1[1]):
     q1, q2 = q2, q1

   for out in T.transitions[q2]:
      # Redirect q2's outgoing transitions to originate from q1 instead
      T.transitions[q1].add((out[0],out[1],out[2]))
      # Also remove q2 from the incoming list of the destination state of each of these transitions...
      T.states[out[2]].remove(q2)
      # ...and add q1 instead
      T.states[out[2]].add(q1)

   # Now redirect all of q2's incoming transitions to go to q1 instead
   to_remove = set()
   to_add = set()
   for incoming in T.states[q2]:
      for out in T.transitions[incoming]:
         if out[2] == q2:
            to_remove.add(out)
            to_add.add((out[0],out[1],q1))
      T.transitions[incoming].difference_update(to_remove)
      T.transitions[incoming].update(to_add)
      to_remove = set()
      to_add = set()

   # Now add those states to q1's incoming list
   T.states[q1].update(T.states[q2])

   # Now remove q2 entirely
   del T.states[q2]
   del T.transitions[q2]

# takes two edges e1 = (q1, a1, x1, q1') and e2 = (q2, a2, x2, q2') and merges their destination states (q1' and q2')
def merge2 (T,e1,e2):

   #print 'merge2 called with',e1,e2
   # Make every outgoing transition of q2' leave q1' instead
   for out in T.transitions[e2[3]]:
      T.transitions[e1[3]].add((out[0],out[1],out[2]))
      T.states[out[2]].remove(e2[3])
      T.states[out[2]].add(e1[3])

   to_remove = set()
   to_add = set()

   # For every state with an incoming transition to q2'...
   for incoming in T.states[e2[3]]:

      # Make sure it's not a loop
      if incoming != e1[0]:
         # Find the transition from that state to q2'
         for out in T.transitions[incoming]:
            if out[2] == e2[3]:
               to_remove.add(out)
               # Create a new transition that goes to q1' instead
               #print 'adding 1',(incoming,out[0],out[1],e1[3])
               to_add.add((out[0],out[1],e1[3]))

         T.transitions[incoming].difference_update(to_remove)
         T.transitions[incoming].update(to_add)
         to_remove = set()
         to_add = set()

   # States with an incoming transition to q2' now get added to q1''s set of states
   T.states[e1[3]].update(T.states[e2[3]])
   # Remove the actual transition causing the non-determinism
   T.transitions[e1[0]].remove((e2[1],e2[2],e2[3]))

   # Create the new transition that will replace it

   #if type(e1[2]) == tuple:
    #  if e2[2] not in e1[2]:
     #    print 'adding 2',(e1[1],(e2[2],)+e1[2],e1[3])
   T.transitions[e1[0]].add((e1[1],create_new_output(e1[2],e2[2]),e1[3]))
   T.transitions[e1[0]].remove((e1[1],e1[2],e1[3]))


   # Otherwise, make the output a tuple with both the previous output and x2
   #else:
    #  print 'adding 3',(e1[1],(e2[2],e1[2]),e1[3])
     # T.transitions[e1[0]].add((e1[1],(e2[2],e1[2]),e1[3]))
      #T.transitions[e1[0]].remove((e1[1],e1[2],e1[3]))


   # Now remove q2' entirely from the FST (unless the transition was a loop - we don't want to remove q1')
   if e1[3] != e2[3]:
      del T.states[e2[3]]
      del T.transitions[e2[3]]


#*********************************** Modified ISL state-merging learner *************************************

def ISLFLAv2(T):

   # Assumption is that T is a PTT that has been made onward via its onward method
   # This version of the ISLFLA creates semi-determinism instead of halting when non-determinism
   # is created that cannot be resolved via pushback

   # Go through the states in order (length-lexicographic). Since the actual state set is changing throughout
   # we need a list copy of the state set before any merging takes place (python complains otherwise)
   states = list(T.states)
   q = nextq(states,T.states,first(T.states))

   while q < last(T.states):

      # Merge each state with its k-1 suffix
      # Something was going wrong with final states so I added the second condition here
      if q[1] != suffix(q[1],k-1) and q[0][-1] != '#':

         for tran in T.states:
             if tran[1] == suffix(q[1],k-1) and tran[0][-1] != '#':
                q1 = tran

         #print "outer loop {} {}".format(T.transitions[q1], T.transitions[q])
         merge(T,q1,q)

         # Determine whether that merge created non-determinism (i.e., the FST is no longer subsequential)
         ssqtest = subseq(T)

         while ssqtest != 1:

            # ssqtest will have two edges ((q1,a1,x1,q1'), (q1,a1,x2,q2')) so the following is just parsing those
            # s and t are the destination states of the edges and v and w are the output strings (variables choices are
            # following Oncina et al. paper
            s = ssqtest[0][3]
            t = ssqtest[1][3]
            v = ssqtest[0][2]
            w = ssqtest[1][2]

            # testing whether the non-determinism can be resolved with pushback. Previously, the algorithm would halt
            # at this point if the answer is no. Now we call merge2 instead, to resolve it by creating semi-determinism
            if (ssqtest[0][2] != ssqtest[1][2] and ssqtest[0][1] == '#') or (s<q and not v in get_prefixes(w)):
               merge2(T,ssqtest[0],ssqtest[1])
               break

            # otherwise, resolve it with pushback as in the standard ISLFLA
            u = lcp(set([v,w]))
            pushback(T,v[len(u):],ssqtest[0])
            pushback(T,w[len(u):],ssqtest[1])
            merge(T,s,t)

            # check whether new merge has created new non-determinism
            ssqtest = subseq(T)

      q = nextq(states,T.states,q)



# **************Test case 1: LD sibilant harmony, progressive, asymmetric (2-TSL)**************

# data = set([('c','K'),('t','T'),('a','A'),('cc','KK'),('tt','TT'),('aa','AA'),('ca','KA'),('ac','AK'),('ta','TA'),('at','AT'),('ct','KT'),('tc','TK')])
# k=1
# test1 = PTT(data,set(['c','t','a']))
#data = set([('a','a'),('s','s'),('S','S'),('sa', 'sa'), ('sS', 'ss'), ('ss', 'ss'), ('as', 'as'), ('aa', 'aa'), ('aS', 'aS'), ('Sa', 'Sa'), ('Ss', 'SS'), ('SS', 'SS'), ('sas', 'sas'), ('saa', 'saa'), ('saS', 'sas'), ('sSs', 'sss'), ('sSS', 'sss'), ('sSa', 'ssa'), ('sss', 'sss'), ('ssS', 'sss'), ('ssa', 'ssa'), ('ass', 'ass'), ('asS', 'ass'), ('asa', 'asa'), ('aas', 'aas'), ('aaS', 'aaS'), ('aaa', 'aaa'), ('aSs', 'aSS'), ('aSS', 'aSS'), ('aSa', 'aSa'), ('Sas', 'SaS'), ('SaS', 'SaS'), ('Saa','Saa'), ('Sss', 'SSS'), ('SsS', 'SSS'), ('Ssa', 'SSa'), ('SSs', 'SSS'), ('SSS', 'SSS'), ('SSa', 'SSa')])

data = set([("VNC", "VNC"), ("CVN", "CVN"), ("CNC", "CNC"), ("NNC", "NNC"), ("NNV", "NNN"), ("VNN", "VNN"), ("NVN", "NNN"), ("VCN", "VCN"),
("CCV", "CCV"), ("CN", "CN"), ("VVC", "VVC"), ("NVC", "NNC"), ("CC", "CC"), ("NV", "NN"), ("NC", "NC"), ("VNV", "VNN"), ("VCV", "VCV"),
("CCN", "CCN"), ("N", "N"), ("CNV", "CNN"), ("NN", "NN"), ("C", "C"), ("NCC", "NCC"), ("CV", "CV"), ("CNN", "CNN"), ("VN", "VN"),
("VVN", "VVN"), ("VC", "VC"), ("NCV", "NCV"), ("CVC", "CVC"), ("VV", "VV"), ("VCC", "VCC"), ("NCN", "NCN"), ("V", "V"), ("NVV", "NNN"),
("CVV", "CVV"), ("CCC", "CCC"), ("VVV", "VVV"), ("NNN", "NNN")])

k=2
#test1 = PTT(data,set(['s','S','a']))
test1 = PTT(data,set(['V','N','C']))
test1.onward(('',''),'')
test1.relabel()
ISLFLAv2(test1)
#print print_FST(test1)

print test1.transduce('CNVVCVN')










#inputs = set([x[0] for x in data])
#if test1.transduce_set(inputs) == data:
#   print 'test 1 passed!'

# Input Strictly Local Function Learning Algorithm (ISLFLA)
# Jane Chandlee

import copy
import itertools

# **************Auxiliary functions**************

# returns the set of prefixes for string w
def get_prefixes(w):
   return set([w[0:i] for i in range(len(w)+1)])

# returns the longest common prefix for a set of strings S
def lcp(S):
   if len(S) == 0:
      return ''
   common_prefs = set()
   common_prefs.update(get_prefixes(S.pop()))
   for w in S:
      common_prefs.intersection_update(get_prefixes(w))
   return max(common_prefs,key=len)






# The PTT is represented as a dictionary in which the keys are state labels and the values are tuples. The first member of the tuple is a set of outgoing transitions, each represented with a tuple (q, x, y, q'). The second member of the tuple is the set of states from which the state has an incoming transition. This function takes the imported data (set of input-output tuples) and returns the PTT.

def buildPTT(S):
   T = dict()

   for iopair in S:
      for p in get_prefixes(iopair[0]):
         if not p in T:
            T[p] = (set(),set())

      T[iopair[0]][0].add((iopair[0],'#',iopair[1],iopair[0]+'#'))
      T[iopair[0]+'#'] = (set(),set([iopair[0]]))

   for state in T.keys():
      for symbol in X:
         if state+symbol in T:
            T[state][0].add((state,symbol,'',state+symbol))
            T[state+symbol][1].add(state)
   return T


# ************Making the PTT onward******************************



# locates the transition in T from q on a and returns a tuple of the output string and destination state
def get_wq(T,q,a):
   for trans in T[q][0]:
      if trans[1] == a:
         return (trans[2],trans[3])
   return 0

# returns a set containing the output strings for all of the outgoing transitions of state q
def get_outputs(T,q):
   outgoing_outstrings = set()
   for trans in T[q][0]:
      outgoing_outstrings.add(trans[2])
   return outgoing_outstrings

# recursive function, initially called with the initial state and the empty string (follows algorithm in de la Higuera (2010))
def onward(T,q,u):
   for a in X:
      wq = get_wq(T,q,a)
      if wq != 0:
         OTST = onward(T,wq[1],a)

         T[q][0].remove((q,a,wq[0],wq[1]))
         T[q][0].add((q,a,wq[0]+OTST[2],wq[1]))

   outs = get_outputs(T,q)
   if len(outs) > 0:
      f = lcp(outs)
   else:
      f = ''
   if f != '':
      for a in X:
         wq2 = get_wq(T,q,a)
         if wq2 != 0:
            T[q][0].remove((q,a,wq2[0],wq2[1]))
            T[q][0].add((q,a,wq2[0][len(f):],wq2[1]))

   return (T,q,f)

# **********************ISLFLA***********************

# returns the suffix of length k-1 of a state
def suffix(state, k):
   if len(state) < k-1:
      return state
   elif k == 1:
      return ''
   else:
      return state[-(k-1):]

# pushback function used in inner loop of ISLFLA; removes the suffix v from the output of the incoming transition e and adds it as a prefix to all outputs of all outgoing transitions of the destination state of e
def pushback(T,v,e):
   # Remove the edge...
   T[e[0]][0].remove(e)
   # ...and replace it with one in which the output string does not include the suffix v
   T[e[0]][0].add((e[0],e[1],e[2][:len(e[2])-len(v)],e[3]))

   to_remove = set()
   to_add = set()

   # Replace all outgoing transitions of the destination state of e with one that adds v as a prefix to the output string
   for edge in T[e[3]][0]:
      to_add.add((edge[0],edge[1],v+edge[2],edge[3]))
      to_remove.add(edge)

   T[e[3]][0].difference_update(to_remove)
   T[e[3]][0].update(to_add)

   return T

# searches T for non-determinism, returns true if none if found, otherwise returns two edges causing non-determinism (very inefficient!)
def subseq(T):
   for t in T:
      for e1 in T[t][0]:
         for e2 in T[t][0]:
            if e1 != e2 and e1[1] == e2[1]:
               if e1[3] < e2[3]:
                  return (e1,e2)
               else:
                  return (e2,e1)
   return 1

# returns the lexicographically first state in the state set Q
def first(Q):
   sortedQ = sorted(Q)
   return sortedQ[0]

# returns the lexicographically last state in the state set Q
def last(Q):
   sortedQ = sorted(Q)
   return sortedQ[len(sortedQ)-1]

# returns the next state in the lexicographically ordered state set Q after q.
def nextq(sts,Q,q1):
   sortedQ = sorted(sts)
   i = sortedQ.index(q1)
   cand = sortedQ[i+1]
   while not cand in Q and cand != last(sortedQ):
      i+=1
      cand = sortedQ[i+1]
   return cand

# merges two states q1 and q2 in T
def merge(T,q1,q2):
   if q2 == suffix(q1,k):
      q2 = q1
      q1 = suffix(q1,k)
   for out in T[q2][0]:
      # Redirect q2's outgoing transitions to originate from q1 instead
      T[q1][0].add((q1,out[1],out[2],out[3]))
      # Also remove q2 from the incoming list of the destination state of each of these transitions...
      T[out[3]][1].remove(q2)
      # ...and add q1 instead
      T[out[3]][1].add(q1)

   # Now redirect all of q2's incoming transitions to go to q1 instead
   to_remove = set()
   to_add = set()
   for incoming in T[q2][1]:
      for out in T[incoming][0]:
         if out[3] == q2:
            to_remove.add(out)
            to_add.add((incoming,out[1],out[2],q1))
      T[incoming][0].difference_update(to_remove)
      T[incoming][0].update(to_add)
      to_remove = set()
      to_add = set()

   # Now add those states to q1's incoming list
   T[q1][1].update(T[q2][1])

   # Now remove q2 entirely
   del T[q2]
   return T


def ISLFLA(T):
   OTST = onward(T,'','')[0]

   target = open('/Users/janemc1980/otst.dot','a')
   target.write(print_FST(OTST))

   states = list(T.keys())
   q = nextq(states,OTST.keys(),first(OTST.keys()))

   while q < last(OTST.keys()):
      if q != suffix(q,k):

         OTST = merge(OTST,suffix(q,k),q)
         print "(outer loop) merging " + q + " and " + suffix(q,k)

         ssqtest = subseq(OTST)
         while ssqtest != 1:
            s = ssqtest[0][3]
            t = ssqtest[1][3]
            v = ssqtest[0][2]
            w = ssqtest[1][2]

            if (ssqtest[0][2] != ssqtest[1][2] and ssqtest[0][1] == '#') or (s<q and not v in get_prefixes(w)):
               print "FAIL"
               break

            u = lcp(set([v,w]))
            OTST = pushback(OTST,v[len(u):],ssqtest[0])
            OTST = pushback(OTST,w[len(u):],ssqtest[1])
            OTST = merge(OTST,s,t)
            print "(inner loop) merging " + s + " and " + t

            ssqtest = subseq(OTST)

      q = nextq(states,OTST.keys(),q)

   return OTST

def get_trans(self,q,a):
   for t in self.transitions[q]:
      if t[0] == a:
         return (t[1],t[2])
   return (None,None)

def transduce(self,s):
   output = ''
   state = ('','')
   for c in s:
      out,state = self.get_trans(state,c)
      output+=str(out)
   return output


X = set(['c','a','t'])
PTT = buildPTT(set())
X.add('#')
OTST = onward(PTT,'','')[0]

for o in OTST:
   print o,OTST[o]


T1 = ISLFLA(PTT)
print T1

# print result to a file
#target = open('/Users/janemc1980/result.dot','a')
#target.write(print_FST(PTT))






# ***********Functions for printing a FST in .dot format**************
def lookup_index (Q,l):
   for q in Q:
      if q[0] == l:
         return str(q[1])

def print_FST (f):
   fst = "digraph G { rankdir = LR "
   i = 0
   indexed_states = []
   for q in f.keys():
      indexed_states.append((q,i))
      fst += (str(i)+"[label=\"" + q + "\"]")
      i += 1

   for q in f.keys():
      for t in f[q][0]:
         fst += (lookup_index(indexed_states, q) + "->"+ lookup_index(indexed_states,t[3])+ "[label = \"" + t[1] + ":")
         if t[2] == '':
            fst += "&#955;\"]"
         else:
            fst += (t[2] + "\"]")

   return (fst+"}")

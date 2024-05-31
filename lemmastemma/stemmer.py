#!/usr/bin/env python3
#re https://stackoverflow.com/a/22283803

import sys
import nltk
from nltk.stem import PorterStemmer

ps = PorterStemmer()
for in_fnam in sys.argv[1:]:
  out_fnam = in_fnam + '.stemmed'
  with open(in_fnam) as in_f:
    with open(out_fnam, 'w') as out_f:
      for line in in_f:
        print(" ".join([ps.stem(w) for w in nltk.tokenize.word_tokenize(line)]), file = out_f)

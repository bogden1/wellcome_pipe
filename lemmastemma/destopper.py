#!/usr/bin/env python3
#re https://stackoverflow.com/a/72999890
import sys
import nltk
#nltk.download('stopwords')

stop_words = set(nltk.corpus.stopwords.words('english'))
for in_fnam in sys.argv[1:]:
  out_fnam = in_fnam + '.destopped'
  with open(in_fnam) as in_f:
    with open(out_fnam, 'w') as out_f:
      for line in in_f:
        print(" ".join([w for w in nltk.tokenize.word_tokenize(line) if w.lower() not in stop_words]), file = out_f)
        #print(" ".join([w for w in line.split() if w.lower() not in stop_words]), file = out_f)

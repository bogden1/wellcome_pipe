#!/usr/bin/env python3

import sys
import string

translation_table = str.maketrans('', '', string.punctuation)

for in_fnam in sys.argv[1:]:
  out_fnam = in_fnam + '.depunctuated'
  with open(in_fnam) as in_f:
    with open(out_fnam, 'w') as out_f:
      for line in in_f:
        print(line.translate(translation_table), file = out_f)


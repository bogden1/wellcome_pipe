#!/usr/bin/env python3
#Applying HaToRI's approach (serv/src/wordcloud/__init__.py)

import os
import sys
import pickle
import numpy as np
import pandas as pd
import argparse

sys.path.append(os.path.dirname(sys.argv[0]))
import _wordcloud as wc

parser = argparse.ArgumentParser()
parser.add_argument('topic_counts',
                    nargs = '+',
                    help = 'Topic count to use (e.g. "50" for "17xx_lemmatized_sorted-topic_state_50_counts.df" (assuming --prefix is "17xx_lemmatized_sorted")')
parser.add_argument('--prefix',
                    default = '17xx_lemmatized_sorted',
                    help = 'Prefix for document topic composition file(s) e.g. to use "17xx_lemmatized_sorted-topic_state_*.df", pass "17xx_lemmatized_sorted"')
parser.add_argument('--output-dir',
                    default = os.path.dirname(sys.argv[0]) + '/data/corpora/examples/clouds',
                    help = 'Top-level location to write wordclouds to')
parser.add_argument('--force',
                    action = 'store_true',
                    help = 'Permit writing into an existing directory')
parser.add_argument('--colorize',
                    action = 'store_true',
                    help = 'Display words in different colours')
parser.add_argument('--dark',
                    type = float,
                    default = 0.99,
                    help = '"Dark" value (0 - 1). No effect if color is enabled.')
args = parser.parse_args()

#path stuff
if os.path.exists(args.output_dir):
  if args.force:
    print(f'Writing into existing directory {args.output_dir}. Previous output will not be deleted (unless it gets overwritten).', file = sys.stderr)
  else:
    print(f'Output dir {args.output_dir} already exists. Delete it, or use --force.', file = sys.stderr)
    sys.exit(1)
else:
  os.makedirs(args.output_dir, exist_ok = True)

for topic_count in args.topic_counts:
  path = f'{args.output_dir}/{os.path.basename(args.prefix)}_{topic_count}'
  if not os.path.exists(path):
    os.mkdir(path)
  with open(f'{args.prefix}-topic_state_{topic_count}_counts.df', 'rb') as f:
    counts_df = pickle.load(f)

  #scale the frequencies as HaToRI does (I think with the effect of squashing them closer together, so we see across a greater range)
  #note that the raw count will do just fine as frequency within a topic (they would all be divided by the same number to get the actual within-topic frequency)
  nl = np.log(2 + counts_df['doc']) #returns a series

  #generate a word cloud for each topic
  for topic_num in range(0, nl.index.get_level_values('topic').nunique()):
    freqs = nl.loc[topic_num]
    freqs.sort_values(ascending = False).to_csv(f'{path}/topic_{topic_num}.csv')
    wc.draw(freqs.to_dict(),                    f'{path}/topic_{topic_num}', args.colorize, args.dark)

#!/usr/bin/env python3

import os
import sys
import json
import pickle
import argparse
import numpy as np
import pandas as pd

NO_SUBJECT_ID = '00000000'
NO_SUBJECT_LABEL = '<No Subject>'

sys.path.append(os.path.dirname(sys.argv[0]))
import _wordcloud as wc

parser = argparse.ArgumentParser()
parser.add_argument('topic_counts',
                    nargs = '+',
                    help = 'Postfix to use, e.g. 10, 50, 100, etc. So if --prefix is "17xx_lemmatized_sorted" and this is set to 50, we will read from "17xx_lemmatized_sorted-composition_50.txt"')
parser.add_argument('--prefix',
                    default = '17xx_lemmatized_sorted',
                    help = 'Prefix for document topic composition file(s) e.g. to use "17xx_lemmatized_sorted-composition_*.txt", pass "17xx_lemmatized_sorted"')
parser.add_argument('--subject-labels',
                    default = 'data/corpora/example/normalized/subjects_map.json',
                    help = 'Location of subject id->label map (a decorate_subjects.py output)')
parser.add_argument('--doc-subjects',
                    default = 'data/corpora/example/normalized/subjects.json',
                    help = 'Location of cat id->subject id map (a decorate_subjects.py output)')
parser.add_argument('--mallet-metadata',
                    required = True,
                    help = 'TSV file used for Mallet input')
parser.add_argument('--reread-mallet-metadata',
                    action = 'store_true',
                    help = 'Force re-read of metadata file, even if a cached dataframe exists')
parser.add_argument('--colorize',
                    action = 'store_true',
                    help = 'Display words in different colours')
parser.add_argument('--dark',
                    type = float,
                    default = 0.01,
                    help = '"Dark" value (0 - 1). No effect if color is enabled.')
parser.add_argument('--output-dir',
                    default = os.path.dirname(sys.argv[0]) + '/data/corpora/examples/clouds',
                    help = 'Top-level location to write wordclouds to')
parser.add_argument('--force',
                    action = 'store_true',
                    help = 'Permit writing into an existing directory')
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

if (not args.reread_mallet_metadata) and os.path.exists(args.mallet_metadata + '.df') and os.path.getmtime(args.mallet_metadata + '.df') > os.path.getmtime(args.mallet_metadata):
  with open(args.mallet_metadata + '.df', 'rb') as f:
    metadata = pickle.load(f)
else:
  metadata = pd.read_csv(args.mallet_metadata, sep = '\t', names = ['cat_id', 'year'], usecols = range(0,2))
  metadata.loc[:,'cat_id'] = metadata['cat_id'].str.strip()
  metadata = metadata.rename_axis('doc_id')
  with open(args.mallet_metadata + '.df', 'wb') as f:
    pickle.dump(metadata, f)
metadata = metadata.assign(cat_id = metadata['cat_id'].str.split().str[-1]) #get the Wellcome catalogue doc id, given current TSV format

with open(args.doc_subjects) as f:
  doc_subjs = json.load(f)

with open(args.subject_labels) as f:
  subj_labels = json.load(f)
if NO_SUBJECT_ID in subj_labels:
  print('No subject indicator unexpectedly listed as a real subject id', file = sys.stderr)
  sys.exit(1)
else:
  subj_labels[NO_SUBJECT_ID] = NO_SUBJECT_LABEL

for topic_count in args.topic_counts:
  path = f'{args.output_dir}/{os.path.basename(args.prefix)}_{topic_count}'
  if not os.path.exists(path):
    os.mkdir(path)
  in_fnam = f'{args.prefix}-composition_{topic_count}.txt'
  with open(in_fnam) as f:
    line = next(f)
    n_topics = line.count('\t') - 1
  topics = list(range(0, n_topics))
  df = pd.read_csv(in_fnam, sep = '\t', index_col = 0, names = ['doc_id', 'author'] + topics).join(metadata, validate = '1:1')
  for topic in topics:
    out_basename = f'{path}/topic_{topic}_subjects'
    doc_proportions = df[[topic, 'cat_id']].rename(columns = lambda x: x if x != topic else 'proportion')
    subj_proportions = doc_proportions.assign(subj_id = doc_proportions['cat_id'].map(doc_subjs)).drop('cat_id', axis = 1)
    #subj_id col now contains one of:
    #A list of subject ids for this doc
    #None: this doc id is in the doc->subjects mapping and has no subjects
    #NaN: this doc_id does not exist in the doc->subjects mapping (so I assume this is a bug earlier in the pipeline, generating a bad doc id)
    #So convert None (but not NaN) into an indicator of that there is no subject
    subj_proportions = subj_proportions.assign(subj_id = subj_proportions.subj_id.map(lambda x: NO_SUBJECT_ID if x is None else x))

    #create a single-col df, indexed by subject id, with proportion of that subject id in the topic (count of times that subject appeared, multiplied by the proportion of the document that corresponds to the topic)
    subj_proportions = subj_proportions.explode('subj_id') #explode lists of subjects out to separate rows
    subj_proportions = subj_proportions.groupby('subj_id').sum()

    #replace index of subj ids with index of equivalent labels, combining any identical labels
    #some subj ids have the same label (e.g. medicine seems to have 3 distinct ids), so sum proportions for the same label
    subj_proportions['labels'] = subj_proportions.index.map(subj_labels)
    subj_proportions = subj_proportions.set_index('labels')
    subj_proportions = subj_proportions.groupby(level = 0).sum()

    #attempt at computing some reasonable frequencies for a word cloud
    #if I was better at maths I'd come up with something more sensible here
    freqs = subj_proportions['proportion'] #returns a series
    freqs = np.log(2 + freqs) #still a series
    freqs.sort_values(ascending = False).to_csv(out_basename + '.csv')
    wc.draw(freqs.to_dict(), out_basename, args.colorize, args.dark)

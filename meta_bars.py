#!/usr/bin/env python3
#plotly export to SVG is a bit messy, especially where links are concerned.
#Output of this script gets fixed up by svg_fixup.py

import os
import sys
import json
import pickle
import argparse
import pandas as pd
import plotly.express as px
from multiprocessing import Pool

def up_to_date(in_fnam, out_fnam):
  return os.path.exists(out_fnam) and os.path.getmtime(out_fnam) > os.path.getmtime(in_fnam) and os.path.getmtime(out_fnam) > os.path.getmtime(sys.argv[0])

parser = argparse.ArgumentParser()
parser.add_argument('topic_counts',
                    nargs = '+',
                    help = 'Postfix to use, e.g. 10, 50, 100, etc. So if --prefix is "17xx_lemmatized_sorted" and this is set to 50, we will read from "17xx_lemmatized_sorted-composition_50.txt"')
parser.add_argument('--prefix',
                    default = '17xx_lemmatized_sorted',
                    help = 'Prefix for document topic composition file(s) e.g. to use "17xx_lemmatized_sorted-composition_*.txt", pass "17xx_lemmatized_sorted"')
parser.add_argument('--mallet-metadata',
                    required = True,
                    help = 'TSV file used for Mallet input')
parser.add_argument('--reread-mallet-metadata',
                    action = 'store_true',
                    help = 'Force re-read of metadata file, even if a cached dataframe exists')
parser.add_argument('--output-dir',
                    default = os.path.dirname(sys.argv[0]) + '/data/corpora/examples/figures',
                    help = 'Top-level location to write wordclouds to')
parser.add_argument('--force',
                    action = 'store_true',
                    help = 'Permit writing into an existing directory')
parser.add_argument('--documents',
                    action = 'store_true',
                    help = 'Generate a bar chart for every document. May take hours.')
parser.add_argument('--topics',
                    action = 'store_true',
                    help = 'Generate summary charts for every topic. Pretty quick.')
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

  doc_topics_df = df.set_index(df.cat_id).drop(['year', 'author', 'cat_id'], axis = 1)
  if args.topics:
    for topic in doc_topics_df.columns:
      t_s = doc_topics_df[topic]
      out_fnam = f'{path}/topic_{topic}_topdocs.svg'
      print(f'Writing summary charts for topic {topic}')
      if up_to_date(in_fnam, out_fnam):
        print(f'  Skipped "top 10" for topic {topic} as already up to date')
      else:
        top_10 = t_s.nlargest(10)
        fig = px.bar(top_10 * 100, range_y = [0, 100], labels = {'index': 'Document', 'value': f'% from topic {topic}'})
        for x, y in top_10.items():
          fig.add_annotation(x = x, y = y * 100, text = f'<a href="https:wrapper_{x}.html">{x}</a>', showarrow = False, yshift = 10)
        fig.update_layout(showlegend = False)
        fig.write_image(out_fnam)

      #out_fnam = f'{path}/topic_{topic}_docs40.svg'
      #if up_to_date(in_fnam, out_fnam):
      #  print(f'  Skipped "over 40%" for topic {topic} as already up to date')
      #else:
      #  over_40 = t_s[t_s > 0.4].sort_values(ascending = False)
      #  if len(over_40) > 150:
      #    print(f"Truncating topic {topic}'s docs40 from {len(over_40)} to 150 rows", file = sys.stderr)
      #    over_40 = over_40.head(150)
      #  fig = px.scatter(over_40 * 100, range_y = [0, 100], labels = {'index': 'Document', 'value': f'% from topic {topic}'})
      #  for x, y in over_40.items():
      #    fig.add_annotation(x = x, y = y * 100, text = f'<a href="https:wrapper_{x}.html">{x}</a>', showarrow = False, yshift = 10, textangle = -90)
      #  fig.update_layout(showlegend = False)
      #  fig.write_image(out_fnam)

  if args.documents:
    def draw_doc(title, row, fnam):
      text = [f'<a href="https://example/com/topic_{x}">{x}</a>' for x in row.index.to_list()]
      text = [f'{x}' for x in row.index.to_list()]
      fig = px.bar(row, y = row * 100, title = title, range_y = [0, 100], labels = {'index': 'Topic', 'y': 'Topic %'})#, text = text)
      fig.update_layout(showlegend = False)
      for x, y in row.items():
        if y > 0.05:
          fig.add_annotation(x = x, y = y * 100, text = f'<a href="https:../topic_{x}.html">{x}</a>', showarrow = False, yshift = 7, xshift = -1, textangle = -90, font_size = 8)
      fig.write_image(fnam)

    pool = Pool()
    orders = []
    for cat_id, row in doc_topics_df.iterrows():
      print(f'Writing chart for doc {cat_id}')
      out_fnam = f'{path}/{cat_id}.svg'
      if up_to_date(in_fnam, out_fnam):
        print(f'  Skipped doc {cat_id} as already up to date')
      else:
        orders.append((cat_id, row, out_fnam))
        if len(orders) == os.cpu_count():
          pool.starmap(draw_doc, orders)
          orders = []
    if len(orders):
      pool.starmap(draw_doc, orders)

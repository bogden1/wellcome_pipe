#!/usr/bin/env python3
#plotly export to SVG is a bit messy, especially where links are concerned.
#Output of this script gets fixed up by svg_fixup.py

import os
import sys
import json
import pickle
import plotly
import argparse
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from works_lookup import WorksLookup
from multiprocessing import Pool
from jsonpath_ng.ext import parse as json_parse

def up_to_date(in_fnam, out_fnam):
  return os.path.exists(out_fnam) and os.path.getmtime(out_fnam) > os.path.getmtime(in_fnam) and os.path.getmtime(out_fnam) > os.path.getmtime(sys.argv[0])

works_lookup = WorksLookup('j', None, database = 'wellcome_works')
def get_text_url(identifier):
  manifest_url = works_lookup.cooked_json_lookup(identifier, 'items', '$.locations[*].url')
  if manifest_url is None:
    print(f'{identifier} lookup failed, or it does not have exactly 1 mainfest URL', file = sys.stderr)
    return None
  text_url = [x.value for x in json_parse("sequences[*].rendering[?@.format='text/plain'].@id").find(requests.get(manifest_url).json())]
  if len(text_url) != 1:
    print(f'{identifier} (via {manifest_url}) does not have exactly 1 plain text rendering', file = sys.stderr)
    return None
  return text_url[0]

def get_title(identifier):
  return works_lookup.field_lookup(identifier, 'title')

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
parser.add_argument('--works-db', default = 'wellcome-works')
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

#NB "metadata" here is the premallet tsv file (or a dataframe cache of it)
#I think this new line here is adding the split (the chunk that I am on)
metadata = metadata.assign(split_id = metadata['cat_id'].str.split().str[-2])
metadata = metadata.assign(cat_id = metadata['cat_id'].str.split().str[-1]) #get the Wellcome catalogue doc id, given current TSV format
#metadata = metadata.assign(text_url = lambda x: get_text_url(x.cat_id))
print(metadata)

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

  doc_topics_df = df.set_index([df.cat_id, df.split_id]).drop(['year', 'author', 'cat_id', 'split_id'], axis = 1)
  #doc_topics_df = df.set_index(df.cat_id).drop(['year', 'author', 'cat_id'], axis = 1)
  if args.topics:
    print('TOPICS')
    for topic in doc_topics_df.columns:
      t_s = doc_topics_df[topic]
      print(t_s)
      out_fnam = f'{path}/topic_{topic}_topdocs.svg'
      print(f'Writing summary charts for topic {topic}')
      if up_to_date(in_fnam, out_fnam):
        print(f'  Skipped "top 10" for topic {topic} as already up to date')
      else:
        top_10 = t_s.nlargest(10)
        fig = px.bar(top_10 * 100, labels = {'index': 'Document', 'value': f'% from topic {topic}'})
        for x, y in top_10.items():
          #TODO: Making x the "split" rather than repeating the doc (which is also the x axis) would make a lot of sense here
          #Just need to work out where that information is
          fig.add_annotation(x = x, y = y * 100, text = f'<a href="https:wrapper_{x}.html">{x}</a>', showarrow = False, yshift = 10)
        fig.update_layout(showlegend = False)
        #fig.update_layout(barmode = 'stack')
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
    print('DOCS')
    def draw_doc(identifier, text_url, title, row, fnam):
      #text_url = row.text_url
      if text_url is None:
        text_url='<no url>'
      text_url = text_url.split('/')[-1]
      row = row.set_index('split_id').drop(['cat_id'], axis=1)
      #text = [f'<a href="https://example/com/topic_{x}">{x}</a>' for x in row.index.to_list()]
      #text = [f'{x}' for x in row.index.to_list()]
      row = row.sort_index(key = lambda x: x.str.split('-').str[0].astype(int)).T
      print(row)
      fig = px.bar(row, x = row.index, y = row.columns, title = f'<a href="https://wellcomecollection.org/works/{identifier}">{title}</a>', labels = {'index': 'Topic', 'y': 'Topic %'})#, text = text)
      fig.update_layout(xaxis_type = 'category', showlegend = False)
      for trace in fig.data:
        #print(trace)
        trace.text = f'<a>{text_url}:{trace.name}</a>'
      #splits = [f'<a>{text_url}:{x}</a>' for x in row.columns] #this one works, but I cannot use it to pass a parameter
      #fig.update_traces(hoverinfo = 'text', text = splits)

      #fig.write_image(fnam + '.svg')
      #fig.write_html( fnam + '.html')
      #fig.write_json( fnam + '.json')
      with open(fnam + '.div', 'w') as f:
        print(plotly.offline.plot(fig, include_plotlyjs = False, output_type = 'div'), file = f) #re https://stackoverflow.com/a/38032952 and /a/36376371

    pool = Pool()
    orders = []
    print(doc_topics_df)
    for identifier, row in doc_topics_df.groupby(level='cat_id'):
      print(f'Writing chart for doc {identifier}')
      out_fnam = f'{path}/{identifier}'
      if False: #up_to_date(in_fnam, out_fnam):
        print(f'  Skipped doc {identifier} as already up to date')
      else:
        orders.append((identifier, get_text_url(identifier), get_title(identifier), row.reset_index(), out_fnam))
        if len(orders) == os.cpu_count():
          pool.starmap(draw_doc, orders)
          orders = []
    if len(orders):
      pool.starmap(draw_doc, orders)

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

text_url_cache = {}

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
#print(metadata)

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
  for topic in doc_topics_df.columns:
    out_fnam = f'{path}/doclist_topic_{topic}.html'
    with open(out_fnam, 'w') as f:
      t_s = doc_topics_df[topic].sort_values(ascending=False) #descending sort of all values (i.e. not within groups according to levels of the multiindex, a global sort)
      print('<html>', file = f)
      print('<head>', file = f)

      print(r'''<script>
function callback_header(e, action) {
  var e = window.e || e;
  if (e.target.tagName.toLowerCase() !== 'span')
    return ''

  if(e.target.title) {
    if(action === 1) {
      const tmp = e.target.title
      e.target.title = e.target.textContent
      e.target.textContent = tmp
    }
    return
  }

  const urlParams = new URLSearchParams(window.location.search)
  var proxy = urlParams.get('p')
  if(proxy)
    proxy = 'https://justcors.com/' + proxy + '/'
  else
    proxy = ''

  var id = e.target.id.split('_')
  var split = id[id.length - 1]
  split = split.split('-')
  var end = parseInt(split[1],10)
  var start = parseInt(split[0],10)
  id = id[0]
  fetch(proxy + id)
  .then(response=>response.text())
  .then(data => {
    const words = data.trim().split(/\s+/);
    const text = words.slice(start, end + 1).join(" ")
    e.target.title = text
    if(action === 1) {
      const tmp = e.target.title
      e.target.title = e.target.textContent
      e.target.textContent = tmp
    }
  })
  .catch(error => {
    e.target.bernard = 'Error loading words'
  })
  return e
}

function callback(e) {
  callback_header(e, 0)
}

function callback_click(e) {
  callback_header(e, 1)
}

if(document.addEventListener)
  document.addEventListener('mouseover', callback, false);
else
  document.attachEvent('onmouseover', callback);
if(document.addEventListener)
  document.addEventListener('click', callback_click, false);
else
  document.attachEvent('onclick', callback_click);
</script>''', file = f)

      print('</head><body><table><tr><td>Document</td><td>Split</td><td>Weight</td><tr>', file = f)

      for index, weight in t_s.items():
        doc_id, split = index
        if not doc_id in text_url_cache:
          text_url_cache[doc_id] = get_text_url(doc_id)
        text_url = text_url_cache[doc_id]
        print('<tr>', file = f)
        print('<td>', file = f)
        print(get_title(doc_id), file = f)
        print('</td>', file = f)
        print('<td>', file = f)
        print(f'<span id={text_url}_{split}>{split}</span>', file = f)
        print('</td>', file = f)
        print('<td>', file = f)
        print(weight, file = f)
        print('</td></tr>', file = f)
      print('</table></body></html>', file = f)

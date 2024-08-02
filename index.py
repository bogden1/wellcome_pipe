#!/usr/bin/env python3
#Example invocation: ./index.py web data/corpora/example/normalized/examplesorted_titles.json

import os
import sys
import json
import string


table = {}
for x in (10, 50, 100, 250, 500):
  table[f'17xx_rebuild_lemmatized_sorted_{x}'] = f'lemma_{x}'
  table[f'17xx_rebuild_entitystripped_lemmatized_sorted_{x}'] = f'lemma_noent_{x}'

root = sys.argv[1]

with open(f'{root}/index.html', 'w') as index_handle:
  print('<html><body>', file = index_handle)
  print('<h3>Topics</h3>', file = index_handle)
  print('<table>', file = index_handle)
  for d in sorted(filter(lambda x: '_' in x, os.listdir(root)), key = lambda x: int(x.split('_')[-1])):
    if d in table:
      topics_name = table[d]
    else:
      topics_name = d
    if os.path.exists(f'{root}/{d}/topics.html'):
      print(f'<tr><td>{topics_name}</td><td><a href="{d}/topics.html">Topics</a></td><td><a href="{d}/documents.html">Documents</a></td></tr>', file = index_handle)
      for titles_file in sys.argv[2:]:
        with open(titles_file) as tf_handle:
          titles = json.load(tf_handle)
        mapping = {titles[x]['full']: x for x in titles}
        with open(f'{root}/{d}/documents.html', 'w') as docs_handle:
          print(f'<html><body><p><a href="../index.html">Home</a></p><h3>All documents in {d}</h3><ul>', file = docs_handle)
          for title in sorted(mapping.keys(), key = lambda x: x.translate(str.maketrans('','',string.punctuation))):
            print(f'<li><a href="{d}/figures/pp_{mapping[title]}.svg">[{topics_name}] {title}</a></li>', file = docs_handle)
          print('</ul></body></html>', file = docs_handle)
  print('</table>', file = index_handle)
  print('</body></html>', file = index_handle)

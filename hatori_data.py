#!/usr/bin/env python3
 
import re
import sys
import os
import json
from glob import glob
from argparse import ArgumentParser
from itertools import zip_longest

parser = ArgumentParser()
parser.add_argument('jsonl')
parser.add_argument('--text-dir', default = 'text/works')
parser.add_argument('--text-suffix', default = '.txt')
parser.add_argument('--strip-json', type = str)
parser.add_argument('--progress-interval', default = 100)
args = parser.parse_args()
 
if args.strip_json:
  stripped_f = open(args.strip_json, 'w')

written = set()
output = {}
with open(args.jsonl) as f:
  for count, line in enumerate(f):
    if count % args.progress_interval == 0: print(f'{len(written)}/{count}', file = sys.stderr)
    work = json.loads(line)
    text_paths = glob(f'{args.text_dir}/*@{work["id"]}*{args.text_suffix}')
    splits = []
    if len(text_paths) == 0:
      print(f'{args.text_dir}/*@{work["id"]}*{args.text_suffix} does not glob. Skipping.', file = sys.stderr)
      continue
    if len(text_paths) > 1:
      for x in text_paths:
        split = x[re.match(r'.*' + re.escape(f'@{work["id"]}'), x).end():-len(args.text_suffix)]
        split = re.fullmatch(r'_\d+-\d+', split)
        if split:
          splits.append(split[0][1:])
        else:
          print(f'Unexpected multiple hits: "{args.text_dir}/*@{work["id"]}*{args.text_suffix}" matches {len(text_paths)} files, not explained by splits. Skipping.', file = sys.stderr)
          break
      if len(splits) != len(text_paths): #this should only happen if we broke due to the else above
        continue
    if work['id'] in written:
      print(f'Re-encountered {work["id"]}. Skipping.', file = sys.stderr)
      continue
    #print('\n'.join([f'{work["id"]}:{x}' for x in splits]))
    #sys.exit(1)
    written.add(work['id'])
    for text_path, split in zip_longest(text_paths, splits):
      text = ''
      with open(text_path, 'rt') as f:
        text = re.sub('[\t\n\r]', ' ', f.read())

      year = 0
      if len(work['production']) != 0 and len(work['production'][0]['dates']) != 0:
        year = re.sub('\\D', '', work['production'][0]['dates'][0]['label'].strip())
        if len(year) == 0: year = 0

      short_title = re.sub('[^a-zA-Z0-9]+', ' ', work['title'])
      short_title = short_title[0:min(160, len(short_title))]

      authors = []
      if 'contributors' in work:
        for contributor in work['contributors']:
          if (not 'primary' in contributor) or not contributor['primary']:
            continue
          if 'agent' in contributor:
            authors.append(contributor['agent']['label'])
      author = '; '.join(authors)

      year = str(year)
      if(len(year) > 4): year = year[0:4]

      if not split:
        split = '0-' + len(text)
      out_text = f'{author}  "{short_title}" {split}  {work["id"]}\t{year}\t{text}'
      if year in output: output[year].append(out_text)
      else: output[year] = [out_text]

    if args.strip_json:
      print(line, file = stripped_f, end = '')

if args.strip_json: stripped_f.close()

#print results, ordered by year
for k in sorted(output.keys()):
  for v in output[k]:
    print(v)


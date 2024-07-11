#!/usr/bin/env python3
#Usage example:
#find clouds -type f -name '*_docs.svg' -o -name '*_subjects.svg' | grep -v '/pp_[^/]*.svg' | sed 's#.*#./svg_postproc.py & --doc-labels short_titles.json#' | nice parallel
import os
import sys
import json
import argparse
import xml.etree.ElementTree as ET

skipped_files = 0
skipped_links = 0

parser = argparse.ArgumentParser()
parser.add_argument('infiles', nargs = '+')
parser.add_argument('--doc-labels', default = 'data/corpora/example/normalized/short_titles.json')
args = parser.parse_args()

with open(args.doc_labels) as f:
  doc_labels = json.load(f)

WELLCOME='https://wellcomecollection.org/works/'
WELLCOME_SEARCH = 'https://wellcomecollection.org/search/works'
SVG_NAMESPACE = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG_NAMESPACE)
for file in args.infiles:
  tree = ET.parse(file)
  root = tree.getroot()
  root.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')

  #Happen to know that all text is directly below root
  for text in root.findall('./text', namespaces = {'': SVG_NAMESPACE}):
    if os.path.splitext(file)[0].endswith('_subjects'):
      query = f'{WELLCOME_SEARCH}?subjects.label=%22{text.text.title()}%22'
    elif os.path.splitext(file)[0].endswith('_docs'):
      if text.text in doc_labels:
        query = f'figures/pp_{doc_labels[text.text]}.svg'
      else:
        print(f'{text.text} not in short_titles.json, skipping link', file = sys.stderr)
        skipped_links += 1
        continue
    else:
      print(f'No action defined for file path matching {os.path.basename(file)}', file = sys.stderr)
      skipped_files += 1
      continue
        
    root.remove(text)
    ET.SubElement(root, 'a', {'xlink:href': query}).append(text)

  ET.ElementTree(root).write(os.path.dirname(file) + '/' + 'pp_' + os.path.basename(file))

  if skipped_links > 0:
    print('Skipped {skipped_links} links', file = sys.stderr)
  if skipped_files > 0:
    print('Skipped {skipped_files} files', file = sys.stderr)

#!/usr/bin/env python3
#Usage example:
#find processed_clouds -type f -name '*_docs.svg' -o -name '*_subjects.svg' | sed 's#.*#./svg_postproc.py &#' | nice parallel
import os
import sys
import json
import xml.etree.ElementTree as ET

skipped_files = 0
skipped_links = 0
with open('short_titles.json') as f:
  doc_labels = json.load(f)

WELLCOME='https://wellcomecollection.org/works/'
WELLCOME_SEARCH = 'https://wellcomecollection.org/search/works'
SVG_NAMESPACE = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG_NAMESPACE)
for file in sys.argv[1:]:
  tree = ET.parse(file)
  root = tree.getroot()
  root.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')

  #Happen to know that all text is directly below root
  for text in root.findall('./text', namespaces = {'': SVG_NAMESPACE}):
    if os.path.splitext(file)[0].endswith('_subjects'):
      query = f'{WELLCOME_SEARCH}?subjects.label=%22{text.text.title()}%22'
    elif os.path.splitext(file)[0].endswith('_docs'):
      if text.text in doc_labels:
        query = f'{WELLCOME}{doc_labels[text.text]}'
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

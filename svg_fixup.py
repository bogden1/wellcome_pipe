#!/usr/bin/env python3
#Usage example:
#find figures -type f -name '*.svg' | grep -v '/pp_[^/]*.svg' | sed 's#.*#./svg_fixup.py & --doc-labels titles.json#' | nice parallel
import os
import sys
import json
import argparse
import xml.etree.ElementTree as ET

skipped_files = 0
skipped_links = 0

parser = argparse.ArgumentParser()
parser.add_argument('infiles', nargs = '+')
parser.add_argument('--doc-labels', default = 'data/corpora/example/normalized/titles.json')
args = parser.parse_args()

with open(args.doc_labels) as f:
  doc_labels = json.load(f)

WELLCOME='https://wellcomecollection.org/works/'
SVG_NAMESPACE = 'http://www.w3.org/2000/svg'
XLINK_NAMESPACE = 'http://www.w3.org/1999/xlink'
ET.register_namespace('', SVG_NAMESPACE)
ET.register_namespace('xlink', XLINK_NAMESPACE)
for file in args.infiles:
  tree = ET.parse(file)

  #use more space
  root = tree.getroot()
  root.set('width', '100%')
  root.set('height', '100%')

  #links to topics
  for link in tree.findall('.//a[@xlink:href]', namespaces = {'': SVG_NAMESPACE, 'xlink': XLINK_NAMESPACE}):
    link.set('{http://www.w3.org/1999/xlink}href', link.get('{http://www.w3.org/1999/xlink}href')[6:])

  #link to doc
  title = tree.find('./g[@class="infolayer"]/g[@class="g-gtitle"]', namespaces = {'': SVG_NAMESPACE, 'xlink': XLINK_NAMESPACE})
  if title:
    children = list(title)
    if len(children) != 1:
      print(f'Too many title children in {file}', file = sys.stderr)
      sys.exit(1)
    text = children[0]
    if text.tag != f'{{{SVG_NAMESPACE}}}text': raise
    title.remove(text)
    ET.SubElement(title, 'a', {'xlink:href': f'{WELLCOME}/{text.text}'}).append(text)
    if text.text in doc_labels:
      text.text=f'{doc_labels[text.text]["full"]} ({text.text})'
    text.set('style', "font-family: 'Open Sans', verdana, arial, sans-serif; font-size: 10px; fill: rgb(42, 63, 95); opacity: 1; white-space: pre;")

  #smaller annotations -- commented out as I managed to get meta_bars to generate something sensible, but keeping for reference
  #for annotation in tree.findall('//text[@class="annotation-text"]', namespaces = {'': SVG_NAMESPACE, 'xlink': XLINK_NAMESPACE}):
  #  annotation.set('style', "font-family: 'Open Sans', verdana, arial, sans-serif; font-size: 8px; fill: rgb(0,0,0); fill-opacity: 1; white-space: pre; pointer-events: all;")
  #for annotation in tree.findall('//g[@class="annotation-text-g"]', namespaces = {'': SVG_NAMESPACE, 'xlink': XLINK_NAMESPACE}):
    #rot, x, y = annotation.get('transform')[7:-1].split(',')
    #annotation.set('transform', f'rotate(-90,{x},{y})')

  tree.write(os.path.dirname(file) + '/' + 'pp_' + os.path.basename(file))

  if skipped_links > 0:
    print('Skipped {skipped_links} links', file = sys.stderr)
  if skipped_files > 0:
    print('Skipped {skipped_files} files', file = sys.stderr)

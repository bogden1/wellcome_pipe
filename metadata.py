#!/usr/bin/env python3
#Given a tsv file generated from hatori_data.py (i.e. PREMALLET in the Makefile),
#generate json files with extra data from works.json. Relies on availability of
#a database -- see README.md for instructions about that.

import os
import sys
import json
import string
import argparse
from works_lookup import WorksLookup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

parser = argparse.ArgumentParser()
parser.add_argument('--pre-mallet')
parser.add_argument('--db', default = 'wellcome_works')
parser.add_argument('--table', default = 'works')
parser.add_argument('--data-col', default = 'col1')
parser.add_argument('--output-subjects', default = 'data/corpora/example/normalized/subjects.json')
parser.add_argument('--output-titles', default = 'data/corpora/example/normalized/titles.json')
parser.add_argument('--verbose', '-v', action = 'store_true')
args = parser.parse_args()
 
concept_map = {}
count = {
  'Invalid identifier':     0,
  'Missing in database':    0,
  'No subject(s)':          0,
  'No concept(s)':          0,
  'No id in concept':       0,
  'At least one concept':   0,
  'Concept id mismatch':    0,
  'Uniqued short titles': 0,
}
label_alternatives = {
  'ujjp8gyr': {
    "dover, thomas, 1660-1742. ancient physician's legacy to his country",
    "dover, thomas, 1660-1742. ancient physician's legacy",
  },
  'dwdd6326': {
    "newton, isaac, 1642-1727. sir isaac newton's tables for renewing and purchasing leases",
  },
  'q5xw52v5': {
    'thornton, robert john, 1768?-1837. philosophy of medicine',
    'thornton, robert john, 1768?-1837. facts decisive in favour of the cow-pock',
    'thornton, robert john, 1768?-1837. new illustration of the sexual system of carolus von linnaeus',
    "thornton, robert john, 1768?-1837. politician's creed",
  },
  'ky9qg5uy': {
    "pitt, rob., 1653-1713. craft and frauds of physick expos'd",
  },
  'khwrqugj': {
    'mead, richard, 1673-1754. short discourse concerning pestilential contagion',
  },
  'nsd3467c': {
    'hancocke, john, -1728. febrifugum magnum: or, common water the best cure for fevers, and probably for the plaque',
  },
  'ym73y5qz': {
    'hartley, david, 1705-1757. some reasons why the practice of inoculation ought to be introduced into the town of bury at present',
  },
  'w3y9ghkp': {
    'walpole, robert, earl of orford, 1676-1745. letter from a member of parliament to his friends in the country, concerning duties on wine and tobacco',
  },
  'qk7nyrtg': {
    'freke, john, 1688-1756. essay to shew the cause of electricity',
  },
  'd244qbuv': {
    "nollet, abbé (jean antoine), 1700-1770. lettres sur l'electricite",
  },
  'zhtn3jfs': {
    'smellie, william, 1697-1763. treatise on the theory and practice of midwifery',
  },
  'v4wvc22p': {
    'cadogan, william, 1711-1797. dissertation on the gout',
  },
  'yvh77xkv': {
    'osborn, william, 1736-1808. essays on the practice of midwifery',
  },
  'q5xw52v5': {
    'thornton, robert john, 1768?-1837. medical extracts',
    'thornton, robert john, 1768?-1837. philosophy of medicine',
    'thornton, robert john, 1768?-1837. facts decisive in favour of the cow-pock',
    'thornton, robert john, 1768?-1837. new illustration of the sexual system of carolus von linnaeus',
    "thornton, robert john, 1768?-1837. politician's creed",
  },
}
label_overrides = {
  'ujjp8gyr': 'dover, thomas, 1660-1742',
  'dwdd6326': 'newton, isaac, 1642-1727',
  'q5xw52v5': 'thornton, robert john, 1768?-1837',
  'ky9qg5uy': 'pitt, rob., 1653-1713',
  'khwrqugj': 'mead, richard, 1673-1754',
  'nsd3467c': 'hancocke, john, -1728',
  'ym73y5qz': 'hartley, david, 1705-1757',
  'w3y9ghkp': 'walpole, robert, earl of orford, 1676-1745',
  'qk7nyrtg': 'freke, john, 1688-1756',
  'd244qbuv': "nollet, abbé (jean antoine), 1700-1770. lettres sur l'électricité",
  'zhtn3jfs': 'smellie, william, 1697-1763',
  'v4wvc22p': 'cadogan, william, 1711-1797',
  'yvh77xkv': 'osborn, william, 1736-1808',
  'q5xw52v5': 'thornton, robert john, 1768?-1837',
}
assert set(label_alternatives.keys()) == set(label_overrides.keys())

lookup = WorksLookup(args.table, args.data_col, database = args.db)
output_dict = {}
title_dict = {}
short_title_dict = {}
stops = set(stopwords.words('english'))

with open(args.pre_mallet) as in_file:
  for line in in_file:
    #compute identifier for lookup
    identifier = line.split('\t', maxsplit = 1)[0] #get the first field (author, short title, identifier)
    identifier = identifier.split(' ')[-1] #hence this is the actual identifier
    if len(identifier) != 8:
      print(f'Skipping bad identifier: {identifier}', file = sys.stderr)
      count['Invalid identifier'] += 1
      continue

    #do the lookup
    data = lookup(identifier)
    if data is None:
      print(f'No entry for id "{identifier}" in {args.db}:{args.table}[{args.data_col}]', file = sys.stderr)
      count['Missing in database'] += 1
      continue

    #look up titles
    if 'title' in data and len(data['title']):
      if identifier in title_dict: raise
      if identifier in short_title_dict: raise
      title = data['title']
      words = list(filter(lambda x: not x.lower() in stops, word_tokenize(title.translate(str.maketrans('', '', string.punctuation)))))
      short_title = words.pop(0)
      while len(short_title) < 30 and len(words):
        short_title += ' ' + words.pop(0)
      if len(words):
        short_title += '...'
      title_dict[identifier] = {
        'full':  title,
      }
      #ensure unique short titles
      #TODO perhaps do this for full titles too
      if short_title in short_title_dict:
        short_title += '0'
        decrement = 1
        while short_title in short_title_dict:
          ext = int(short_title[-decrement:]) + 1
          if ext % 10 == 0:
            decrement += 1
          short_title = short_title[0:-decrement] + str(ext)
        print(f"Extended {identifier}'s already-seen short title {short_title[0:-decrement]} with {short_title[-decrement:]}", file = sys.stderr)
        count['Uniqued short titles'] += 1
      title_dict[identifier]['short'] = short_title
      short_title_dict[short_title] = identifier

    #find any subjects (or rather, concepts) in the resulting data
    subjects = []
    if 'subjects' in data and len(data['subjects']):
      assert isinstance(data['subjects'], list)
      for subject in data['subjects']:
        if 'concepts' in subject:
          assert isinstance(subject['concepts'], list)
          for concept in subject['concepts']:
            if not 'id' in concept:
              print(f'Missing id in concept for {identifier}', file = sys.stderr)
              count['No id in concept'] += 1
              continue
            c_id = concept['id']
            subjects.append(c_id)

            #get the label, apply a couple of heuristics to reduce clashes, check we don't contain tabs
            c_label = concept['label'].lower().strip()
            if c_label[-1] == '.': c_label = c_label[0:-1]
            if c_id in label_alternatives:
              if c_label in label_alternatives[c_id]:
                c_label = label_overrides[c_id]

            #Add label to concept map
            if c_id in concept_map:
              if concept_map[c_id] != c_label:
                print(f'Concept id mismatch: {c_id} had label "{concept_map[c_id]}" and now also has "{c_label}" (from {identifier})', file = sys.stderr)
                count['Concept id mismatch'] += 1
            else:
              concept_map[c_id] = c_label
    else:
      if args.verbose: print(f'No subject(s): {identifier}')
      count['No subject(s)'] += 1

      #Avoid double-counting with 'no concepts' by outputting the result now
      if identifier in output_dict: raise
      output_dict[identifier] = None
      continue

    if subjects: 
      count['At least one concept'] += 1
    else:
      if args.verbose: print(f'No concept(s): {identifier}')
      count['No concept(s)'] += 1

    #print result
    if identifier in output_dict: raise
    output_dict[identifier] = subjects

#create map for identifier to subject(s)
with open(args.output_subjects, 'w') as f:
  json.dump(output_dict, f, indent = 2)

#create map from concept id to label
with open(os.path.splitext(args.output_subjects)[0] + '_map.json', 'w') as f:
  json.dump(concept_map, f, indent = 2)

with open(args.output_titles, 'w') as f:
  json.dump(title_dict, f, indent = 2)

with open('short_' + args.output_titles, 'w') as f:
  json.dump(short_title_dict, f, indent = 2)

#dump some stats
for k, v in count.items():
  print(f'{k}:{" " * (20 - len(k))} {v:4d}')

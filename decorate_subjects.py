#!/usr/bin/env python3
#Given a tsv file generated from hatori_data.py (i.e. PREMALLET in the Makefile), generate a new tsv with extra data from works.json

import os
import sys
import json
import argparse
from works_lookup import WorksLookup

parser = argparse.ArgumentParser()
parser.add_argument('--pre-mallet')
parser.add_argument('--db', default = 'wellcome_works')
parser.add_argument('--table', default = 'works')
parser.add_argument('--data-col', default = 'col1')
parser.add_argument('--output', default = 'subjects.tsv')
parser.add_argument('--verbose', '-v', action = 'store_true')
args = parser.parse_args()
 
concept_map = {}
count = {
  'Invalid identifier':   0,
  'Missing in database':  0,
  'No subject(s)':        0,
  'No concept(s)':        0,
  'No id in concept':     0,
  'At least one concept': 0,
  'Concept id mismatch':  0,
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
with open(args.output, 'w') as out_file:
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
        print(identifier, file = out_file)
        continue

      if subjects: 
        count['At least one concept'] += 1
      else:
        if args.verbose: print(f'No concept(s): {identifier}')
        count['No concept(s)'] += 1

      #print result
      print(identifier, '\t'.join(subjects), sep = '\t', file = out_file)

#create map from concept id to label
path, ext = os.path.splitext(args.output)
with open(os.path.basename(path) + '_map.json', 'w') as f:
  print(json.dumps(concept_map, indent = 2), file = f)

#dump some stats
for k, v in count.items():
  print(f'{k}:{" " * (20 - len(k))} {v:4d}')

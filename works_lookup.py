#!/usr/bin/env python3

import ast
import psycopg2

class WorksLookup:
  def __init__(self, table, data_col, **db_args):
    self.table = table
    self.data_col = data_col
    self.verbose = False
    self.conn = psycopg2.connect(**db_args)

  def raw_json_lookup(self, identifier):
    cur = self.conn.cursor()
    if self.verbose:
      print(f"select {self.data_col} from {self.table} where id='{identifier}'")
    cur.execute(f"select {self.data_col} from {self.table} where id='{identifier}'") #postgres wants single-quoted identifier
    rows = cur.fetchall()
    if len(rows) == 0:
      return None
    elif len(rows) > 1: raise #I expect we could get more efficient by grabbing more than one row at a time
    if len(rows[0]) != 1: raise
    return ast.literal_eval(rows[0][0])

  def field_lookup(self, identifier, field, single = True):
    cmd = f"select {field} from {self.table} where id='{identifier}'"
    if self.verbose:
      print(cmd)
    cur = self.conn.cursor()
    cur.execute(cmd)
    results = cur.fetchall() #list of tuples. each list element is a row in the results
    if single:
      if len(results) != 1 or len(results[0]) != 1:
        return None
      else:
        return results[0][0]
    return results

  def cooked_json_lookup(self, identifier, field, jsonpath, single = True):
    cmd = f"select jsonb_path_query({field}, '{jsonpath}') from {self.table} where id='{identifier}'"
    if self.verbose:
      print(cmd)
    cur = self.conn.cursor()
    cur.execute(cmd)
    results = cur.fetchall() #list of tuples. each list element is a row in the results
    if single:
      if len(results) != 1 or len(results[0]) != 1:
        return None
      else:
        return results[0][0]
    return results


if __name__ == '__main__':
  import os
  import sys
  import json
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument('identifiers', nargs = '+', help = 'Identifiers to look up')
  parser.add_argument('--db', default = 'wellcome_works', help = 'Name of the database')
  parser.add_argument('--table', default = 'works', help = 'Table containing works.json data')
  parser.add_argument('--data-col', default = 'col1', help = 'Column containing the data')
  parser.add_argument('--verbose', '-v', action = 'store_true', help = 'Show queries')
  parser.add_argument('--out-dir', '-o', help = 'If set, create this directory if it does not exist, and dump all results as JSON files in this directory. If not set, results are dumped to STDOUT instead.')
  args = parser.parse_args()

  lookup = WorksLookup(args.table, args.data_col, database = args.db)
  lookup.verbose = args.verbose
  if args.out_dir:
    if not os.path.isdir(args.out_dir):
      os.mkdir(args.out_dir)
  for identifier in args.identifiers:
    result = lookup(identifier)
    if result == None:
      print(f'No result for identifier {identifier}', file = sys.stderr)
      continue
    if args.out_dir:
      with open(f'{args.out_dir}/{identifier}.json', 'w') as f:
        print(json.dumps(result, indent = 2), file = f)
    else:
      if len(args.identifiers) > 1: print('\033[1m' + identifier + '\033[0;0m')
      print(json.dumps(result, indent = 2))
      if len(args.identifiers) > 1: print()

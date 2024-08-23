#!/usr/bin/env python3

import sys
import psycopg2

class WorksInsert:
  def __init__(self, table, verbose, **db_args):
    self.table = table
    self.verbose = verbose
    self.conn = psycopg2.connect(**db_args)
    self.conn.autocommit = True

  def create(self):
    cur = self.conn.cursor()
    cur.execute(f'drop table {self.table}')
    cur.execute(f'create table {self.table} (succeededBy JSONB, production JSONB, subjects JSONB, description VARCHAR, items JSONB, designation JSONB, workType JSONB, identifiers JSONB, thumbnail JSONB, formerFrequency JSONB, alternativeTitles JSONB, id CHAR(8) PRIMARY KEY, languages JSONB, precededBy JSONB, partOf JSONB, genres JSONB, notes JSONB, holdings JSONB, title VARCHAR, type VARCHAR, contributors JSONB, images JSONB, availabilities JSONB, parts JSONB)')
    #DANGER: when we insert using json_populate_record, if the json contains any extra fields then they will just be silently dropped.
    #See https://www.postgresql.org/docs/current/functions-json.html (search for "json_populate_record")

  def __call__(self, json_line):
    cur = self.conn.cursor()
    #dollar-quoting to avoid escape problems
    #the null bit means we'll insert nulls where there are missing values
    cmd = f'insert into {self.table} select * from json_populate_record(null::{self.table},$BernardsUnlikelyTag${json_line}$BernardsUnlikelyTag$)'
    if self.verbose:
      print(cmd)
    try:
      cur.execute(cmd)
    except psycopg2.errors.UniqueViolation as e:
      print(e.pgerror, file = sys.stderr)

if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument('infile', help = 'JSONL file to insert')
  parser.add_argument('--db', default = 'wellcome_works', help = 'Name of the database')
  parser.add_argument('--table', default = 'j', help = 'Table containing works.json data')
  parser.add_argument('--verbose', '-v', action = 'store_true', help = 'Show queries')
  parser.add_argument('--force-create', action = 'store_true', help = 'Create table (DANGER, destroys it if it already exists')
  args = parser.parse_args()
  insert = WorksInsert(args.table, args.verbose, database = args.db)
  if args.force_create:
    insert.create()
  
  with open(args.infile) as f:
    for line in f:
      insert(line.rstrip('\r\n'))

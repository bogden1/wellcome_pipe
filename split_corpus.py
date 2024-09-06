#!/usr/bin/env python3

import os
import re
import sys
import shutil
import argparse

def chunk(in_doc, words, start = 0):
  end   = start + args.chunk
  doclen = len(words)
  while start < doclen:
    with open(f'{output_dir}/{in_doc[:-len(args.input_ext)]}_{start}-{end-1}{args.input_ext}', 'w') as f:
      print(' '.join(words[start:end]), file = f)
      start += args.chunk
      end   += args.chunk

def chunk_file(in_doc):
  with open(input_dir + '/' + in_doc) as f:
    words = f.read().split()
  chunk(in_doc, words)
  chunk(in_doc, words, int(args.chunk / 2))

parser = argparse.ArgumentParser()
parser.add_argument('corpus', help = 'Name of corpus', default = 'example')
parser.add_argument('--input-ext', help = 'Extension of files to be used as input', default = '.txt') #Follows the identifier so the default will not e.g. include .clean.txt
parser.add_argument('--corpus-dir', help = 'Directory where corpora live', default = os.path.dirname(sys.argv[0]) + '/data/corpora')
parser.add_argument('--split-ext', help = 'Extension to be applied in the new, split-up corpus', default = '_split')
parser.add_argument('--chunk', help = 'Number of words per chunk in the split corpus', default = 500)
parser.add_argument('--procs', type = int, help = 'Number of parallel processes to run', default = os.cpu_count())
args = parser.parse_args()

input_dir  = '/'.join([args.corpus_dir, args.corpus,                  'normalized', args.corpus])
output_dir = '/'.join([args.corpus_dir, args.corpus + args.split_ext, 'normalized', args.corpus + args.split_ext])
os.makedirs(output_dir)
shutil.copyfile(f'{input_dir}/../{args.corpus}.jsonl', f'{output_dir}/../{args.corpus}{args.split_ext}.jsonl')

from multiprocessing import Pool
Pool(args.procs).map(chunk_file, filter(lambda x: re.search(r'@[^\.]+' + re.escape(args.input_ext) + r'$', x), os.listdir(input_dir)))

print('Now run OCRNormalizer on')
print(os.path.abspath(output_dir))

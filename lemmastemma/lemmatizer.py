#!/usr/bin/env python3
#re https://spacy.io/usage/spacy-101#annotations-pos-deps
#python -m spacy download en_core_web_trf

import spacy
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('infiles', nargs = '*', type = str, help = 'File(s) to process')
parser.add_argument('--strip-entities', action = argparse.BooleanOptionalAction, default = False, help = 'Drop all named entities')
args = parser.parse_args()

spacy.require_gpu()
nlp = spacy.load("en_core_web_trf")
nlp.max_length = 3000000 #Alarmingly high -- may consume ~30GB of RAM!

for in_fnam in args.infiles:
  out_fnam = in_fnam + '.lemmatized'
  with open(in_fnam, encoding = 'utf-8') as f:
    doc = nlp(f.read())
  if(args.strip_entities):
    tokens = filter(lambda x: x.ent_type_ == '', doc)
  else:
    tokens = doc #bit ugly, but happens to work here
  lemmas = [x.lemma_ for x in tokens]
  with open(out_fnam, 'w', encoding = 'utf-8') as f:
    print(" ".join(lemmas).strip(), file = f)

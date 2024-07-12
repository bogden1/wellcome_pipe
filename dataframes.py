import os
import pandas as pd
import pickle
import argparse

def save(fnam, data):
  with open(fnam, 'wb') as f:
    pickle.dump(data, f)

def load(fnam, base = None):
  if args.force:
    return None
  if not base is None:
    if os.path.getmtime(base) > os.path.getmtime(fnam):
      return None
  if os.path.exists(fnam):
    with open(fnam, 'rb') as f:
      d = pickle.load(f)
    print(f'loaded {fnam}')
    return d
  else:
    return None

parser = argparse.ArgumentParser()
parser.add_argument('input')
parser.add_argument('--force', action = 'store_true')
args = parser.parse_args()

base_name, ext = os.path.splitext(args.input)
base_df_name   = base_name + '.df'
counts_df_name = base_name + '_counts.df'
sums_df_name   = base_name + '_sums.df'
freq_df_name   = base_name + '_freqs.df'
freq_csv_name  = base_name + '_freqs.csv'

base_df = load(base_df_name, base_name + ext)
if base_df is None:
  print(f'constructing {base_df_name}')
  base_df = pd.read_csv(base_name + ext, sep = ' ', names = ('doc', 'source', 'pos', 'typeindex', 'type', 'topic'), skiprows = 3)
  save(base_df_name, base_df)

#count of each unique word in topic
#e.g. at time of writing, with base of 17xx_lemmatized_sorted-topic_state_10
#counts_df.xs('elixir', level = 'type') should return:
#topic      
#4      1944
#7        21
#9      4917
counts_df = load(counts_df_name, base_name + ext)
if counts_df is None:
  print(f'constructing {counts_df_name}')
  assert base_df['doc'].isna().sum() == 0
  counts_df = base_df[['doc', 'topic', 'type']].groupby(['topic', 'type']).count() #we only need one column (of non-NA values) to do the count
  save(counts_df_name, counts_df)

#Total words in topic (counting duplicates e.g. if "elixir" appears 1944 times, all 1944 will be counted)
#e.g. at time of writing, topic 4 is 24359667; topic 7 is 9549174 and topic 9 is 9010839
sums_df = load(sums_df_name, base_name + ext)
if sums_df is None:
  print(f'constructing {sums_df_name}')
  assert base_df['doc'].isna().sum() == 0
  sums_df = base_df[['doc', 'topic']].groupby('topic').count() #we only need one column (of non-NA values) to do the count
  save(sums_df_name, sums_df)

#Frequencies of words in topic
#Calculated with a calculator for elixir:
#topic
#4     0.000079804
#7     0.000002199
#9     0.000545676
#To the 6 decimal places I get from Pandas view:
#topic
#4     0.000080
#7     0.000002
#9     0.000546
freq_df = load(freq_df_name, base_name + ext)
if freq_df is None:
  print(f'constructing {freq_df_name}')
  freq_df = counts_df.div(sums_df, level = 'topic', axis = 0)
  save(freq_df_name, freq_df)
  
freq_df.to_csv(freq_csv_name)

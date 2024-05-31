#!/usr/bin/env python3
 
import re
import sys
import os
import requests
import json
import time
 
def keys_matching(key, d):
  results = []
  for k, v in d.items():
    if isinstance(v, dict):
      assert k != key, k
      results += keys_matching(key, v)
    elif isinstance(v, list):
      assert k != key, k
      for x in v:
        if isinstance(x, dict):
          results += keys_matching(key, x)
    elif k == key:
      results.append(v)
  return results
 
for snapshot in os.listdir('data/inputs'):
  seen = set()
  input_name = os.path.splitext(snapshot)[0]
  log_out_path = f'./data/log/{input_name}'; os.makedirs(log_out_path, exist_ok = True)
  with open(f'{log_out_path}/log.txt', 'w') as log:
    print(input_name)
    input_path = f'./data/inputs/{snapshot}' #jsonl
    json_out_path = f'./data/json/{input_name}'; os.makedirs(json_out_path, exist_ok = True)
    text_out_path = f'./data/text/{input_name}'; os.makedirs(text_out_path, exist_ok = True)
 
    with open(input_path) as f:
      for count, line in enumerate(f):
        #print(f'{count} {line}')
        work = json.loads(line)

        #My inputs seem to have multiple of the same work sometimes
        if work['id'] in seen:
          print(f'REPEAT ID: {count} {line}', file = log)
          continue
        seen.add(work['id'])
 
        urls = list(filter(lambda x: '/presentation/' in x, keys_matching('url', work)))
        if(len(urls) == 0):
          print(f'NO URL: {count} {line}', file = log)
          continue
 
        print(f"  {work['title']}")
        try:
          if len(work['production']) == 0:
            short_name = '0000@'
          elif len(work['production'][0]['dates']) == 0:
            short_name = '0000@'
          else:
            short_name = work['production'][0]['dates'][0]['label'] + '@'
          short_name += '_'.join(work['title'].split()[0:min(7, len(work['title']))])
          short_name = re.sub('^\D*', '', re.sub('[^a-zA-Z0-9_@?\-]', '%', short_name))
          print(f"  {short_name} ({work['id']})")
 
          for url in urls:
            print('  ' + url)
            response = requests.get(url)
            url_json = response.json()
 
            with open(f"{json_out_path}/{work['id']}.json", 'w') as f:
              json.dump(url_json, f, indent=2, sort_keys=True)
            if 'sequences' in url_json:
              seqs = url_json['sequences']
              assert len(seqs) == 1
              if 'rendering' in seqs[0]:
                rendering = seqs[0]['rendering']
                if not isinstance(rendering, list):
                  rendering = [rendering]
                for r in rendering:
                  if r['format'][0:4] == 'text':
                    with open(f"{text_out_path}/{short_name}@{work['id']}.txt", 'w') as f:
                      print('  ' + re.sub(r'\\x\w*', '', requests.get(r['@id']).text), file = f)
        except Exception as e:
          print(f'  {count}: ' + str(e) + ': ' + str(e.__traceback__))
          print(f'  {count}: ' + str(e) + ': ' + str(e.__traceback__), file = sys.stderr)
        print()
        time.sleep(0.5)

    print(f'Finished {input_name}')

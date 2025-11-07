# section, title, subsecton is string arr: 15, 12, 11, 9, 8, 7, 2_2, 2_1, 1_2, 1_1
# section, title, content: 6_1, 5_1, 4_1
# section, title, subsecton is string obj: 3

pattern_01 = ['15', '12', '11', '9', '8', '7', '2_2', '2_1', '1_2', '1_1']
pattern_02 = ['6_1', '5_1', '4_1']
pattern_03 = ['3']

import math
import os
import json
import re
from tokenize import group

folder = 'HoidapquychebachkhoahanoiData'

chunks = []

def group_list_01(lst, threshold):
  res = []
  
  for item in lst:
    if len(res) == 0 or res[-1] >= threshold:
      res.append(item)
    else:
      res[-1] += item

  return res

def group_list_02(lst, threshold):
  res = []
  
  for item in lst:
    if len(res) == 0 or res[-1] <= threshold:
      res.append(item)
    else:
      res[-1] += item

  return res

def group_list_03(lst, threshold):
  res = []
  
  for item in lst:
    if len(res) == 0 or res[-1] + item > threshold:
      res.append(item)
    else:
      res[-1] += item
  return res

def group_chunk(chunks, grouped_lens):
  result = []
  current = []
  idx = 0
  target = grouped_lens[idx]
  for chunk in chunks:
    temp_str = ''
    for i in current:
      temp_str += i['content']
    if len(temp_str) >= target:
      result.append(current)
      current = []
      idx += 1
      if idx < len(grouped_lens):
        target = grouped_lens[idx]
      else:
        break
    current.append(chunk)
  if len(current) > 0:
    result.append(current)

  final_length = 0
  for group in result:
    for item in group:
      final_length += len(item['content'])
  print(final_length, sum(grouped_lens))

  # To text
  final_contents = []
  for group in result:
    content = ''
    current_title = ''
    for item in group:
      if item['title'] != current_title:
        current_title = item['title']
        content += current_title + '\n'
      content += item['content'] + '\n'
    final_contents.append(content)
  print(len(final_contents), [len(item) for item in final_contents])
  return final_contents

max_length = 0
for filename in pattern_02:
  json_path = folder + '/' + filename + '.json'
  with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    for item in data['sections']:
      max_length = max(max_length, len(item['content']))

min_accept_length = 600
max_accept_length = 2500

def check_ok(lst):
  for item in lst:
    if item < min_accept_length or item > max_accept_length:
      return False
  return True

for filename in pattern_01:
  json_path = folder + '/' + filename + '.json'
  with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    section_chunks = []
    splitted_section_chunks = []
    for item in data['sections']:
      length = 0
      for subsection in item['subsections']:
        length += len(subsection)
        section_chunks.append({
          'title': item['title'],
          'content': subsection
        })
    lens = []
    for chunk in section_chunks:
      subsection = chunk['content']
      if len(chunk['content']) > 2000:
        title_match = re.search(r"^(Điều\s*\d+\.\s*[^\n]+)", subsection)
        title = title_match.group(1).strip() if title_match else ''
        pattern = r"(?<=\n)(\d+\..*?)(?=\n\d+\.|\Z)"
        matches = re.findall(pattern, subsection, flags=re.S)
        for match in matches:
          lens.append(len(match))
          splitted_section_chunks.append({
            'title': chunk['title'] + '\n' + title,
            'content': match
          })
      else: 
        lens.append(len(subsection))
        splitted_section_chunks.append(chunk)
    print(filename)
    for threshold in range(0, 10000, 50):
      grouped_01 = group_list_01(lens, threshold)
      grouped_02 = group_list_02(lens, threshold)
      grouped_03 = group_list_03(lens, threshold)
      if check_ok(grouped_01):
        grouped_chunks = group_chunk(splitted_section_chunks, grouped_01)
        chunks.extend([{ 'file': data['name'], 'content': item } for item in grouped_chunks])
        break
      elif check_ok(grouped_02):
        grouped_chunks = group_chunk(splitted_section_chunks, grouped_02)
        chunks.extend([{ 'file': data['name'], 'content': item } for item in grouped_chunks])
        break
      elif check_ok(grouped_03):
        grouped_chunks = group_chunk(splitted_section_chunks, grouped_03)
        chunks.extend([{ 'file': data['name'], 'content': item } for item in grouped_chunks])
        break
      if threshold == 10000:
        print('Cannot chunk:', filename,lens)

print(len(chunks))
with open('chunks.json', 'w', encoding='utf-8') as f:
  json.dump(chunks, f, ensure_ascii=False, indent=2)

print(max_length)
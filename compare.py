import os
import json

correct_avg_count = 0
correct_max_count = 0
correct_llm_count = 0
question_count = 0
with open('process_data.json', 'r', encoding='utf-8') as f:
  data = json.load(f)
  
  for item in data:
    truth_answer = item['truth_answer']
    system_answer_avg = item['system_answer_avg']
    system_answer_max = item['system_answer_max']
    system_answer_llm = item['system_answer_llm']

    if system_answer_avg == truth_answer:
      correct_avg_count += 1
    if system_answer_max == truth_answer:
      correct_max_count += 1
    if system_answer_llm == truth_answer:
      correct_llm_count += 1
    question_count += 1

  print(f'Correct avg count: {correct_avg_count}')
  print(f'Correct max count: {correct_max_count}')
  print(f'Correct llm count: {correct_llm_count}')
  print(f'Question count: {question_count}')
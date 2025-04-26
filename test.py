#!/usr/bin/python
import json

with open('data/students/Commerce/quizU1_a.json', 'r', encoding='utf-8') as f:
    data = json.loads(f.read())
    for i in range(100):
        with open(f'data/students/Commerce/quizU1_{i}.json', 'w', encoding='utf-8') as g:
            json.dump(data, g)
            print(i)
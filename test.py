#!/usr/bin/python
import json

with open('data/quizs/quizU1.json', 'r') as f:
    questions = json.loads(f.read())
    print(questions)
    print(questions.keys())
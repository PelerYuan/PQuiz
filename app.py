from flask import Flask, render_template, redirect, request, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    if 'class' in session:
        tests = []
        for quiz_name in os.listdir('data/quizs'):
            with open(f'data/quizs/{quiz_name}', 'r', encoding='utf-8') as f:
                quiz = json.loads(f.read())
                tests.append({'name':quiz_name[:-5], 'title': quiz['title'], 'subtitle': quiz['subtitle']})
        return render_template('index.html', user_name=session['name'], tests=tests)

    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        class_ = request.form['class']
        name = request.form['name']
        if class_ != 'not select':
            session['class'] = class_
            session['name'] = name
            return redirect(url_for('index'))

    classes = os.listdir('data/students/')
    return render_template('login.html', classes=classes)


@app.route('/quiz/<quiz_name>')
def quiz(quiz_name):
    """
    Quiz display
    """
    with open(f'data/quizs/{quiz_name}.json', 'r', encoding='utf-8') as f:
        quiz = json.loads(f.read())
        for i in range(len(quiz['questions'])):
            question = quiz['questions'][i]['index'] = i + 1

    return render_template('quiz.html', quiz=quiz)


@app.route('/submit', methods=['POST'])
def correct():
    """
    Check correct answer
    """
    print(request.form)


@app.route('/test')
def test():
    return render_template('test.html')


if __name__ == '__main__':
    app.run()

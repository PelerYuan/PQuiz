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
        return render_template('index.html', class_=session['class'],name=session['name'], tests=tests)

    return redirect(url_for('login'))

def is_tested(quiz_name):
    print(f"data/students/{session['class']}/{quiz_name}_{session['name']}.json")
    return os.path.exists(f"data/students/{session['class']}/{quiz_name}_{session['name']}.json")
app.jinja_env.globals['is_tested'] = is_tested


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
            quiz['questions'][i]['index'] = i + 1

    return render_template('quiz.html', quiz=quiz, quiz_name=quiz_name)


@app.route('/submit/<quiz_name>', methods=['POST'])
def submit(quiz_name):
    """
    Record submit
    """
    selection = {}
    for key in request.form.keys():
        selection[int(key)] = request.form.getlist(key)

    with open(f"data/students/{session['class']}/{quiz_name}_{session['name']}.json", 'w', encoding='utf-8') as f:
        json.dump(selection, f, ensure_ascii=False, indent=4)
    return "Hello"

@app.route('/review/<quiz_name>')
def review(quiz_name):
    with open(f'data/quizs/{quiz_name}.json', 'r', encoding='utf-8') as f:
        quiz = json.loads(f.read())
        for i in range(len(quiz['questions'])):
            quiz['questions'][i]['index'] = i + 1
    with open(f"data/students/{session['class']}/{quiz_name}_{session['name']}.json", 'r', encoding='utf-8') as f:
        answer = json.loads(f.read())
    return render_template('review.html', quiz=quiz, answer=answer)


@app.route('/test')
def test():
    return render_template('test.html')


if __name__ == '__main__':
    app.run()

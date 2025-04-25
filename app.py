from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route('/')
def quiz():
    """
    Quiz display
    """
    with open('./data/quizU1.json', 'r') as f:
        quiz = json.loads(f.read())
        for i in range(len(quiz['questions'])):
            question = quiz['questions'][i]['index'] = i+1

    return render_template('quiz.html', quiz=quiz)

@app.route('/submit', methods=['POST'])
def correct():
    """
    Check correct answer
    """
    print(request.form)


if __name__ == '__main__':
    app.run()

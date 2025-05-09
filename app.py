from flask import Flask, render_template, redirect, request, url_for, session, send_from_directory, jsonify, send_file
import json
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True


# Read configure
with open('configure.json', 'r') as f:
    config = json.load(f)
    for school in os.listdir("data/students"):
        if config['admin password'].get(school, None) is None:
            raise Exception(f"{school} admin password is missing, please set it in configure.json")
@app.route('/')
def index():
    if session.get('name', 'admin') != 'admin':
        tests = []
        for quiz_name in os.listdir('data/quizs'):
            with open(f'data/quizs/{quiz_name}', 'r', encoding='utf-8') as f:
                quiz = json.loads(f.read())
                if quiz.get('close', '') != 'true':
                    tests.append({'name': quiz_name[:-5], 'title': quiz['title'], 'subtitle': quiz['subtitle']})
        return render_template('index.html', class_=session['class'], name=session['name'], tests=tests)

    return redirect(url_for('login'))


def is_tested(quiz_name):
    return os.path.exists(f"data/students/{session['school']}/{session['class']}/{quiz_name}_{session['name']}.json")


app.jinja_env.globals['is_tested'] = is_tested


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        class_ = request.form['class']
        name = request.form['name']
        school = request.form['school']
        if name != 'admin':
            if class_ != 'not select':
                session['class'] = class_
                session['name'] = name
                session['school'] = school
                return redirect(url_for('index'))
        else:
            return redirect(url_for('admin_login'))

    school_class = {}
    for school in os.listdir('data/students'):
        school_class[school] = os.listdir(f'data/students/{school}')
    return render_template('login.html', school_class=school_class)


@app.route('/logout')
def logout():
    session.pop('class', None)
    session.pop('name', None)
    return redirect(url_for('login'))


@app.route('/quiz/<quiz_name>')
def quiz(quiz_name):
    if session.get('name', 'admin') != 'admin':
        with open(f'data/quizs/{quiz_name}.json', 'r', encoding='utf-8') as f:
            quiz = json.loads(f.read())
            for i in range(len(quiz['questions'])):
                quiz['questions'][i]['index'] = (i + 1)
        return render_template('quiz.html', quiz=quiz, quiz_name=quiz_name)
    return redirect(url_for('login'))


@app.route('/submit/<quiz_name>', methods=['GET', 'POST'])
def submit(quiz_name):
    if session.get('name', 'admin') != 'admin':
        if request.method == 'POST':
            selection = {}
            for key in request.form.keys():
                selection[key] = request.form.getlist(key)

            with open(f'data/quizs/{quiz_name}.json', 'r', encoding='utf-8') as f:
                quiz = json.loads(f.read())
                quiz['points'] = float(quiz['points'])
                for i in range(len(quiz['questions'])):
                    quiz['questions'][i]['index'] = str(i + 1)

            score = quiz['points']
            total_score = 0
            question_count = 0
            for question in quiz['questions']:
                if 'options' in question.keys():
                    question_count += 1
                    if selection.get(question['index'], False):
                        selection[question['index']].append(0)  # last one to be the score
                        for option in question['options']:
                            print(option.get('correct', ''))
                            if option['opt'] == selection[question['index']][0] and option.get('correct', '') == 'true':
                                selection[question['index']][-1] = score
                                total_score += score
                                break
                    else:
                        selection[question['index']] = [0]

                elif 'multioptions' in question.keys():
                    question_count += 1
                    if selection.get(question['index'], False):
                        selection[question['index']].append(0)
                        question_count = len(question['multioptions'])
                        for option in question['multioptions']:
                            print(option.get('correct', ''))
                            print(option['opt'])
                            print(selection[question['index']])
                            if option['opt'] in selection[question['index']]:
                                if option.get('correct', '') == 'true':
                                    selection[question['index']][-1] += score / question_count
                                else:
                                    selection[question['index']][-1] -= score / question_count
                        if selection[question['index']][-1] < 0:
                            selection[question['index']][-1] = 0
                        total_score += selection[question['index']][-1]
                    else:
                        selection[question['index']] = [0]

                elif 'itext' in question.keys():
                    if selection.get(question['index'], False):
                        selection[question['index']].append(-404)
                    else:
                        selection[question['index']] = [-404]

                selection['score'] = str(total_score)
                selection['total_score'] = str(score * question_count)  # Ignore itext

            with open(f"data/students/{session['school']}/{session['class']}/{quiz_name}_{session['name']}.json", 'w',
                      encoding='utf-8') as f:
                json.dump(selection, f, ensure_ascii=False, indent=4)

            return render_template('finish.html', score=f"{total_score} / {score * question_count}")
        else:
            return redirect(url_for('index'))
    return redirect(url_for('login'))


@app.route('/review/<quiz_name>')
def review(quiz_name):
    if session.get('name', 'admin') != 'admin':
        with open(f'data/quizs/{quiz_name}.json', 'r', encoding='utf-8') as f:
            quiz = json.loads(f.read())
            for i in range(len(quiz['questions'])):
                quiz['questions'][i]['index'] = str(i + 1)
        with open(f"data/students/{session['school']}/{session['class']}/{quiz_name}_{session['name']}.json", 'r',
                  encoding='utf-8') as f:
            answer = json.loads(f.read())
        return render_template('review.html', quiz=quiz, answer=answer)
    return redirect(url_for('login'))


def is_answered(answer):
    return len(answer) > 1


app.jinja_env.globals['is_answered'] = is_answered


# @app.route('/test')
# def test():
#     return render_template('test.html')


@app.route('/img/<folder>/<filename>')
def img(folder, filename):
    return send_from_directory(folder, filename)


# admin function
@app.route('/admin')
def admin():
    if session.get('name') == 'admin':
        tests = []
        for quiz_name in os.listdir('data/quizs'):
            with open(f'data/quizs/{quiz_name}', 'r', encoding='utf-8') as f:
                quiz = json.loads(f.read())
                tests.append({'name': quiz_name[:-5], 'title': quiz['title'], 'subtitle': quiz['subtitle']})
        is_super = session['school'] == 'High School Affiliated to Nanjing Normal University'
        return render_template('admin/admin.html', tests=tests, is_super=is_super)
    return redirect(url_for('admin_login'))


@app.route('/close/<quiz_name>')
def close(quiz_name):
    if session.get('name') == 'admin':
        with open(f'data/quizs/{quiz_name}.json', 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
            data['close'] = 'true'
        with open(f'data/quizs/{quiz_name}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return redirect(url_for('admin'))
    return redirect(url_for('admin_login'))


@app.route('/open/<quiz_name>')
def open_(quiz_name):
    if session.get('name') == 'admin':
        with open(f'data/quizs/{quiz_name}.json', 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
            data['close'] = 'false'
        with open(f'data/quizs/{quiz_name}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return redirect(url_for('admin'))
    return redirect(url_for('admin_login'))


def is_closed(quiz_name):
    with open(f'data/quizs/{quiz_name}.json', 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
        return data.get('close', '') == 'true'


app.jinja_env.globals['is_closed'] = is_closed


@app.route('/delete/<quiz_name>')
def delete(quiz_name):
    if session.get('name') == 'admin':
        os.remove(f'data/quizs/{quiz_name}.json')
        return redirect(url_for('admin'))
    return redirect(url_for('admin_login'))


@app.route('/edit/<quiz_name>')
def edit(quiz_name):
    if session.get('name') == 'admin':
        if os.path.exists(f'data/quizs/{quiz_name}.json'):
            with open(f'data/quizs/{quiz_name}.json', 'r', encoding='utf-8') as f:
                return render_template('admin/edit.html', quiz_name=quiz_name, content=f.read())
        else:
            return render_template('admin/edit.html', quiz_name=quiz_name, content="")
    return redirect(url_for('admin_login'))


# 保存 JSON 数据的接口
@app.route('/save/<quiz_name>', methods=['POST'])
def save(quiz_name):
    if session.get('name') == 'admin':
        try:
            # 获取前端发送的 JSON 数据
            json_data = request.get_json()

            # 将 JSON 数据保存到文件
            with open(f'data/quizs/{quiz_name}.json', 'w') as f:
                json.dump(json_data, f, indent=4)

            # 返回成功响应
            return jsonify({"message": "JSON saved successfully!"}), 200
        except Exception as e:
            # 返回错误响应
            return jsonify({"error": str(e)}), 400
    return redirect(url_for('admin_login'))


@app.route('/update_quiz_name/<current_name>', methods=['POST'])
def update_quiz_name(current_name):
    new_name = request.get_json().get('newName')

    if not new_name:
        return jsonify({"error": "New name cannot be empty"}), 400

    with open(f'data/quizs/{current_name}.json', 'r') as f:
        data = json.loads(f.read())
    with open(f'data/quizs/{new_name}.json', 'w') as f:
        json.dump(data, f, indent=4)
    os.remove(f'data/quizs/{current_name}.json')

    return jsonify({"message": "Quiz name updated successfully", "newName": new_name}), 200


@app.route('/trial/<quiz_name>')
def trial(quiz_name):
    if session.get('name') == 'admin':
        with open(f'data/quizs/{quiz_name}.json', 'r', encoding='utf-8') as f:
            quiz = json.loads(f.read())
            for i in range(len(quiz['questions'])):
                quiz['questions'][i]['index'] = (i + 1)
        return render_template('admin/trial.html', quiz=quiz, quiz_name=quiz_name)
    return redirect(url_for('admin_login'))


@app.route('/result/<quiz_name>')
def result(quiz_name):
    if session.get('name') == 'admin':
        classes = os.listdir(f"data/students/{session['school']}")
        return render_template('admin/result.html', quiz_name=quiz_name, class_name="None", classes=classes,
                               students="None")
    return redirect(url_for('admin_login'))


@app.route('/result/<quiz_name>/<class_name>')
def result_class(quiz_name, class_name):
    if session.get('name') == 'admin':
        students = {}
        for filename in os.listdir(f"data/students/{session['school']}/{class_name}"):
            quiz, student = filename[:-5].split('_')
            if quiz_name == quiz:
                with open(f"data/students/{session['school']}/{class_name}/{quiz_name}_{student}.json", 'r',
                          encoding='utf-8') as f:
                    data = json.loads(f.read())
                    students[student] = f"{data['score']} / {data['total_score']}"
        classes = os.listdir(f"data/students/{session['school']}")
        return render_template('admin/result.html', quiz_name=quiz_name, class_name=class_name, classes=classes,
                               students=students)
    return redirect(url_for('admin_login'))


@app.route('/review/<quiz_name>/<class_name>/<student_name>')
def review_admin(quiz_name, class_name, student_name):
    if session.get('name') == 'admin':
        with open(f'data/quizs/{quiz_name}.json', 'r', encoding='utf-8') as f:
            quiz = json.loads(f.read())
            for i in range(len(quiz['questions'])):
                quiz['questions'][i]['index'] = str(i + 1)
        with open(f"data/students/{session['school']}/{class_name}/{quiz_name}_{student_name}.json", 'r',
                  encoding='utf-8') as f:
            answer = json.loads(f.read())
        return render_template('review.html', quiz=quiz, answer=answer)
    return redirect(url_for('admin_login'))


@app.route('/excel/<quiz_name>/<class_name>')
def excel(quiz_name, class_name):
    if session.get('name') == 'admin':
        output = {
            "student_name": [],
            "score": [],
            "total_score": [],
            "percentage": []
        }
        for filename in os.listdir(f"data/students/{session['school']}/{class_name}"):
            quiz, student = filename[:-5].split('_')
            if quiz_name == quiz:
                with open(f"data/students/{session['school']}/{class_name}/{quiz_name}_{student}.json", 'r',
                          encoding='utf-8') as f:
                    data = json.loads(f.read())
                    output['student_name'].append(student)
                    output['score'].append(float(data['score']))
                    output['total_score'].append(float(data['total_score']))
                    output['percentage'].append(float(data['score']) / float(data['total_score']))
        # 创建DataFrame
        df = pd.DataFrame(output)
        # 将DataFrame写入Excel文件
        df.to_excel(f'tmp/{quiz_name}_{class_name}.xlsx', index=False)
        return send_file(f'tmp/{quiz_name}_{class_name}.xlsx', as_attachment=True)
    return redirect(url_for('admin_login'))


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        school = request.form['school']
        password = request.form['password']
        if school != 'not select':
            if password == config['admin password'][school]:
                session['class'] = 'admin'
                session['name'] = 'admin'
                session['school'] = school
                return redirect(url_for('admin'))
    schools = os.listdir(f"data/students/")
    return render_template('admin/login.html', schools=schools)


if __name__ == '__main__':
    app.run()

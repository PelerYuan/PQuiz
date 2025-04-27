# PQuiz

Quickly create online quizzes with PQuiz

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Configuration](#configuration)

## Features

### For students:

- Login with their class and name
- Take different quizzes
- Review the quizzes that have been done

### For teacher/admin:

- Create quizzes by Json file, edit and verify
- View the detailed result of every student
- Download statistics in Excel form

## Installation

Step-by-step instructions on how to set up the project locally.

```bash
# Clone the repository
git clone https://github.com/PelerYuan/PQuiz

# Navigate into the project directory
cd repo

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows
venv\Scripts\activate
# Linux & Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the web server
python app.py
```

## Usage

### For students:

Login with their class and name:

![student login page](doc/1.png)

See all the quizzes in Homepage:

![Student Homepage](doc/2.png)

Take a quiz:

![Take a quiz](doc/3.png)

Review a quiz:

![Review a quiz](doc/4.png)

### For teacher/admin

Login the admin account by simply put `admin` as the name, then input the password `ajajaj`:

![Login as admin](doc/5.png)

Manage all the quizzes here:

![Manage quizzes](doc/6.png)

Edit Json file:

![Edit Json file](doc/7.png)

See the results:

![See the results](doc/8.png)

Download statistics in Excel form:

![Excel statistics](doc/9.png)

## Configuration

1. Create quizzes using Json with the format in [example](doc/quiz_example.json)

2. Put quiz configuration files in `data/quizs`, for example:

```
./data/quizs/
├── quizU1.json
└── quizU2.json
```

3. Create folders in `data/students` to represent different classes, for example:

```
./data/students/
├── Commerce
├── Design
├── Science1
├── Science2
└── admin
```
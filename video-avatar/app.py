from flask import Flask, render_template, request, jsonify, url_for, redirect, session
from model import load_model, get_response 
from flask_cors import CORS  
import os
import json
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "GOOGLE_API_KEY")
CORS(app)
CORS(app, origins=["http://127.0.0.1:5000"])
model = None  

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() 
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    role = request.form.get('role')
    session['role'] = role
    if role == 'instructor':
        return redirect('/instructor')
    else:
        return redirect('/student')

@app.route('/instructor')
def instructor():
    return render_template('instructor.html')

@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/chapters')
def add_subject():
    return render_template('chapters.html')

@app.route('/chapter_view')
def chapter_view():
    return render_template('chapter_view.html')

@app.route('/avatar', methods=['GET', 'POST']) 
def coursePage(): 
    subject = request.args.get('subject', 'Unknown')
    chapter = request.args.get('chapter', 'Unknown')
    role = session.get('role', None)
    global model 

    if request.method == 'GET':
        model = load_model(data[subject]['chapters'][chapter]['notes']) 
        return render_template('avatar.html', role=role, chapter=chapter)

    elif request.method == 'POST':
        x = request.json  
        question = x.get("question", "")
        if model:
            response = get_response(model, question)
        else:
            response = "Model not initialized yet. Please select a course."
        return jsonify({"answer": response})

@app.route('/studentChapters', methods=['GET'])
def studentChapters():
    return render_template('studentChapters.html')


@app.route('/ask', methods=['POST'])
def solution():
    try:
        data = request 

        question = data.json.get("query", "")
        if model:
            result = get_response(model, question)
        else:
            result = "Model is not available. Please load a course first."
        
        return jsonify({"answer": result})
    
    except Exception as e:
        print(f"Error herere: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500
    
@app.route('/subjects', methods=['GET', 'POST'])
def subjects():
    if request.method == 'GET':
        subject = []
        for key in data.keys():
            subject.append({'name': key, 'description': data[key]['description']})
        return jsonify(subject)
    elif request.method == 'POST':
        x = request.json
        data[x['name']]={
            'description': x['description'],
            'chapters': {}
        }
        print(data)
        with open('data.json', 'w') as file:
            json.dump(data, file, indent=4)
        
        return jsonify({})

@app.route('/getChapters', methods=['GET', 'POST'])
def getChapters():
    if request.method == 'GET':
        subject_name = request.args.get('subject')
        chapters=[]
        for chapter in list(data[subject_name]['chapters'].keys()):
            chapters.append({'name': chapter, 'description': data[subject_name]['chapters'][chapter]['description']})
        return jsonify(chapters)
    elif request.method == 'POST':
        x = request.json
        data[x['subject']]['chapters'][x['chapterData']['name']] = {
            'description': x['chapterData']['description'],
            'notes': x['chapterData']['notes']
        }
        with open('data.json', 'w') as file:
            json.dump(data, file, indent=4)
        
        return jsonify({})



@app.route('/displayNotes', methods=['GET'])
def display():
    subject = request.args.get('subject', 'Unknown')
    chapter = request.args.get('chapter', 'Unknown')

    desc = data[subject]['description']
    notes = data[subject]['chapters'][chapter]['notes']
    return render_template('notesView.html', desc = desc, notes = notes, chapter = chapter)


if __name__ == '__main__':

    with open('data.json') as file:
        data = json.load(file)
    
    subject = []
    for key in data.keys():
        subject.append({'name': key, 'description': data[key]['description']})
    
    app.run()

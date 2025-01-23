from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import logging
from src.common import calculate_score

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.logger.setLevel(logging.INFO)

# Configuration
ARTIFACTS_FOLDER = "artifacts"
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm'}
os.makedirs(ARTIFACTS_FOLDER, exist_ok=True)

# Q&A Database
qa_map = {
    "What is Python programming?": "Python is a high-level, interpreted programming language known for its simplicity and readability. It supports multiple programming paradigms, including procedural, object-oriented, and functional programming.",
    "What are data types in Python?": "Data types in Python define the type of data a variable can hold. Common data types include int, float, str, list, tuple, dict, and set.",
    "What is the Pandas library used for?": "Pandas is a Python library used for data manipulation and analysis. It provides data structures like Series and DataFrame for handling structured data efficiently.",
    "What is a DataFrame in Pandas?": "A DataFrame is a 2-dimensional, tabular data structure in Pandas, similar to a spreadsheet or SQL table. It consists of rows and columns, allowing easy data manipulation and analysis.",
    "How do you create a DataFrame in Pandas?": "You can create a DataFrame using the pandas.DataFrame() function by passing data in the form of lists, dictionaries, or NumPy arrays. Example: `import pandas as pd; df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})`."
}

# Global Variables
data_store = []
current_question_index = 0
questions = list(qa_map.keys())
candidate_info = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')
# Initialize candidate_info
candidate_info = {}

@app.route('/start', methods=['POST'])
def start_test():
    global candidate_info
    try:
        # Collect candidate information from the request
        candidate_name = request.form.get('name')
        candidate_email = request.form.get('email')

        if not candidate_name or not candidate_email:
            return jsonify({'error': 'Candidate name and email are required'}), 400

        # Create candidate-specific folder
        candidate_folder = os.path.join(ARTIFACTS_FOLDER, secure_filename(candidate_name))
        os.makedirs(candidate_folder, exist_ok=True)

        # Save candidate info to a text file
        candidate_info_file = os.path.join(candidate_folder, f"{secure_filename(candidate_name)}.txt")
        with open(candidate_info_file, 'w') as f:
            f.write(f"Name: {candidate_name}\n")
            f.write(f"Email: {candidate_email}\n")

        # Create folder for uploaded audio
        uploaded_audio_folder = os.path.join(candidate_folder, "uploaded_audio")
        os.makedirs(uploaded_audio_folder, exist_ok=True)

        # Initialize candidate state
        candidate_info = {
            'name': candidate_name,
            'email': candidate_email,
            'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'folder': candidate_folder,
            'current_question_index': 0  # Start at the first question
        }

        app.logger.info(f"Test started for candidate: {candidate_info}")

        return jsonify({'message': 'Test started successfully', 'candidate_info': candidate_info})

    except Exception as e:
        app.logger.error(f"Error in start_test: {str(e)}")
        return jsonify({'error': 'Server error occurred'}), 500

@app.route('/next', methods=['GET', 'POST'])
def next_question():
    try:
        # Ensure candidate_info is populated
        if not candidate_info or 'folder' not in candidate_info:
            app.logger.error("Candidate information is missing or incomplete.")
            return jsonify({'error': 'Candidate information is missing or incomplete.'}), 400

        # Fetch the candidate's current question index
        current_question_index = candidate_info.get('current_question_index', 0)

        candidate_audio_folder = os.path.join(candidate_info['folder'], "uploaded_audio")
        os.makedirs(candidate_audio_folder, exist_ok=True)

        if request.method == 'POST':
            # Check if the recording is provided
            if 'recording' not in request.files:
                return jsonify({'error': 'No recording file provided'}), 400

            recording = request.files['recording']

            # Validate the file type
            if recording and allowed_file(recording.filename):
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{current_question_index + 1}.wav"  # Renaming the file
                filepath = os.path.join(candidate_audio_folder, filename)
                recording.save(filepath)

                # Store the recording data
                data_store.append({
                    "question": questions[current_question_index],
                    "recording": filename,
                    "timestamp": timestamp
                })

                # Move to the next question
                current_question_index += 1
                candidate_info['current_question_index'] = current_question_index  # Update index in state

                if current_question_index < len(questions):
                    return jsonify({
                        "question": questions[current_question_index],
                        "answer": ""
                    })
                else:
                    # All questions answered
                    return jsonify({
                        "question": None,
                        "lastRecordingStored": True
                    })
            else:
                return jsonify({'error': 'Invalid file type'}), 400

        # For GET requests, serve the next question
        if current_question_index < len(questions):
            return render_template('index.html', question=questions[current_question_index])
        else:
            app.logger.error("All questions have been completed.")
            return jsonify({'error': 'No more questions available.'}), 400

    except Exception as e:
        app.logger.error(f"Error in next_question: {str(e)}")
        return jsonify({'error': 'Server error occurred'}), 500
    
    
@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Check if we have the last recording in the request
        if 'final_recording' in request.files:
            recording = request.files['final_recording']
            if recording and allowed_file(recording.filename):
                filename = f"{len(questions)}.wav"  # Last question number
                candidate_audio_folder = os.path.join(candidate_info['folder'], "uploaded_audio")
                filepath = os.path.join(candidate_audio_folder, filename)
                recording.save(filepath)

                # Add the final recording to data_store if it's not already there
                last_question = questions[-1]
                if not any(d['question'] == last_question for d in data_store):
                    data_store.append({
                        "question": last_question,
                        "recording": filename,
                        "timestamp": datetime.now().strftime("%Y%m%d%H%M%S")
                    })

        candidate_audio_folder = os.path.join(candidate_info['folder'], "uploaded_audio")
        list_of_audio = [os.path.join(candidate_info['folder'], "uploaded_audio",f) for f in os.listdir(candidate_audio_folder) if os.path.isfile(os.path.join(candidate_audio_folder, f))]
        for audio_path in list_of_audio:
            index = int(audio_path.split(".")[0][-1])
            print(index)
        print(list_of_audio)
        result = calculate_score(list_of_audio=list_of_audio, qa_map=qa_map)

        print(f"result ---------- {result}")
        return jsonify({
            "message": f"Interview responses submitted successfully. {result}",
            "data": data_store,
            "candidate_info": candidate_info
        })

    except Exception as e:
        app.logger.error(f"Error in submit: {str(e)}")
        return jsonify({'error': 'Server error occurred'}), 500

@app.route('/recordings/<path:filename>')
def serve_recording(filename):
    candidate_audio_folder = os.path.join(candidate_info['folder'], "uploaded_audio")
    return send_from_directory(candidate_audio_folder, filename)




from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import logging
from src.common import calculate_score

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.logger.setLevel(logging.INFO)

# Configuration
RECORDING_FOLDER = "artifacts/uploaded_audio"
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm'}
os.makedirs(RECORDING_FOLDER, exist_ok=True)

# Q&A Database
qa_map = {
    "What is Python programming?": "Python is a high-level, interpreted programming language known for its simplicity and readability. It supports multiple programming paradigms, including procedural, object-oriented, and functional programming.",
    "What are data types in Python?": "Data types in Python define the type of data a variable can hold. Common data types include int, float, str, list, tuple, dict, and set.",
    "What is the Pandas library used for?": "Pandas is a Python library used for data manipulation and analysis. It provides data structures like Series and DataFrame for handling structured data efficiently.",
    "What is a DataFrame in Pandas?": "A DataFrame is a 2-dimensional, tabular data structure in Pandas, similar to a spreadsheet or SQL table. It consists of rows and columns, allowing easy data manipulation and analysis.",
    "How do you create a DataFrame in Pandas?": "You can create a DataFrame using the pandas.DataFrame() function by passing data in the form of lists, dictionaries, or NumPy arrays. Example: `import pandas as pd; df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})`."
}

data_store = []
current_question_index = 0
questions = list(qa_map.keys())

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    global current_question_index
    current_question_index = 0
    return render_template('index.html', 
                         question=questions[current_question_index], 
                         qa_data=qa_map[questions[current_question_index]])

@app.route('/next', methods=['POST'])
def next_question():
    global current_question_index
    
    try:
        if 'recording' not in request.files:
            return jsonify({'error': 'No recording file provided'}), 400
            
        recording = request.files['recording']
        
        if recording and allowed_file(recording.filename):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{current_question_index + 1}.wav"  # Renaming the file to match the question index
            filepath = os.path.join(RECORDING_FOLDER, filename)
            recording.save(filepath)
            
            # Store the current recording data
            data_store.append({
                "question": questions[current_question_index],
                "recording": filename,
                "timestamp": timestamp
            })
            
            current_question_index += 1
            
            if current_question_index < len(questions):
                return jsonify({
                    "question": questions[current_question_index],
                    "answer": qa_map[questions[current_question_index]]
                })
            else:
                # Return the last question's data along with completion status
                return jsonify({
                    "question": None,
                    "lastRecordingStored": True
                })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
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
                filepath = os.path.join(RECORDING_FOLDER, filename)
                recording.save(filepath)
                
                # Add the final recording to data_store if it's not already there
                last_question = questions[-1]
                if not any(d['question'] == last_question for d in data_store):
                    data_store.append({
                        "question": last_question,
                        "recording": filename,
                        "timestamp": datetime.now().strftime("%Y%m%d%H%M%S")
                    })
        
        directory_path = os.path.join("artifacts","uploaded_audio")
        list_of_audio = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

        result = calculate_score(list_of_audio=list_of_audio, qa_map=qa_map)

        print(f"result ---------- {result}")
        return jsonify({
            "message": f"Interview responses submitted successfully. {result}",
            "data": data_store
        })
        
    except Exception as e:
        app.logger.error(f"Error in submit: {str(e)}")
        return jsonify({'error': 'Server error occurred'}), 500

@app.route('/recordings/<path:filename>')
def serve_recording(filename):
    return send_from_directory(RECORDING_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
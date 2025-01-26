# AI Interview

This project is designed to conduct automated interviews utilizing speech recognition, machine learning models, and natural language processing techniques. The system allows for interviewee evaluation and prediction.

## Features

- **Speech Recognition**: Utilizes `SpeechRecognition` for interpreting the interviewee's spoken responses.
- **Machine Learning Models**: Implements models for predicting code clusters based on provided questions.
- **Interview Evaluation**: Assesses the accuracy of responses using fuzzy text matching and provides a recruitment prediction based on the interviewee's answers.
- **User Interface**: Utilizes `Streamlit` to provide an interactive and user-friendly web interface for interview sessions.

## Installation

Follow these steps to set up the project:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/atcsanchit/AI_interview.git
   ```

2. **Navigate to the project directory**:

   ```bash
   cd AI_interview
   ```

3. **Install FFmpeg**:

   Ensure that FFmpeg is installed on your system. You can install it using `pip`:

   ```bash
   pip install ffmpeg
   ```

4. **Install the required dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:

   Create a `.env` file in the project root directory and add the following variables:

   ```ini
   MISTRAL_API_KEY=your_mistral_api_key_here  # Get the API key from the Mistral official website
   PORT=3000
   ```

## Usage

To start the application, run the following command:

```bash
python wsgi.py
```

Once the application is running, open your web browser and navigate to the provided URL to begin the interview process.

## File Structure

- `wsgi.py`: The entry point for running the application.
- `requirements.txt`: Lists the Python dependencies required for the project.
- `.env`: Contains environment variables for configuration.
- Other files and directories contain the implementation of various components of the AI Interview system.

## Contributing

Contributions are welcome! Fork the repository, make changes, and create pull requests to enhance the system's functionality or address any issues.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


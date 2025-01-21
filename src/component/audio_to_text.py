import os
import sys
import whisper
import shutil
from dataclasses import dataclass

from src.logger import logging
from src.exception import CustomException

@dataclass
class AudioToTextConfig:
    def __init__(self):
        self.model_name = "base"
        # self.filepath = "artifacts\uploaded_audio\Me at the zoo.wav"

class AudioToText:
    def __init__(self):
        self.audio_to_text = AudioToTextConfig()

    def load_whisper_model(self):
        try:
            self.model = whisper.load_model(self.audio_to_text.model_name)
        except Exception as e:
            logging.info(f"Error in load_whisper_model -- {e}")
            raise CustomException(e,sys)
        

    def get_response(self, filepath):
        # if not shutil.which("ffmpeg"):
        #     # raise CustomException("FFmpeg is not installed or not in PATH.", sys)
        #     return "yaha phata"
        try:
            # filepath = r"C:\Users\USER\Documents\projects\AI interview\artifacts\uploaded_audio\Me at the zoo.wav"
            if os.path.exists(filepath):
                print("File found")
            result = self.model.transcribe(filepath)
            return result
        except Exception as e:
            raise CustomException(e, sys)
    
# if __name__ == "__main__":
#     audio_to_text = AudioToText()
#     audio_to_text.load_whisper_model()
#     config = AudioToTextConfig()
#     audio_to_text.get_response(filepath=config.filepath)
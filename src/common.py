import os
import sys
from src.component.audio_to_text import AudioToText
from src.component.prediction_mistral import PredictionMistral

from src.logger import logging
from src.exception import CustomException


def calculate_score(list_of_audio, qa_map):
    try:
        scores = []
        threshold = 40
        for audio_path in list_of_audio:
            index = int(audio_path.split(".")[0])
            if index > 5:
                 continue
            directory_path = os.path.join("artifacts","uploaded_audio")
            audio_to_text = AudioToText()
            audio_to_text.load_whisper_model()
            file_path = os.path.join(directory_path, audio_path)
            audio_output = audio_to_text.get_response(filepath=file_path)
            candidate_response = audio_output["text"]
            prediction = PredictionMistral()
            prediction.load_model()
            
            score_ = prediction.predict_score(answer=qa_map[list(qa_map.keys())[index-1]], text=candidate_response)
            scores.append(int(score_))


        print(scores)
        if sum(scores) < threshold:
            return "Sorry but you are not selected"
        else:
            return "Congratulations you are selected"




    except Exception as e:
            logging.info(f"Error in calculate_score -- {e}")
            raise CustomException(e,sys)
    
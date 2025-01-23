import os
import sys
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import AIMessage
from dotenv import load_dotenv
from dataclasses import dataclass

from src.logger import logging
from src.exception import CustomException

@dataclass
class PredictionMistralConfig:
    model="mistral-large-latest"
    # vector_db_path = os.path.join("artifacts","prepare_vector_db")
    temprature = 0.2
    # embedding_model_name = "BAAI/bge-base-en"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": True}

class PredictionMistral:
    def __init__(self):
        self.prediction_config = PredictionMistralConfig()

    def load_model(self):
        try:
            load_dotenv()
            api_key = os.getenv("MISTRAL_API_KEY")
            os.environ["MISTRAL_API_KEY"] = api_key
            self.llm = ChatMistralAI(model=self.prediction_config.model,
                                     temprature = self.prediction_config.temprature,
                                     max_retries = 2)
            print("*"*100)
            print("model load successfully")
        except Exception as e:
            logging.info(f"Error in load_model -- {e}")
            raise CustomException(e,sys)
    
    def predict_score(self, answer, text):
        try:
            messages = [
    (
        "system",
        "You are a helpful assistant that compares the answer of the candidate with the correct answer and, based on that, gives a score between 0 to 10. Make sure to only give the score and nothing else.",
    ),
    ("human", f"What is your score for my answer: '{text}' compared to the correct answer: '{answer}'"),
]       
            ai_msg = self.llm.invoke(messages)
            # ai_message = AIMessage(ai_msg)
            print(ai_msg.content)
            return int(ai_msg.content)
        
        except Exception as e:
            logging.info(f"Error in predict_score -- {e}")
            raise CustomException(e,sys)
        

# if __name__ == "__main__":
#     prediction = PredictionMistral()
#     prediction.load_model()
#     prediction.predict_score(answer="xuzC++ is a programming language used to create software. It's an object-oriented language that gives programmers more control over memory and system resources. C++ is often used to create large-scale applications, such as operating systems, video games, and databases.",text=" This was the fastest programming language. One of the fastest is it is an oops based programming language and it is basically used to develop very fast systems such as data bases, operating systems, games.")
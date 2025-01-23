from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
# import python-multipart
import os
from pathlib import Path
from src.component.audio_to_text import AudioToText
import os
# from main import process_image

app = FastAPI()


@app.get("/")
async def xyz():
    return {"hard coding is good":"but not cool!"}

@app.post("/submit")
async def abc(file: UploadFile = File(...)):

    save_dir = Path("artifacts/uploaded_audio")
    save_dir.mkdir(parents=True, exist_ok=True)

    file_path = os.path.join(save_dir, file.filename)
    print(file_path)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    # output = process_image(str(file_path))
    audio_to_text = AudioToText()
    audio_to_text.load_whisper_model()
    output = audio_to_text.get_response(filepath=file_path)
    return {"result": output["text"]}

@app.get("/test")
async def random(name:str):
    return {"this is cool ":f"{name}"}
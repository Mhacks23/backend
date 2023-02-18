from fastapi import FastAPI
import uvicorn
import motor.motor_asyncio
from utilities import get_transcription,get_chunks,get_summary
from models import *

app = FastAPI()

MONGO_DETAILS = "mongodb+srv://admin:12345@cluster0.crod9kz.mongodb.net/?retryWrites=true&w=majority"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.hackathon
Transcriptions = database.get_collection("Transcriptions")


@app.get('/')
def index():
  return {'message':"Hello World"}


@app.post('/get_transcription')
async def create_notes(transcript: TranscriptionModel ):
    
    video_url = transcript.video_url
    user_id = str(transcript.user_id)
    chapter_name = str(transcript.chapter_name)
    subject_name = str(transcript.subject_name)


    transcription,title = get_transcription(video_url)
    chunks = get_chunks(transcription['text'])
    print(type(transcription['text']))

    summarries = []

    for para in chunks:
        summary = get_summary(para)
        summarries.append(summary)    
    obj = {'title':str(title),'chunks':str(chunks),'summary': str(summarries), 'user_id': user_id, 'chapter_name': chapter_name, 'video_url': video_url }
    
    await Transcriptions.insert_one(obj)
    obj['_id'] = str(obj['_id']) 
    return obj

@app.post("/ocr_to_notes")
async def ocr_to_notes(data: OCRToNotesModel):
    
    print(data)
    user_id = str(data.user_id)
    chapter_name = str(data.chapter_name)
    subject_name = str(data.subject_name)
    text = str(data.text)

    chunks = get_chunks(text)
    summarries = []

    for para in chunks:
        summary = get_summary(para)
        summarries.append(summary)    
    obj = {'chunks':str(chunks),'summary': str(summarries), 'user_id': user_id, 'chapter_name': chapter_name }
    
    await Transcriptions.insert_one(obj)
    obj['_id'] = str(obj['_id']) 
    return obj
    
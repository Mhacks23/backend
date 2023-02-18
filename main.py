from fastapi import FastAPI
import motor.motor_asyncio
from utilities import get_transcription,get_chunks,get_summary
from models import *

app = FastAPI()

MONGO_DETAILS = "mongodb://localhost:27017"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.hackathon
Transcriptions = database.get_collection("Transcriptions")


@app.get('/')
def index():
  return {'message':"Hello World"}


@app.post('/create_notes')
async def create_notes(transcript: TranscriptionModel ):
    
    print("data: ", transcript)
    video_url = transcript.video_url
    user_id = str(transcript.user_id)
    chapter_name = str(transcript.chapter_name)
    subject_name = str(transcript.subject_name)


    transcription,title = get_transcription(video_url)
    chunks = get_chunks(transcription['text'])

    summarries = []

    for para in chunks:
        summary = get_summary(para)
        summarries.append(summary)    
    obj = {'title':str(title),'chunks':str(chunks),'summary': str(summarries), 'user_id': user_id, 'chapter_name': chapter_name, 'video_url': video_url }
    Transcriptions.insert_one(obj)
    obj['_id'] = str(obj['_id']) 
    return obj